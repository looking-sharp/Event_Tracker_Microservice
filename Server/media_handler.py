from dotenv import load_dotenv 
from flask import jsonify, make_response
import requests
import os

load_dotenv()
MEDIA_URL = os.getenv("MEDIA_MICROSERVICE_URL")

def upload_file(file, old_id):
    if old_id is not None:
        response = requests.post(f"{MEDIA_URL}/delete/{old_id}")

    files = {
        "file": (file.filename, file.stream, file.mimetype)
    }
    try:
        response = requests.post(f"{MEDIA_URL}/upload", files=files)
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
    