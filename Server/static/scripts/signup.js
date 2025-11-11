'use strict';

const emailInput = document.getElementById("email")
const usernameInput = document.getElementById("username");
const cPasswordInput = document.getElementById("c_password");
const passwordInput = document.getElementById("password");
const statusSpan = document.getElementById("username-status");
const passwordSpan = document.getElementById("password-status");
let typingTimer; // used for debounce
const debounceDelay = 100; // milliseconds

let usernameGood = false;
let passwordGood = false;
let display = false;

document.addEventListener("DOMContentLoaded", () => {
    checkPassword();
    checkEmail();
    display = true;
})

emailInput.addEventListener("input", () => {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(checkEmail, debounceDelay);
});

cPasswordInput.addEventListener("input", () => {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(checkPassword, debounceDelay);
});

function checkEmail() {
  const email = emailInput.value.trim();

  if (email == null || email.length == 0) {
    statusSpan.textContent = "";
    return;
  }
  
  fetch(`/check_email?email=${encodeURIComponent(email)}`)
    .then(response => response.json())
    .then(data => {
      if (data.exists && display) {
        statusSpan.textContent = "Email already taken";
        statusSpan.style.color = "red";
        usernameGood = false;
      } else if (display) {
        statusSpan.textContent = "Email available";
        statusSpan.style.color = "green";
        usernameGood = true;
      }
    })
    .catch(err => {
      if(display) {
        console.error("Error checking email:", err);
        statusSpan.textContent = "Error checking email";
        statusSpan.style.color = "orange";
        usernameGood = false;
      }
    });
}

function checkPassword() {
    const password = passwordInput.value.trim();
    const c_password= cPasswordInput.value.trim();
    if((password == null || password == "") || (c_password == null || c_password == "")) {
        passwordSpan.textContent= "";
        return;
    }
    if (password.length < 6 && display) {
      passwordSpan.innerHTML = "Passwords must be at least 6 chacters<br>"
      passwordSpan.style.color = "red";
      passwordGood = false;
      return;
    }
    if((password != c_password) && display) {
      passwordSpan.innerHTML = "Passwords must match<br>"
      passwordSpan.style.color = "red";
      passwordGood = false;
    }
    else if((password == c_password) && display) {
      passwordSpan.innerHTML = "Passwords matching<br>"
      passwordSpan.style.color = "green";
      passwordGood = true;
    }
}

function validateForm() {
    display = false;
    checkPassword();
    checkEmail();
    if(!passwordGood || !usernameGood)
    { 
        alert("Email or Password not valid");
        return false;
    }
    document.getElementById("signupForm").submit();
    return true;
}