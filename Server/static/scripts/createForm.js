const labelInput = document.getElementById("labelInput");
const nameInput = document.getElementById("nameInput");
const typeInput = document.getElementById("typeInput");
const requiredInput = document.getElementById("requiredInput");

const optionsContainer = document.getElementById("optionsContainer");
const optionsInput = document.getElementById("optionsInput");

const addFieldBtn = document.getElementById("addFieldBtn");
const submitBtn = document.getElementById("submitBtn");

const fieldList = document.getElementById("fieldList");
const outputBox = document.getElementById("outputBox");

const previewForm = document.getElementById("previewForm");

let fields = [];
let idCounter = 1;

const allowed_field_types = [
  "text", "password", "email", "number", "tel", "url",
  "date", "time", "datetime", "datetime-local",
  "color", "range", "textarea",
  "checkbox", "radio", "select", "file"
];

typeInput.innerHTML = allowed_field_types
  .map(t => `<option value="${t}">${t}</option>`)
  .join("");

typeInput.addEventListener("change", () => {
  if (["radio", "checkbox", "select"].includes(typeInput.value)) {
    optionsContainer.style.display = "block";
  } else {
    optionsContainer.style.display = "none";
  }
});

addFieldBtn.addEventListener("click", () => {
  const label = labelInput.value.trim();
  const name = nameInput.value.trim();
  const type = typeInput.value;
  const required = requiredInput.checked;

  if (!label || !name) {
    alert("Label and field name are required.");
    return;
  }

  if (!allowed_field_types.includes(type)) {
    alert("Invalid field type.");
    return;
  }

  const field = {
    field_id: `fld_${idCounter++}`,
    field_type: type,
    field_name: name,
    label: label,
    required: required
  };

  if (["radio", "checkbox", "select"].includes(type)) {
    const options = optionsInput.value
      .split(",")
      .map(o => o.trim())
      .filter(o => o.length > 0);

    if (options.length != 0) {
      field.options = options;
    }
  }

  fields.push(field);
  renderFieldList();
  addField(field, previewForm);

  labelInput.value = "";
  nameInput.value = "";
  optionsInput.value = "";
  requiredInput.checked = false;
  
});

function renderFieldList() {
  fieldList.innerHTML = "";
  fields.forEach(f => {
    const li = document.createElement("li");
    li.textContent = `${f.label} (${f.field_type})`;
    fieldList.appendChild(li);
  });
}

submitBtn.addEventListener("click", () => {
  const payload = { fields };
  outputBox.textContent = JSON.stringify(payload, null, 2);
});


const side_by_side_elements = ["checkbox", "number", "color", "radio", "date", "time", "datetime-local", "datetime"];

function addField(field, form) {
    if(field.hasOwnProperty("options")) {
        if(field.field_type != "select") {
            var newInnerHtml = "";
            var optionNum = 0;
            newInnerHtml += `<fieldset><legend>${field.label}</legend>`;
            field.options.forEach(option => {
                optionNum++;
                newInnerHtml += `
                <div class="side-by-side-div">
                <label for="${option}">${option}</label>
                <input type="${field.field_type}" id="${field.field_id}" value="${option}" name="${field.field_name}" ${field.required && optionNum==1 ? "required" : ""} disabled>
                </div>`;
            });
            newInnerHtml += `</fieldset>`;
            form.innerHTML += newInnerHtml;
        }
        else {
            var newInnerHtml = "";
            newInnerHtml += 
            `<div class="side-by-side-div"><label for="${field.label}">${field.label}:</label>
             <select id="${field.field_id}" name="${field.field_name}">`;
            field.options.forEach(option => {
                newInnerHtml += `
                <option value="${option}" disabled>${option}</option>`;
            });
            newInnerHtml += `</select></div>`
            form.innerHTML += newInnerHtml;
        }
    }
    else if (field.field_type == "hidden") {
        form.innerHTML += `
        <label style="display: none;" for="${field.label}">${field.label}:</label>
        <input disabled type="${field.field_type}" id="${field.field_id}" name="${field.field_name}" ${field.required ? "required" : ""}>`;
    }
    else if (field.field_type == "textarea") {
        form.innerHTML += `
        <label for="${field.label}">${field.label}:</label>
        <textarea disabled id="${field.field_id}" name="${field.field_name}" ${field.required ? "required" : ""} rows="5" cols="50"></textarea>`;
    }
    else if(side_by_side_elements.includes(field.field_type)) {
        form.innerHTML += `
        <div class="side-by-side-div">
        <label for="${field.label}">${field.label}:</label>
        <input disabled type="${field.field_type}" id="${field.field_id}" name="${field.field_name}" maxlength="255" ${field.required ? "required" : ""}>
        </div>`;
    }
    else {
        form.innerHTML += `
        <label for="${field.label}">${field.label}:</label>
        <input disabled type="${field.field_type}" id="${field.field_id}" name="${field.field_name}" maxlength="255" ${field.required ? "required" : ""}>`;
    }
}