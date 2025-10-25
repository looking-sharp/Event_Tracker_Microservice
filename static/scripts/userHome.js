document.querySelectorAll("td").forEach(td => {
  td.setAttribute("title", td.textContent);
});

const divs = document.getElementsByClassName("rsvp-table-div");

Array.from(divs).forEach(div => {
  if (!div.querySelector("table")) {
    div.style.overflowY = "hidden";
  }
});