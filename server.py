from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv # type: ignore
from flask import Flask, request, redirect, url_for, render_template, jsonify # type: ignore
from datetime import datetime
from encode import encode, decode
import uuid
import os

load_dotenv()
uri = os.getenv("DATABASE_URL")
client = MongoClient(uri)
db = client.event_tracker

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

app = Flask(__name__)

def format_time(time_str):
    return datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")

def getDecodedUserID(user_id):
    try:
        user_id = decode(user_id)
        return user_id
    except Exception as e:
        return -1

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/signUp", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_id = uuid.uuid4().hex[:8]
        # while unlikely, don't want more than one user to have same id
        while db.users.find_one({"_id":user_id}):
            user_id = uuid.uuid4().hex[:8]
        db.users.insert_one({
            "_id": user_id,
            "username": username,
            "password": password
        })
        return redirect(url_for("user_page", user_id=encode(user_id)))
    return render_template("signUp.html")

@app.route("/check_username")
def check_username():
    username = request.args.get("username", "").strip()
    if not username:
        return jsonify({"exists": False})

    exists = db.users.find_one({"username": username}) is not None
    return jsonify({"exists": exists})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = db.users.find_one({"username": username, "password":password})
        print(user)
        if user == None:
            return render_template("login.html", login_failed=True)
        return redirect(url_for("user_page", user_id=encode(user["_id"])))
    return render_template("login.html")

@app.route("/userHome/<user_id>")
def user_page(user_id):
    user_id = getDecodedUserID(user_id)
    if user_id == -1 :
        return redirect(url_for("login"))
    user = db.users.find_one({"_id":user_id})
    if user == None:
        # user needs to log in first
        return redirect(url_for("sign_up"))
    events = db.events.find({"user_id":user_id})
    num_events = db.events.count_documents({"user_id": user_id})
    return render_template("userHome.html", username=user["username"], user_id=encode(user_id), events=events, num_events=num_events, url=request.host_url)
    
@app.route("/createEvent/<user_id>", methods=["GET", "POST"])
def create_event(user_id):
    user_id = getDecodedUserID(user_id)
    if user_id == -1 :
        return redirect(url_for("login"))
    if request.method == "POST":
        event_name = request.form["eventName"]
        event_date = request.form["eventDate"]
        event_location = request.form["location"]
        event_description = request.form["description"]
        start_time = format_time(request.form["startTime"])
        end_time = format_time(request.form["endTime"])
        # Optional Info
        public = bool(request.form.get('public'))
        age_restriction = request.form["age_restriction"]
        attendence_restriction = request.form["attendence_restriction"]
        # id
        event_id = uuid.uuid4().hex[:8]
        while db.events.find_one({"_id":event_id}):
            event_id = uuid.uuid4().hex[:8]
        
        event_doc = {
            "_id": event_id,
            "user_id": user_id,
            "eventName": event_name,
            "eventDate": event_date,
            "startTime": start_time,
            "endTime": end_time,
            "public": public,
            "eventLocation": event_location,
            "eventDescription": event_description,
            "rsvps": []
        }

        if age_restriction:
            event_doc["age_restriction"] = age_restriction
        if attendence_restriction:
            event_doc["attendance_restriction"] = attendence_restriction

        # Insert into MongoDB
        db.events.insert_one(event_doc)

        return redirect(url_for("user_page", user_id=encode(user_id)))
    return render_template("newEvent.html", user_id=encode(user_id))

def delete_event_logic(event_id, user_id):
    result = db.events.delete_one({"_id": event_id, "user_id": user_id})
    if result.deleted_count == 0:
        return "Event not found or you don't have permission", 404
    return "Deleted", 200

@app.route("/delete_event/<event_id>/<user_id>", methods=["POST"])
def delete_event(event_id, user_id):
    user_id = getDecodedUserID(user_id)
    if user_id == -1 :
        return redirect(url_for("login"))
    delete_event_logic(event_id, user_id)
    return redirect(url_for("user_page", user_id=encode(user_id)))

@app.route("/updateEvent/<user_id>/<event_id>", methods=["GET", "POST"])
def update_event(user_id, event_id):
    user_id = getDecodedUserID(user_id)
    if user_id == -1 :
        return redirect(url_for("login"))
    # Get the event from DB first
    event = db.events.find_one({"_id": event_id, "user_id": user_id})
    if not event:
        return "Event not found or unauthorized", 404

    if request.method == "POST":
        event_name = request.form["eventName"]
        event_date = request.form["eventDate"]
        event_location = request.form["location"]
        event_description = request.form["description"]
        start_time = format_time(request.form["startTime"])
        end_time = format_time(request.form["endTime"])
        # Optional Info
        public = bool(request.form.get('public'))
        age_restriction = request.form["age_restriction"]
        attendence_restriction = request.form["attendence_restriction"]

        updated_fields = {
            "eventName": event_name,
            "eventDate": event_date,
            "eventLocation": event_location,
            "eventDescription": event_description,
            "startTime": start_time,
            "endTime": end_time,
            "public": public
        }

        if age_restriction:
            updated_fields["age_restriction"] = age_restriction
        else:
            db.events.update_one({"_id": event_id, "user_id": user_id}, {"$unset": {"age_restriction": ""}})
        
        if attendence_restriction:
            updated_fields["attendence_restriction"] = attendence_restriction
        else:
            db.events.update_one({"_id": event_id, "user_id": user_id}, {"$unset": {"attendence_restriction": ""}})

        db.events.update_one({"_id": event_id, "user_id": user_id}, {"$set": updated_fields})

        return redirect(url_for("user_page", user_id=encode(user_id)))

    # GET request: show prefilled form
    return render_template("updateEvent.html", user_id=encode(user_id), event_id=event["_id"])

@app.route("/getEvent")
def get_event():
    print("got request")
    event_id = request.args.get("event_id", "").strip()
    if db.events.find_one({"_id":event_id}):
        print("Found data")
        data = {
            "exists": True,
            "event": db.events.find_one({"_id":event_id})
        }
        return jsonify(data)
    return jsonify({"exists":False, "event": None})

if __name__ == "__main__":
    app.run(debug=True)
