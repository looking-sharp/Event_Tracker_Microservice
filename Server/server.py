from dotenv import load_dotenv # type: ignore
from flask import Flask, request, redirect, url_for, render_template, jsonify # type: ignore
from flask.wrappers import Response as FlaskResponse
from datetime import datetime, time, date
from flask_cors import CORS
from database import init_db, get_db, add_to_db, event_id_exists
from models import EventLog
from sqlalchemy import select
from zoneinfo import ZoneInfo
import email_handler
import check_in_handler
import media_handler
import requests
import os
import json
import secrets

app = Flask(__name__)

load_dotenv()
EMAIL_URL = os.getenv("EMAIL_MICROSERVICE_URL")
USER_URL = os.getenv("USER_AUTH_MICROSERVICE_URL")
CHECK_URL = os.getenv("CHECK_IN_MICROSERVICE_URL")
MEDIA_URL = os.getenv("MEDIA_MICROSERVICE_URL")
REVIEW_URL = os.getenv("REVIEW_AND_FEEDBACK_MICROSERVICE_URL")

PUB_CHECK_URL = os.getenv("PUB_CHECK_URL")
PUB_MEDIA_URL = os.getenv("PUB_MEDIA_URL")
TOKEN = ""

"""

Helper Functions and Initilization

"""


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

def _get_user_validity() -> tuple:
    """ Function to check if the current user token is valid
        - Uses User Auth Mcroservice    
    
        Returns (bool):
            if the user's token is valid
    """
    if TOKEN == "":
        return False, None
    headers = { "Authorization": f"Bearer {TOKEN}" }
    response = requests.get(f"{USER_URL}/auth/verify", headers=headers)
    if(response.status_code != 200):
        return False, None
    return True, response.json()

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
    """ Function to turn an event into a serializable object
        so that it can be passed to HTML files
    """
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
        "attendence_restriction": event.attendence_restriction,
        "cover_photo_url_id": event.cover_photo_url_id
    }

def _parse_response_data(response) -> tuple:
    """ Helper function to catch possible errors on recieving
        HTTP data
    """
    status = None
    message = "No message returned"
    
    if isinstance(response, requests.Response):
        status = response.status_code
        try:
            data = response.json()
            message = data.get("message", message)
        except Exception:
            message = response.text or message
    elif isinstance(response, FlaskResponse):
        status = response.status_code
        try:
            data = json.loads(response.get_data(as_text=True))
            message = data.get("message", message)
        except Exception:
            message = response.get_data(as_text=True) or message
    return status, message

def delete_event_logic(event_id, user_id):
    """ Helper function to delete an event from the database
        - Uses Email Microservice
        - Uses Event Check In Microservice
    """
    try:
        with get_db() as db:
            event = db.query(EventLog).filter(EventLog.id == event_id,EventLog.user_id == user_id).first()
            if not event:
                return "event not found", 400
            responders = [r["email"] for r in event.rsvps]
            if responders:
                email_handler.send_cancel_email(recipients=responders, event=_serialize_event(event))
            print(f"deleting event: {event.id} - {event.event_name}")
            requests.post(f'{CHECK_URL}/delete-form?formID="{event.check_in_token}"')
            db.delete(event)
            db.commit()
            return "event deleted", 200
    except Exception as e:
        print("ERROR:" + str(e))
        return "deletion failed", 400

"""

Backend Helper routes and User Creation / Login

"""


@app.route("/", methods=["GET", "POST"])
def index():
    """ Home page """
    return render_template("index.html")

@app.route("/check-microservices", methods=["GET"])
def checkMicroservices():
    returned = {}
    urls = [EMAIL_URL, USER_URL, CHECK_URL, MEDIA_URL, REVIEW_URL]
    names = ["email microservice", "user auth microservice", "event check in microservice", "media management microservice", "review and feedback microservice"]
    for i in range(len(urls)):
        if urls[i]:
            try:
                response = requests.get(f"{urls[i]}/health")
                returned[names[i]] = response.json().get("message")
                if returned[names[i]] is None:
                    returned[names[i]] = response.json().get("status")
            except Exception as e:
                returned[names[i]] = "NOT ACTIVE"
        else:
            returned[names[i]] = "NOT DEFINED IN ENV" 
    return jsonify(returned), 200

@app.route("/signUp", methods=["GET", "POST"])
def sign_up():
    """ Page so the user can sign up. 
        - Uses User Auth Mcroservice
        - Uses Email Microservice
    """
    global TOKEN
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        payload = { "name": name, "password": password, "email": email }

        response = requests.post(f"{USER_URL}/auth/register", json=payload)
        if(response.status_code == 201):
            email_handler.send_welcome_email(email)

            payload2 = { "email": email, "password": password}
            response = requests.post(f"{USER_URL}/auth/login", json=payload2)
            data = response.json()
            TOKEN = data.get("token")
            return redirect(url_for("user_page", user_id=data.get("short_token")))
        
        return response.json()
    
    return render_template("signUp.html")

