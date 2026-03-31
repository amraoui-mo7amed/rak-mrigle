document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    var roleOptionCards = document.querySelectorAll(".role-option-card");
    var driverLicenseSection = document.querySelector(".driver-license-section");
    var profilePictureInput = document.getElementById("profile_picture");
    var roleForm = document.getElementById("roleForm");
    var deleteAccountBtn = document.getElementById("deleteAccountBtn");

    roleOptionCards.forEach(function (card) {
        card.addEventListener("click", function () {
            roleOptionCards.forEach(function (c) {
                c.classList.remove("selected");
            });
            this.classList.add("selected");
            var radio = this.querySelector('input[type="radio"]');
            radio.checked = true;

            if (this.dataset.value === "provider") {
                driverLicenseSection.style.display = "block";
            } else {
                driverLicenseSection.style.display = "none";
            }
        });
    });

    if (profilePictureInput) {
        profilePictureInput.addEventListener("change", function () {
            if (this.files && this.files.length > 0) {
                var form = document.getElementById("profileForm");
                var formData = new FormData(form);
                formData.set("profile_picture", this.files[0]);

                var xhr = new XMLHttpRequest();
                xhr.open("POST", form.action);
                xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
                xhr.setRequestHeader("X-CSRFToken", form.querySelector('[name=csrfmiddlewaretoken]').value);

                xhr.onload = function () {
                    if (xhr.status === 200) {
                        var response = JSON.parse(xhr.responseText);
                        if (response.success) {
                            location.reload();
                        }
                    }
                };
                xhr.send(formData);
            }
        });
    }

    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener("click", function (e) {
            e.preventDefault();
            var btn = this;

            Swal.fire({
                icon: "warning",
                title: btn.dataset.confirmTitle,
                text: btn.dataset.confirmText,
                showCancelButton: true,
                confirmButtonColor: "#DC2626",
                cancelButtonColor: "#64748B",
                confirmButtonText: btn.dataset.confirmButton,
                cancelButtonText: btn.dataset.cancelButton,
            }).then(function (result) {
                if (result.isConfirmed) {
                    var xhr = new XMLHttpRequest();
                    xhr.open("POST", btn.dataset.deleteUrl);
                    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
                    xhr.setRequestHeader("X-CSRFToken", document.querySelector('[name=csrfmiddlewaretoken]').value);

                    xhr.onload = function () {
                        if (xhr.status === 200) {
                            var response = JSON.parse(xhr.responseText);
                            if (response.success) {
                                Swal.fire({
                                    icon: "success",
                                    title: response.message,
                                    showConfirmButton: false,
                                    timer: 2000,
                                }).then(function () {
                                    window.location.href = response.redirect_url;
                                });
                            } else {
                                Swal.fire({
                                    icon: "error",
                                    title: "Error",
                                    text: response.errors ? response.errors.join(", ") : "An error occurred",
                                });
                            }
                        }
                    };
                    xhr.send();
                }
            });
        });
    }
});