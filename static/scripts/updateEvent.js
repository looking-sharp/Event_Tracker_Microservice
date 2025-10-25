'use strict';

const event_id = document.querySelector(".non-fixed").id;
const content = document.getElementById("content");
const loading = document.getElementById("loading");

function formatTimeForInput(timeStr) {
    // Example: "2:30 PM" -> "14:30"
    const [time, modifier] = timeStr.split(" "); // ["2:30", "PM"]
    let [hours, minutes] = time.split(":").map(Number);

    if (modifier === "PM" && hours < 12) hours += 12;
    if (modifier === "AM" && hours === 12) hours = 0;

    // pad with zero
    hours = hours.toString().padStart(2, "0");
    minutes = minutes.toString().padStart(2, "0");

    return `${hours}:${minutes}`;
}


document.addEventListener("DOMContentLoaded", () => {
    fetch(`/getEvent?event_id=${encodeURIComponent(event_id)}`)
        .then(response => response.json())
        .then(data => { 
            //console.log(data);
            document.getElementById("eventName").value = data.event.eventName;
            document.getElementById("eventDate").value = data.event.eventDate;
            document.getElementById("startTime").value = formatTimeForInput(data.event.startTime);
            document.getElementById("endTime").value = formatTimeForInput(data.event.endTime);
            document.getElementById("location").value = data.event.eventLocation;
            document.getElementById("description").value = data.event.eventDescription;

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