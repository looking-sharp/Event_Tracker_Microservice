'use strict';

const event_id = document.querySelector(".non-fixed").id;
const content = document.getElementById("content");
const loading = document.getElementById("loading");

function formatTimeForInput(timeStr) {
    if (!timeStr) return "";
    return timeStr.slice(0,5); // take only HH:MM

}


document.addEventListener("DOMContentLoaded", () => {
    fetch(`/getEvent?event_id=${encodeURIComponent(event_id)}`)
        .then(response => response.json())
        .then(data => { 
            //console.log(data);
            document.getElementById("eventName").value = data.event.event_name;
            document.getElementById("eventDate").value = data.event.event_date;
            document.getElementById("startTime").value = formatTimeForInput(data.event.start_time);
            document.getElementById("endTime").value = formatTimeForInput(data.event.end_time);
            document.getElementById("location").value = data.event.event_location;
            document.getElementById("description").value = data.event.event_description;
            document.getElementById("timezone").value = data.event.tz_str;
            document.getElementById("public").checked = data.event.public;
            
            if(data.event.hasOwnProperty("age_restriction")) {
                document.getElementById("age_restriction").value = Number(data.event.age_restriction);
            }
            else {
                document.getElementById("age_restriction").value = null;
            }
            if(data.event.hasOwnProperty("attendence_restriction")) {
                document.getElementById("attendence_restriction").value = data.event.attendence_restriction;
            }
            setTimeout(() => {
                content.style.display = "block";
                loading.style.display = "none";
            }, 500);
        });
});