@app.route("/check_email")
def check_email():
    """ Route to check if an email is already in use
        - Uses User Auth Microservice
    """
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"exists": False})

    response = requests.get(f"{USER_URL}/auth/exists", params={"email": email})
    data = response.json()
    
    exists = data.get("message") == "email taken"
    return jsonify({"exists": exists})

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Route for a user to log in to their account
        - Uses User Auth Microservice
    """
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
    """ Route for users to sign out
        - Uses User Auth Microservice
    """
    global TOKEN
    if TOKEN != "":
        headers = { "Authorization": f"Bearer {TOKEN}" }
        response = requests.post(f"{USER_URL}/auth/logout", headers=headers)
        print(response.json())
        TOKEN = ""
    return redirect(url_for("index"))

@app.route("/delete_account/<user_id>", methods=["POST"])
def delete_account(user_id):
    """ Route to delete a users account and
        recursively delete all their events
        - Uses User Auth Microservice
        - Uses Email Microservice
    """
    valid, data = _get_user_validity()
    if not valid:
        return redirect(url_for("index"))
    email = data["user"]["email"]

    email_handler.send_goodbye_email(email)
    with get_db() as db:
        events = db.query(EventLog).filter_by(user_id=user_id).all()
        for event in events:
            delete_event_logic(event.id, user_id)
        
        headers = { "Authorization": f"Bearer {TOKEN}" }
        response = requests.post(f"{USER_URL}/auth/delete-account", headers=headers)
        status, message = _parse_response_data(response)

        return render_template("resultInfo.html", Title="Deleted Account", Header="Delete Account Results", Status=status, Details=message, user_id=-1)

"""

User Dashboard Route

"""


@app.route("/userHome/<user_id>")
def user_page(user_id):
    """ Brings a user to their dashboard and makes sure all
        their events are loaded in
    """
    valid, data = _get_user_validity()
    if not valid:
        return redirect(url_for("index"))
    
    with get_db() as db:
        events = db.execute(
            select(EventLog).where(EventLog.user_id == user_id)
        ).scalars().all()
    
        # Format time for displaying
        for e in events:
            e.start_dt = datetime.combine(e.event_date, e.start_time).replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(e.tz_str))
            e.end_dt   = datetime.combine(e.event_date, e.end_time).replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(e.tz_str))
            e.home_page_url = f'{PUB_CHECK_URL}/get-check-in-front-page?formID="{e.check_in_token}"'
            e.check_in_submissions_url = f'{PUB_CHECK_URL}/check-submissions?formID="{e.check_in_token}"'
        
        return render_template(
            "userHome.html",
            username=data.get("user").get("name"),
            user_id=user_id,
            url=request.host_url,
            events=events,
            num_events=len(events)
        )


"""

Event Routes

"""

@app.route("/getEvent")
def get_event():
    """ Route to grab an event from database """
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

@app.route("/createEvent/<user_id>", methods=["GET", "POST"])
def create_event(user_id):
    """ Brings uses to the create event form is GET, and adds
        the event based on the form information if POST to db
    """
    valid, _ = _get_user_validity()
    if not valid:
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

        if 'cover_photo' in request.files:
            file = request.files['cover_photo']
            if file and file.filename:
                response = _parse_response_data(media_handler.upload_file(file, None))
                response_data = response.json()
                if "url_id" in response_data:
                    new_event.cover_photo_url_id = response_data["url_id"]
                    print(response_data["url_id"])

        # Save to DB
        with get_db() as db:
            add_to_db(db, new_event)

        # create default check in form
        check_in_handler.create_default_form(new_event.id)

        return redirect(url_for("user_page", user_id=user_id))

    # GET request
    return render_template("newEvent.html", user_id=user_id)

@app.route("/updateEvent/<user_id>/<event_id>", methods=["GET", "POST"])
def update_event(user_id, event_id):
    """ Brings uses to the update event form is GET, and updates
        the event based on the form information if POST to db
    """
    valid, _ = _get_user_validity()
    if not valid:
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
            
            if 'cover_photo' in request.files:
                file = request.files.get('cover_photo')
                if file and file.filename:
                    response = media_handler.upload_file(file, event.cover_photo_url_id)
                    response_data = response.json()
                    if "url_id" in response_data:
                        event.cover_photo_url_id = response_data["url_id"]
                        print(response_data["url_id"])

            # Commit changes
            db.commit()
        
        return redirect(url_for("user_page", user_id=user_id))

    # GET request: show prefilled form
    return render_template("updateEvent.html", user_id=user_id, event_id=event_id)

@app.route("/delete_event/<event_id>/<user_id>", methods=["POST"])
def delete_event(event_id, user_id):
    """ Route to delete an event """
    valid, _ = _get_user_validity()
    if not valid:
        return redirect(url_for("index"))
    message, status = delete_event_logic(event_id, user_id)
    return render_template("resultInfo.html", Title="Deleted Event", Header="Delete Event Results", Status=status, Details=message, user_id=user_id)


"""

