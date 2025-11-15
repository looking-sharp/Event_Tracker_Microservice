from dotenv import load_dotenv 
from flask import jsonify, make_response
import requests
import os

load_dotenv()
EMAIL_URL = os.getenv("EMAIL_MICROSERVICE_URL")

def _convert_to_html(body: str) -> str:
    bslash = '\n'
    return f"<p>{body.replace(bslash, '<br>')}</p>"

def send_email(recipients: list[str], subject_line: str, body: str, is_html: bool):
    with open("templates/signature.html", "r") as signature:
        signature_html = signature.read()
        payload = {
            "recipiants": recipients,
            "subject_line": subject_line,
            "body": f"""{body if is_html else _convert_to_html(body)}
                        <br>
                        {signature_html}""",
            "is_html": True
        }
    try:
        response = requests.post(f"{EMAIL_URL}/send-email", json=payload)
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

def contact_attendees(recipients: list[str], subject_line: str, event_name: str, body: str, is_html: bool):
    if not is_html:
        body = _convert_to_html(body)
        is_html = True
    related_to = f"<p><b>This message is related to {event_name}</b></p>"
    body = related_to + body
    return send_email(recipients, subject_line, body, is_html)