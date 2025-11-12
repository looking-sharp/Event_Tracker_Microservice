from dotenv import load_dotenv # type: ignore
from flask import Flask, request, redirect, url_for, render_template, jsonify # type: ignore
from datetime import datetime, time, date
from flask_cors import CORS
from database import init_db, get_db, add_to_db, event_id_exists
from models import EventLog
from sqlalchemy import select
from zoneinfo import ZoneInfo
import requests
import os
import secrets

app = Flask(__name__)

load_dotenv()
EMAIL_URL = os.getenv("EMAIL_MICROSERVICE_URL")
USER_URL = os.getenv("USER_AUTH_MICROSERVICE_URL")
TOKEN = ""

def create_event_id(length: int = 12) -> str:
    """Create short for URL"""
    return secrets.token_urlsafe(length)[:length]

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5000").split(",")
CORS(app, resources={
    r"/*": {
        "origins": [o.strip() for o in allowed_origins if o.strip()],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

def _get_user_validity() -> bool:
    if TOKEN == "":
        return False
    headers = { "Authorization": f"Bearer {TOKEN}" }
    response = requests.get(f"{USER_URL}/auth/verify", headers=headers)
    if(response.status_code != 200):
        return False
    return True

def _parse_date(date_str: str) -> datetime.date:
    """Convert 'YYYY-MM-DD' string to date object."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def _convert_to_utc(event_date_str, time_str, tz_str):
    """
    Convert date + time string + timezone to UTC time object
    """
    event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
    hour, minute = map(int, time_str.split(":"))
    local_dt = datetime.combine(event_date, time(hour, minute))
    local_dt = local_dt.replace(tzinfo=ZoneInfo(tz_str))
    utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
    return utc_dt.time()

def _serialize_event(event):
    # Convert times from UTC to the event's timezone
    tz = ZoneInfo(event.tz_str) if event.tz_str else None

    def convert_time(t: time):
        if not t or not tz:
            return t.isoformat() if t else None
        # Combine with event_date to get a datetime for conversion
        dt_utc = datetime.combine(event.event_date, t, tzinfo=ZoneInfo("UTC"))
        dt_local = dt_utc.astimezone(tz)
        return dt_local.time().isoformat(timespec="seconds")  # "HH:MM:SS"

    return {
        "id": event.id,
        "user_id": event.user_id,
        "event_name": event.event_name,
        "event_date": event.event_date.isoformat(),
        "start_time": convert_time(event.start_time),
        "end_time": convert_time(event.end_time),
        "tz_str": event.tz_str,
        "public": event.public,
        "event_location": event.event_location,
        "event_description": event.event_description,
        "age_restriction": event.age_restriction,
        "attendence_restriction": event.attendence_restriction
    }

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/signUp", methods=["GET", "POST"])
def sign_up():
    global TOKEN
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        payload = { "name": name, "password": password, "email": email }

        response = requests.post(f"{USER_URL}/auth/register", json=payload)
        if(response.status_code == 201):
            payload2 = { "email": email, "password": password}
            response = requests.post(f"{USER_URL}/auth/login", json=payload2)
            data = response.json()
            TOKEN = data.get("token")
            return redirect(url_for("user_page", user_id=data.get("short_token")))
        
        return response.json()
    
    return render_template("signUp.html")

@app.route("/check_email")
def check_email():
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"exists": False})

    response = requests.get(f"{USER_URL}/auth/exists", params={"email": email})
    data = response.json()
    
    exists = data.get("message") == "email taken"
    return jsonify({"exists": exists})

@app.route("/login", methods=["GET", "POST"])
def login():
    global TOKEN
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        payload = { "email": email, "password": password}
        response = requests.post(f"{USER_URL}/auth/login", json=payload)
        
        data = response.json()
        TOKEN = data.get("token")
        
        return redirect(url_for("user_page", user_id=data.get("short_token")))
        
    return render_template("login.html")

@app.route("/signout")
def signout():
    global TOKEN
    if TOKEN != "":
        headers = { "Authorization": f"Bearer {TOKEN}" }
        response = requests.post(f"{USER_URL}/auth/logout", headers=headers)
        print(response.json())
        TOKEN = ""
    return redirect(url_for("index"))

@app.route("/userHome/<user_id>")
def user_page(user_id):
    if TOKEN == "":
        return redirect(url_for("index"))
    headers = { "Authorization": f"Bearer {TOKEN}" }
    response = requests.get(f"{USER_URL}/auth/verify", headers=headers)
    
    if(response.status_code != 200):
        return redirect(url_for("login"))
    
    data = response.json();
    
    with get_db() as db:
        events = db.execute(
            select(EventLog).where(EventLog.user_id == user_id)
        ).scalars().all()
    
    # Format time for displaying
    for e in events:
        e.start_dt = datetime.combine(e.event_date, e.start_time).replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(e.tz_str))
        e.end_dt   = datetime.combine(e.event_date, e.end_time).replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(e.tz_str))
    
    return render_template(
        "userHome.html",
        username=data.get("user").get("name"),
        user_id=user_id,
        url=request.host_url,
        events=events,
        num_events=len(events)
    )

@app.route("/createEvent/<user_id>", methods=["GET", "POST"])
def create_event(user_id):
    if not _get_user_validity():
        return redirect(url_for("index"))

    if request.method == "POST":
        # Required fields
        _id = create_event_id(12)
        while event_id_exists(_id):
            _id= create_event_id(12)

        event_name = request.form["eventName"]
        event_date = _parse_date(request.form["eventDate"])
        event_location = request.form["location"]
        event_description = request.form["description"]
        tz_info = request.form["timezone"]

        # Optional fields
        public = bool(request.form.get('public'))
        age_restriction = request.form.get("age_restriction")
        attendance_restriction = request.form.get("attendence_restriction")

        # Create EventLog instance
        new_event = EventLog(
            id=_id,
            user_id=user_id,
            event_name=event_name,
            event_date=event_date,
            start_time = _convert_to_utc(request.form["eventDate"], request.form["startTime"], tz_info),
            end_time = _convert_to_utc(request.form["eventDate"], request.form["endTime"], tz_info),
            tz_str = tz_info,
            public=public,
            event_location=event_location,
            event_description=event_description,
            rsvps=[], 
            age_restriction=int(age_restriction) if age_restriction else None,
            attendence_restriction=attendance_restriction if attendance_restriction else None
        )

        # Save to DB
        with get_db() as db:
            add_to_db(db, new_event)

        return redirect(url_for("user_page", user_id=user_id))

    # GET request
    return render_template("newEvent.html", user_id=user_id)

def delete_event_logic(event_id, user_id):
    try:
        with get_db() as db:
            event = db.query(EventLog).filter(EventLog.id == event_id,EventLog.user_id == user_id).first()
            if not event:
                return "event not found", 400
            print(f"deleting event: {event.id} - {event.event_name}")
            db.delete(event)
            db.commit()
            return "event deleted", 200
    except Exception as e:
        return "deletion failed", 400

@app.route("/delete_event/<event_id>/<user_id>", methods=["POST"])
def delete_event(event_id, user_id):
    if not _get_user_validity():
        return redirect(url_for("index"))
    delete_event_logic(event_id, user_id)
    return redirect(url_for("user_page", user_id=user_id))

@app.route("/delete_account/<user_id>", methods=["POST"])
def delete_account(user_id):
    if not _get_user_validity():
        return redirect(url_for("index"))

    #email_handeler.send_account_delete_email(user["email"])
    with get_db() as db:
        events = db.query(EventLog).filter_by(user_id=user_id).all()
        for event in events:
            delete_event_logic(event.id, user_id)
        
        headers = { "Authorization": f"Bearer {TOKEN}" }
        response = requests.post(f"{USER_URL}/auth/delete-account", headers=headers)
        print(response.json())

        return redirect(url_for("sign_up"))

@app.route("/updateEvent/<user_id>/<event_id>", methods=["GET", "POST"])
def update_event(user_id, event_id):
    if not _get_user_validity():
        return redirect(url_for("index"))
    
    if request.method == "POST":
        # Required fields
        event_name = request.form["eventName"]
        event_date = _parse_date(request.form["eventDate"])
        event_location = request.form["location"]
        event_description = request.form["description"]
        tz_info = request.form["timezone"]

        # Optional fields
        public = bool(request.form.get('public'))
        age_restriction = request.form.get("age_restriction")
        attendance_restriction = request.form.get("attendence_restriction")

        with get_db() as db:
            # Find the event
            event = db.query(EventLog).filter(
                EventLog.id == event_id,
                EventLog.user_id == user_id
            ).first()
            
            if not event:
                return "event not found or not authorized", 400

            # Update fields
            event.event_name = event_name
            event.event_date = event_date
            event.start_time = _convert_to_utc(request.form["eventDate"], request.form["startTime"], tz_info)
            event.end_time = _convert_to_utc(request.form["eventDate"], request.form["endTime"], tz_info)
            event.tz_str = tz_info
            event.public = public
            event.event_location = event_location
            event.event_description = event_description
            event.age_restriction = int(age_restriction) if age_restriction else None
            event.attendence_restriction = attendance_restriction if attendance_restriction else None

            # Commit changes
            db.commit()
        
        return redirect(url_for("user_page", user_id=user_id))

    # GET request: show prefilled form
    return render_template("updateEvent.html", user_id=user_id, event_id=event_id)

@app.route("/getEvent")
def get_event():
    print("got request")
    event_id = request.args.get("event_id", "").strip()
    with get_db() as db:
        event = db.query(EventLog).filter(EventLog.id == event_id).first()
        if event:
            print("Found data")
            data = {
                "exists": True,
                "event": _serialize_event(event)
            }
            return jsonify(data)
        return jsonify({"exists":False, "event": None})    
    return jsonify({"exists":False, "event": None})

@app.route("/rsvp/<event_id>", methods=["GET", "POST"])
def rsvp(event_id):
    with get_db() as db:
        e = db.query(EventLog).filter_by(id=event_id).first()
        if not e:
            return "Event not found", 404
        e.start_dt = datetime.combine(e.event_date, e.start_time).replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(e.tz_str))
        e.end_dt   = datetime.combine(e.event_date, e.end_time).replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(e.tz_str))
        if request.method == "POST":
            email = request.form["email"]
            first_name = request.form["firstName"]
            last_name = request.form["lastName"]
            rsvp_entry = {
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
            }
            e.rsvps.append(rsvp_entry)
            db.commit()
            return "Thanks for RSVPing!"
        return render_template("rsvpForm.html", event=e)


@app.route("/email", methods=["GET", "POST"])
def email_attendees():
    if TOKEN == "":
        return redirect(url_for("index"))
    headers = { "Authorization": f"Bearer {TOKEN}" }
    response = requests.get(f"{USER_URL}/auth/verify", headers=headers)
    
    if(response.status_code != 200):
        return redirect(url_for("login"))
    
    data = response.json();
    
    user_id = request.args.get("uid")
    if request.method == "POST":
        # Get form data
        
        subject = request.form["subject"]
        body = request.form["body"]
        recipients = request.form.getlist("recipients")
        try:
            additional_email = request.form["includeYourself"]
            recipients.append(data.email)
        except Exception as e:
            print("include yourself not provided")
        finally:
            with get_db() as db:
                event_id = request.args.get("eventid")
                event = db.query(EventLog).filter_by(id=event_id, user_id=user_id).first()
                if(event == None):
                    return redirect(url_for("index"))
            print(event)
            # Implement send email here
        return "Email submitted!"
    else:
        event_id = request.args.get("eventid")
        with get_db() as db:
            event = db.query(EventLog).filter_by(id=event_id, user_id=user_id).first()
            if(event == None):
                return redirect(url_for("index"))
            return render_template("emailAttendees.html", user_id=user_id, event_id=event_id, event=event)



if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    init_db()
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