RSVP Routes

"""


@app.route("/rsvp/<event_id>", methods=["GET", "POST"])
def rsvp(event_id):
    """ Route to bring users to an RSVP form for a spesific event
        if GET, and update the database with their information if POST
    """
    with get_db() as db:
        e = db.query(EventLog).filter_by(id=event_id).first()
        if not e:
            return render_template("resultInfo.html", Title="RSVP", Header="RSVP", Status=404, Details="Event not found", user_id=-1)
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
            return render_template("resultInfo.html", Title="RSVP", Header="RSVP", Status=200, Details="RSVP Successful", user_id=-1)
        cover_photo_link = None
        if e.cover_photo_url_id is not None:
            cover_photo_link = f"{PUB_MEDIA_URL}/access/{e.cover_photo_url_id}"
        return render_template("rsvpForm.html", event=e, cover_photo_link = cover_photo_link)


"""

Email Routes

"""


@app.route("/email", methods=["GET", "POST"])
def email_attendees():
    """ Route that bring users to an email form is GET
        and sends the email to listed recipients if post
        - Uses Email Microservice
    """
    valid, data = _get_user_validity()
    if not valid:
        return redirect(url_for("index"))
    user_id = request.args.get("uid")

    if request.method == "POST":
        # Get form data
        
        subject = request.form["subject"]
        body = request.form["body"]
        recipients = request.form.getlist("recipients")
        if request.form.get("includeYourself"):
            recipients.append(data["user"]["email"])
        else:
            print("No include found")

        with get_db() as db:
            event_id = request.args.get("eventid")
            event = db.query(EventLog).filter_by(id=event_id, user_id=user_id).first()
            if(event == None):
                print("Event not found")
                return redirect(url_for("index"))
        response = email_handler.contact_attendees(
            recipients=recipients, 
            subject_line=subject, 
            body=body, 
            is_html=True, 
            event=_serialize_event(event))
        status, message = _parse_response_data(response)
        return render_template("resultInfo.html", Title="Send Email", Header="Send Email Results", Status=status, Details=message, user_id=user_id)
    else:
        event_id = request.args.get("eventid")
        with get_db() as db:
            event = db.query(EventLog).filter_by(id=event_id, user_id=user_id).first()
            if(event == None):
                return redirect(url_for("index"))
            return render_template("emailAttendees.html", user_id=user_id, event_id=event_id, event=event)

@app.route("/email-submissions/<user_id>/<event_id>")
def email_submissions(user_id, event_id):
    """ Route to email the submissions from the check in form
        to the user's main email
        - Uses Email Microservice
        - Uses Event Check In Microservice
    """
    valid, data = _get_user_validity()
    if not valid:
        return redirect(url_for("index"))
    with get_db() as db:
        e = db.query(EventLog).filter_by(id=event_id).first()
        if not e:
            return render_template("resultInfo.html", Title="Email Submissions", Header="Emal Submissions", Status=404, Details="Event not found", user_id=user_id)
        url = f'{CHECK_URL}/check-submissions?formID="{e.check_in_token}"&asString=True'
        check_response = requests.get(url)
        email_results = email_handler.send_email([data["user"]["email"]], "Check In Submissions", check_response.json().get("html"), True)
        status, message = _parse_response_data(email_results)
        return render_template("resultInfo.html", Title="Send Email", Header="Send Email Results", Status=status, Details=message, user_id=user_id)


"""

Check In Routes

"""

@app.route("/create-check-in-form/<user_id>/<event_id>", methods=["GET", "POST"])
def create_form(user_id, event_id):
    """ Route to bring users to a create form form if GET, and take
        the fields to create a check in form if POST
        - Uses Event Check In Microservice
    """
    valid, _ = _get_user_validity()
    if not valid:
        return redirect(url_for("index"))
    with get_db() as db:
        e = db.query(EventLog).filter_by(id=event_id).first()
        if not e:
            return render_template("resultInfo.html", Title="Create Form", Header="Create Check In Form", Status=404, Details="Event not found", user_id=user_id)
    if request.method == 'GET':
        return render_template("newForm.html", event_id=event_id, user_id=user_id)
    elif request.method == 'POST':
        fields = json.loads(request.form.get("fieldsOutput"))
        fields_list = fields.get("fields", [])

        response = check_in_handler.create_form(event_id=event_id, fields=fields_list)
        status, message = _parse_response_data(response)
        return render_template("resultInfo.html", Title="Send Email", Header="Send Email Results", Status=status, Details=message, user_id=user_id)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    init_db()
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
