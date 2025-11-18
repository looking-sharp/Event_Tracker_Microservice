document.querySelectorAll("td").forEach(td => {
  td.setAttribute("title", td.textContent);
});

const divs = document.getElementsByClassName("rsvp-table-div");

Array.from(divs).forEach(div => {
  if (!div.querySelector("table")) {
    div.style.overflowY = "hidden";
  }
});

function toggleDetails(id) {
  const details = document.getElementById(`checkin-${id}`);
  const arrow = document.getElementById(`arrow-${id}`);
  if (details.style.display === "grid") {
    details.style.display = "none";
    arrow.classList.remove("open");
  } else {
    details.style.display = "grid";
    arrow.classList.add("open");
  }
}