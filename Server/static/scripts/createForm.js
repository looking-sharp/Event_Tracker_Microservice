const labelInput = document.getElementById("labelInput");
const nameInput = document.getElementById("nameInput");
const typeInput = document.getElementById("typeInput");
const requiredInput = document.getElementById("requiredInput");

const optionsContainer = document.getElementById("optionsContainer");
const multiVariedContainer = document.getElementById("multiVariedContainer");
const optionsInput = document.getElementById("optionsInput");
const multiVariedInput = document.getElementById("multiVaried");

const addFieldBtn = document.getElementById("addFieldBtn");
const submitBtn = document.getElementById("submitBtn");

const fieldList = document.getElementById("fieldList");
const fieldsOutput = document.getElementById("fieldsOutput");

const previewForm = document.getElementById("previewForm");
const submitForm = document.getElementById("submitForm");

const builder = document.getElementById("builder");
const showBuilder = document.getElementById("showBuilder");

// populate with default fields
let fields = [
  {
    "field_id": "fld_1",
    "field_type": "text",
    "field_name": "first_name",
    "label": "First Name",
    "required": true
  },
  {
    "field_id": "fld_2",
    "field_type": "text",
    "field_name": "last_name",
    "label": "Last Name",
    "required": true
  },
  {
    "field_id": "fld_3",
    "field_type": "email",
    "field_name": "email",
    "label": "Email",
    "required": true
  }];

let idCounter = 4;

document.addEventListener("DOMContentLoaded", () => {
  fields.forEach(element => {
    addField(element, previewForm)
  });
  multiVariedContainer.style.display = "none";
  optionsContainer.style.display = "none";
});

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
    multiVariedContainer.style.display = "grid";
  } 
  else {
    multiVariedContainer.style.display = "none";
  }
});

multiVariedInput.addEventListener("change", () => {
  console.log("CHANGE")
  if (multiVariedInput.checked) {
    optionsContainer.style.display = "block";
  }
  else {
    optionsContainer.style.display = "none";
  }
});

showBuilder.addEventListener("click", () => {
  builder.style.display = "block";
  showBuilder.style.display = "none";
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
  addField(field, previewForm);

  labelInput.value = "";
  nameInput.value = "";
  optionsInput.value = "";
  requiredInput.checked = false;
  multiVariedInput.checked = false;
  showBuilder.style.display = "block";
  builder.style.display = "none";
  
});

function deleteField(id) {
  if (confirm('Are you sure you want to delete this field?')) {
    id = id.toString().trim();
    const indexToRemove = fields.findIndex(obj => obj.field_id === id);
    if (indexToRemove !== -1) {
      fields.splice(indexToRemove, 1);
    }
  }

  previewForm.innerHTML = "<h2>Form Preview</h2>";
  fields.forEach(element => {
    addField(element, previewForm)
  });
}

const side_by_side_elements = ["checkbox", "number", "color", "radio", "date", "time", "datetime-local", "datetime"];

function addField(field, form) {
  if(field.hasOwnProperty("options")) {
    if(field.field_type != "select") {
      var newInnerHtml = "";
      var optionNum = 0;
      newInnerHtml += `<fieldset><legend>${field.label}<span class="required">${field.required ? " *" : ""}</span></legend>`;
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
      `<div class="side-by-side-div"><label for="${field.label}">${field.label}:<span class="required">${field.required ? "*" : ""}</span></label>
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
    <label style="display: none;" for="${field.label}">${field.label}:<span class="required">${field.required ? "*" : ""}</span></label>
    <input disabled type="${field.field_type}" id="${field.field_id}" name="${field.field_name}" ${field.required ? "required" : ""}>`;
  }
  else if (field.field_type == "textarea") {
    form.innerHTML += `
    <label for="${field.label}">${field.label}:<span class="required">${field.required ? "*" : ""}</span></label>
    <textarea disabled id="${field.field_id}" name="${field.field_name}" ${field.required ? "required" : ""} rows="5" cols="50"></textarea>`;
  }
  else if(side_by_side_elements.includes(field.field_type)) {
    form.innerHTML += `
    <div class="side-by-side-div">
    <label for="${field.label}">${field.label}:<span class="required">${field.required ? "*" : ""}</span></label>
    <input disabled type="${field.field_type}" id="${field.field_id}" name="${field.field_name}" maxlength="255" ${field.required ? "required" : ""}>
    </div>`;
  }
  else {
    form.innerHTML += `
    <label for="${field.label}">${field.label}:<span class="required">${field.required ? "*" : ""}</span></label>
    <input disabled type="${field.field_type}" id="${field.field_id}" name="${field.field_name}" maxlength="255" ${field.required ? "required" : ""}>`;
  }
  form.innerHTML += `<button class="delete-field-btn" id="${field.field_id}DeleteBtn" onclick="deleteField('${field.field_id}')">Delete Field</button>`
}

// temp
submitForm.addEventListener("submit", function(e) {
  const payload = { fields };
  fieldsOutput.value = JSON.stringify(payload);
});