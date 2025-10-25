const arrow_innerHTML = '<g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path fill-rule="evenodd" clip-rule="evenodd" d="M12.7071 14.7071C12.3166 15.0976 11.6834 15.0976 11.2929 14.7071L6.29289 9.70711C5.90237 9.31658 5.90237 8.68342 6.29289 8.29289C6.68342 7.90237 7.31658 7.90237 7.70711 8.29289L12 12.5858L16.2929 8.29289C16.6834 7.90237 17.3166 7.90237 17.7071 8.29289C18.0976 8.68342 18.0976 9.31658 17.7071 9.70711L12.7071 14.7071Z" fill="#000000"></path> </g></svg>';
const arrow = document.getElementById("dropdown_arrow");
const opt_div = document.getElementById("optional-questions");
let isActive = false;

document.addEventListener("DOMContentLoaded", () => {
    arrow.innerHTML = arrow_innerHTML;
});

arrow.addEventListener('click', () => {
    arrow.style.transform = isActive ? "rotate(0deg)" : "rotate(180deg)";
    isActive = !isActive;
    opt_div.style.display = isActive ? "block" : "none";
});