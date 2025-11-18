from dotenv import load_dotenv 
from flask import jsonify, make_response
import requests
import os

load_dotenv()
EMAIL_URL = os.getenv("EMAIL_MICROSERVICE_URL")

def _convert_to_html(body: str) -> str:
    """Converts a non-HTML string to HTML for emailing"""
    bslash = '\n'
    return f"<p>{body.replace(bslash, '<br>')}</p>"

def send_email(recipients: list[str], subject_line: str, body: str, is_html: bool):
    """ Main interaction with the email microservice, it 
        sends an email based on the above parameters and returns a json response
    """
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

def contact_attendees(recipients: list[str], subject_line: str, body: str, is_html: bool, event):
    """ Sends an email based on an event to selected attendees """
    if not is_html:
        body = _convert_to_html(body)
        is_html = True
    related_to = f"<p><b>This message is regarding: {event['event_name']} on {event['event_date']}</b></p>"
    body = related_to + body
    return send_email(recipients, subject_line, body, is_html)

def send_cancel_email(recipients: list[str], event):
    """ Sends a cancel email for respondants """
    subject_line = "An Event You RSVP'd for was Canceled"
    body = f"""
        <p><b>This message is regarding: {event['event_name']} on {event['event_date']}</b></p>
        <p>This is an automated email to inform you that an event you RSVP'd to was canceled. </p>
        <p>For any other questions, you can reach out to the event coordinator</p>
        <br>
    """
    return send_email(recipients, subject_line, body, True)

def send_welcome_email(recipient: str):
    """ Sends a welcome email to new users """
    subject_line = "Welcome to Event Tracker!"
    body = f"""
        <p><b>This message is regarding your Event Tracker account</b></p>
        <p>Your account has been successfully created. Welcome to Event Tracker! The easy to use platform for your event tracking needs</p>
        <ul>
            <li>Create, update, and track events</li>
            <li>Collect RSVP's</li>
            <li>Easily contact attendees</li>
        </ul>
        <p>Check out the Github Repo for this project: <a href='https://github.com/looking-sharp/Event_Tracker_Microservice'>Github</a></p>
    """
    return send_email([recipient], subject_line, body, True)

def send_goodbye_email(recipient: str):
    """ Sends a goodbye email to users who delete their accounts """
    subject_line = "Your Account has Been Deleted"
    body = f"""
        <p><b>This message is regarding your Event Tracker account</b></p>
        <p>Your account has been successfully deleted. Thank you for using my application</p>
        <p>- Thomas</p>
    """
    return send_email([recipient], subject_line, body, True)