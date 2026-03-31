document.addEventListener("DOMContentLoaded", function() {
"use strict";

function togglePassword(fieldId) {
const input = document.getElementById(fieldId);
const button = event.currentTarget;
const icon = button.querySelector("i");

if (!input || !icon) {
return;
}

if (input.type === "password") {
input.type = "text";
icon.classList.remove("fa-eye");
icon.classList.add("fa-eye-slash");
} else {
input.type = "password";
icon.classList.remove("fa-eye-slash");
icon.classList.add("fa-eye");
}
}

window.togglePassword = togglePassword;

const phoneInput = document.getElementById("phone_number");
if (phoneInput) {
phoneInput.addEventListener("input", function() {
this.value = this.value.replace(/[^0-9]/g, "");
});
}

const roleOptions = document.querySelectorAll(".role-option");
const driverLicenseField = document.querySelector(".driver-license-field");
const driverLicenseInput = document.getElementById("driver_license");

roleOptions.forEach(function(option) {
option.addEventListener("click", function() {
roleOptions.forEach(function(opt) {
opt.classList.remove("selected");
});
this.classList.add("selected");
const radio = this.querySelector('input[type="radio"]');
radio.checked = true;

if (this.dataset.value === "provider") {
driverLicenseField.style.display = "block";
if (driverLicenseInput) {
driverLicenseInput.setAttribute("required", "");
}
} else {
driverLicenseField.style.display = "none";
if (driverLicenseInput) {
driverLicenseInput.removeAttribute("required");
}
}
});
});
});
