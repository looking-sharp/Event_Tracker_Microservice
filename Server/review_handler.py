from dotenv import load_dotenv 
from flask import jsonify, make_response
from database import get_db
from models import EventLog
import requests
import os

load_dotenv()
REVIEW_URL = os.getenv("REVIEW_AND_FEEDBACK_MICROSERVICE_URL")

def submit_review(name: str, rating: int, comment: str):
    payload = {
        "userId": name,
        "entityId": "event-tracker",
        "rating": rating,
        "comment": comment
    }
    
    try:
        response = requests.post(f"{REVIEW_URL}/feedback", json=payload)
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

def get_reviews(start: int, end: int, order="desc") -> list:
    payload = {
        "amount": end-start,
        "start": start,
        "order": order
    }
    
    try:
        response = requests.get(f"{REVIEW_URL}/get-feedback", params=payload)
        return response.json().get("results")
    except requests.exceptions.ConnectionError:
        status = 400
        details = "Email service is currently unavailable."
        return [details, status]
    except requests.exceptions.Timeout:
        status = 408
        details = "Request timed out."
        return [details, status]
    except requests.exceptions.RequestException as e:
        status = 500
        details = str(e)
        return [details, status]