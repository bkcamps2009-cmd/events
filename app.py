import os
from uuid import UUID

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from postgrest import APIError
from supabase import Client, create_client

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__, static_folder=None)


@app.after_request
def add_frontend_cors(response):
    # Permit the optional standalone frontend dev server. The app itself uses
    # no cookies or other credentialed browser requests.
    response.headers.setdefault("Access-Control-Allow-Origin", "*")
    response.headers.setdefault("Access-Control-Allow-Headers", "Content-Type")
    response.headers.setdefault("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response


supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_PUBLISHABLE_KEY")
if not supabase_url or not supabase_key:
    raise RuntimeError("Set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in the environment")

supabase: Client = create_client(supabase_url, supabase_key)


def json_error(message, status):
    return jsonify({"error": message}), status


def is_uuid(value):
    try:
        UUID(str(value))
        return True
    except (ValueError, TypeError, AttributeError):
        return False


@app.errorhandler(APIError)
def handle_database_error(error):
    # Avoid returning database internals to API clients.
    app.logger.exception("Supabase request failed: %s", error)
    return json_error("Database request failed", 500)


@app.get("/")
def index():
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    return send_from_directory(frontend_dir, "index.html")


@app.get("/<path:filename>")
def frontend_asset(filename):
    if filename not in {"styles.css", "app.js"}:
        return json_error("Not found", 404)
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    return send_from_directory(frontend_dir, filename)


@app.get("/api")
def api_index():
    return jsonify({
        "service": "events-api",
        "endpoints": [
            "GET /api/events",
            "GET /api/events/<id>",
            "POST /api/registrations",
            "GET /api/me/registrations?user_id=<uuid>",
            "GET /api/events/<id>/registrations",
        ],
    })


@app.get("/api/events")
def list_events():
    response = supabase.table("events").select("*").execute()
    return jsonify(response.data)


@app.get("/api/events/<event_id>")
def get_event(event_id):
    if not is_uuid(event_id):
        return json_error("id must be a valid UUID", 400)

    response = (
        supabase.table("events")
        .select("*")
        .eq("id", event_id)
        .maybe_single()
        .execute()
    )
    if response.data is None:
        return json_error("Event not found", 404)
    return jsonify(response.data)


@app.post("/api/registrations")
def create_registration():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return json_error("Request body must be a JSON object", 400)

    user_id = payload.get("user_id")
    event_id = payload.get("event_id")
    if not is_uuid(user_id) or not is_uuid(event_id):
        return json_error("user_id and event_id must be valid UUIDs", 400)

    user = supabase.table("users").select("id").eq("id", user_id).maybe_single().execute()
    if user.data is None:
        return json_error("User not found", 404)

    event = supabase.table("events").select("id,capacity").eq("id", event_id).maybe_single().execute()
    if event.data is None:
        return json_error("Event not found", 404)

    existing = (
        supabase.table("registrations")
        .select("id")
        .eq("user_id", user_id)
        .eq("event_id", event_id)
        .maybe_single()
        .execute()
    )
    if existing.data is not None:
        return json_error("User is already registered for this event", 409)

    registrations = supabase.table("registrations").select("id", count="exact").eq("event_id", event_id).execute()
    capacity = event.data.get("capacity")
    if capacity is not None and registrations.count is not None and registrations.count >= capacity:
        return json_error("Event has reached capacity", 409)

    created = (
        supabase.table("registrations")
        .insert({"user_id": user_id, "event_id": event_id})
        .execute()
    )
    return jsonify(created.data[0]), 201


@app.get("/api/me/registrations")
def list_user_registrations():
    user_id = request.args.get("user_id")
    if not is_uuid(user_id):
        return json_error("user_id query parameter must be a valid UUID", 400)

    user = supabase.table("users").select("id").eq("id", user_id).maybe_single().execute()
    if user.data is None:
        return json_error("User not found", 404)

    response = (
        supabase.table("registrations")
        .select("*, events(*)")
        .eq("user_id", user_id)
        .execute()
    )
    return jsonify(response.data)


@app.get("/api/events/<event_id>/registrations")
def list_event_attendees(event_id):
    if not is_uuid(event_id):
        return json_error("id must be a valid UUID", 400)

    event = supabase.table("events").select("id").eq("id", event_id).maybe_single().execute()
    if event.data is None:
        return json_error("Event not found", 404)

    # Authentication is intentionally omitted, so this attendee list is public for now.
    response = (
        supabase.table("registrations")
        .select("*, users(id,email,role)")
        .eq("event_id", event_id)
        .execute()
    )
    return jsonify(response.data)


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
