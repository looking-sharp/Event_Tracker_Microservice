import requests
from datetime import datetime, timezone

from datetime import datetime, timezone

payload = {
  "event_id": "evt_12345",
  "event_name": "Weekly Standup Meeting",
  "event_date": datetime.now(timezone.utc).isoformat(),
  "fields": [
    {
      "field_id": "fld_1",
      "field_type": "text",
      "field_name": "full_name",
      "label": "Full Name",
      "required": True
    },
    {
      "field_id": "fld_2",
      "field_type": "email",
      "field_name": "email",
      "label": "Email Address",
      "required": True
    },
    {
      "field_id": "fld_3",
      "field_type": "password",
      "field_name": "password",
      "label": "Password",
      "required": True
    },
    {
      "field_id": "fld_4",
      "field_type": "number",
      "field_name": "age",
      "label": "Age",
      "required": False
    },
    {
      "field_id": "fld_5",
      "field_type": "tel",
      "field_name": "phone",
      "label": "Phone Number",
      "required": False
    },
    {
      "field_id": "fld_6",
      "field_type": "url",
      "field_name": "website",
      "label": "Personal Website",
      "required": False
    },
    {
      "field_id": "fld_7",
      "field_type": "date",
      "field_name": "birthdate",
      "label": "Birth Date",
      "required": False
    },
    {
      "field_id": "fld_8",
      "field_type": "time",
      "field_name": "meeting_time",
      "label": "Preferred Meeting Time",
      "required": False
    },
    {
      "field_id": "fld_9",
      "field_type": "datetime-local",
      "field_name": "appointment",
      "label": "Set Appointment",
      "required": False
    },
    {
      "field_id": "fld_10",
      "field_type": "color",
      "field_name": "fav_color",
      "label": "Favorite Color",
      "required": False
    },
    {
      "field_id": "fld_11",
      "field_type": "range",
      "field_name": "satisfaction",
      "label": "Satisfaction (0-100)",
      "required": False
    },
    {
      "field_id": "fld_12",
      "field_type": "textarea",
      "field_name": "comments",
      "label": "Additional Comments",
      "required": False
    },
    {
      "field_id": "fld_13",
      "field_type": "checkbox",
      "field_name": "is_full_time",
      "label": "Are you a full-time employee?",
      "required": False
    },
    {
      "field_id": "fld_14",
      "field_type": "radio",
      "field_name": "attendance_type",
      "label": "Attendance Type",
      "options": ["In Person", "Remote", "Hybrid"],
      "required": True
    },
    {
      "field_id": "fld_15",
      "field_type": "select",
      "field_name": "department",
      "label": "Department",
      "options": ["Engineering", "Sales", "Marketing", "HR", "Finance"],
      "required": True
    },
    {
      "field_id": "fld_16",
      "field_type": "file",
      "field_name": "resume",
      "label": "Upload Resume (PDF Only)",
      "required": False
    },
    {
      "field_id": "fld_17",
      "field_type": "hidden",
      "field_name": "internal_code",
      "label": "Internal Code",
      "value": "ABC123",
      "required": False
    }
  ]
}

payload2 = {
  "event_id": "evt_12346",
  "event_name": "TEST SUBMIT",
  "event_date": datetime.now(timezone.utc).isoformat(),
  "fields": [
    {
      "field_id": "fld_1",
      "field_type": "text",
      "field_name": "full_name",
      "label": "Full Name",
      "required": True
    },
    {
      "field_id": "fld_2",
      "field_type": "email",
      "field_name": "email",
      "label": "Email",
      "required": False
    },
    {
      "field_id": "fld_3",
      "field_type": "radio",
      "field_name": "radio_test",
      "label": "Radio Test",
      "required": False
    },
    {
      "field_id": "fld_14",
      "field_type": "radio",
      "field_name": "attendance_type",
      "label": "Attendance Type",
      "options": ["In Person", "Remote", "Hybrid"],
      "required": True
    },
    {
      "field_id": "fld_15",
      "field_type": "select",
      "field_name": "department",
      "label": "Department",
      "options": ["Engineering", "Sales", "Marketing", "HR", "Finance"],
      "required": True
    },
    {
      "field_id": "fld_17",
      "field_type": "checkbox",
      "field_name": "food_items",
      "label": "Food Items:",
      "options": ["Chicken", "Donuts", "Beans", "Cake", "Cupcakes"],
      "required": False
    }]
}

#simple test form
#IVDHmDejVumY
#WL8egqR9W0hS
#Hp6CjXoGdXbS
#WKISjKSN6Ot3
#n4fe-afedG7S  c6e396c0-ad5b-438d-a1d8-8deca0ef376f

#Extensive Form
#WwVrs2qZIkTm  df6bb57d-ccb3-4477-8c14-25d53cdc61a1
response = requests.post("http://localhost:5003/create-check-in-form", json=payload2)
print(response)
print(response.json())