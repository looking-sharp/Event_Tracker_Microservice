'use strict';

const form = document.getElementById("emailForm");
const selectAllBtn = document.getElementById('selectAll');
const unselectAllBtn = document.getElementById('unselectAll');
const checkboxes = document.querySelectorAll('input[name="recipients"]');
const search = document.getElementById("search")
const participants = document.querySelectorAll("#participantsList label");

form.addEventListener("submit", (e) => {
    document.getElementById("emailBody").value = quill.root.innerHTML;

    const checkedRecipients = Array.from(checkboxes).filter(cb => cb.checked);
    if (checkedRecipients.length === 0) {
        e.preventDefault();
        alert("Please select at least one recipient before sending the email.");
        return false;
    }

    const isEmpty = quill.getText().trim().length === 0;
    if(isEmpty) {
        e.preventDefault();
        alert("Email body cannot be empty.");
        return false;
    }
});

selectAllBtn.addEventListener('click', () => {
    checkboxes.forEach(cb => cb.checked = true);
});

unselectAllBtn.addEventListener('click', () => {
    checkboxes.forEach(cb => cb.checked = false);
});

search.addEventListener("input", () => {
  const query = search.value.toLowerCase();

  participants.forEach(label => {
    const text = label.textContent.toLowerCase();
    if (text.includes(query)) {
      label.style.display = "flex";  // show matching
    } else {
      label.style.display = "none";  // hide non-matching
    }
  });
});