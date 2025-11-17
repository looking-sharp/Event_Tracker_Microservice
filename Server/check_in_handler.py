from dotenv import load_dotenv 
from flask import jsonify, make_response
from database import get_db
from models import EventLog
import requests
import os

load_dotenv()
CHECK_IN_URL = os.getenv("CHECK_IN_MICROSERVICE_URL")
PUB_CHECK_URL = "http://localhost:5003"

"""
    Args:
        Request (JSON):
        {
            "event_id": "string",
            "event_name": "string",
            "event_date": "DateTime",
            fields = [
                {
                    "field_id": "string",
                    "field_type": "string",
                    "field_name": "string",
                    "label": "string",
                    "required": "boolean"
                },
                ...
            ]
        }
"""
def create_form(event_id: str, fields: dict):
    with get_db() as db:
        e = db.query(EventLog).filter_by(id=event_id).first()
        if not e:
            status = 408
            details = "Event ID is invalid."
            return make_response(jsonify({"message": details}), status)

        event_name = e.event_name
        event_date = e.event_date
        end_time = e.end_time
        
        payload = {
            "event_id": event_id,
            "event_name": event_name,
            "event_date": f"{event_date}T{end_time}",
            "fields": fields
        }
        try:
            response = requests.post(f"{CHECK_IN_URL}/create-check-in-form", json=payload)
            data = response.json()
            form_id = data.get("form_id")

            e.check_in_link = f'{PUB_CHECK_URL}/get-check-in-front-page?formID="{form_id}"'
            e.check_in_token = form_id
            db.commit()

            return response
        except requests.exceptions.ConnectionError:
            status = 400
            details = "Email service is currently unavailable."
            return make_response(jsonify({"message": details}), status)
        except requests.exceptions.Timeout:
            status = 408
            details = "Request timed out."
            return make_response(jsonify({"message": details}), status)
        except requests.exceptions.RequestException as e:
            status = 500
            details = str(e)
            return make_response(jsonify({"message": details}), status)
