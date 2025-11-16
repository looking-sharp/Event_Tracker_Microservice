import requests
from datetime import datetime, timezone

payload = {
  "event_id": "evt_12345",
  "event_name": "Weekly Standup Meeting",
  "event_date": datetime.now(timezone.utc).isoformat(),
  "fields": [
    {
      "field_id": "fld_1",
      "field_type": "text",
      "label": "Full Name",
      "required": True
    },
    {
      "field_id": "fld_2",
      "field_type": "email",
      "label": "Email Address",
      "required": True
    },
    {
      "field_id": "fld_3",
      "field_type": "checkbox",
      "label": "Employee?",
      "required": False
    }
  ]
}

#IkAYTL1mC9at
response = requests.post("http://localhost:5003/create-check-in-form", json=payload)
print(response)
print(response.json())