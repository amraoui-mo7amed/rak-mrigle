document.addEventListener("DOMContentLoaded", function() {
"use strict";

var socialContainer = document.querySelector(".social-login-container");
var socialButtons = document.querySelectorAll(".btn-social");

socialButtons.forEach(function(button) {
button.addEventListener("click", function(e) {
if (this.getAttribute("href") === "#") {
e.preventDefault();
var container = socialContainer;
Swal.fire({
icon: "warning",
title: container.dataset.notConfiguredTitle,
text: container.dataset.notConfiguredText,
confirmButtonText: container.dataset.okText
});
}
});
});
});
