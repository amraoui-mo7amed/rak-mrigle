document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    function getCsrfToken() {
        var token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) return token.value;
        var metaToken = document.querySelector('meta[name="csrf-token"]');
        return metaToken ? metaToken.content : '';
    }

    window.deleteProviderOffer = function (offerId) {
        var deleteUrl = '/dashboard/my-offers/' + offerId + '/delete/';
        var redirectUrl = '/dashboard/my-offers/';

        Swal.fire({
            icon: "warning",
            title: window.trans_delete_confirm_title || "Delete Offer",
            text: window.trans_delete_confirm_text || "Are you sure you want to delete this offer? This action cannot be undone.",
            showCancelButton: true,
            confirmButtonColor: "#dc3545",
            cancelButtonColor: "#6c757d",
            confirmButtonText: window.trans_yes_delete || "Yes, delete it",
            cancelButtonText: window.trans_cancel || "Cancel"
        }).then(function (result) {
            if (result.isConfirmed) {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", deleteUrl);
                xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
                xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
                xhr.onload = function () {
                    if (xhr.status === 200) {
                        var response = JSON.parse(xhr.responseText);
                        if (response.success) {
                            Swal.fire({
                                icon: "success",
                                title: response.message,
                                showConfirmButton: false,
                                timer: 2000
                            }).then(function () {
                                window.location.href = response.redirect_url || redirectUrl;
                            });
                        } else {
                            Swal.fire({
                                icon: "error",
                                title: window.trans_error || "Error",
                                text: response.message
                            });
                        }
                    }
                };
                xhr.send();
            }
        });
    };

    window.handleOfferForm = function (formId, offerId) {
        var form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', function (e) {
            e.preventDefault();

            var formData = new FormData(form);
            var xhr = new XMLHttpRequest();
            xhr.open('POST', window.location.href);
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            xhr.setRequestHeader('X-CSRFToken', getCsrfToken());

            xhr.onload = function () {
                if (xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: response.message,
                            showConfirmButton: false,
                            timer: 2000
                        }).then(function () {
                            if (response.redirect_url) {
                                window.location.href = response.redirect_url;
                            }
                        });
                    } else {
                        if (response.errors && response.errors.length > 0) {
                            var errorList = document.getElementById('errorList');
                            if (errorList) {
                                errorList.innerHTML = '';
                                response.errors.forEach(function (error) {
                                    var li = document.createElement('li');
                                    li.className = 'alert alert-danger mb-2';
                                    li.textContent = error;
                                    errorList.appendChild(li);
                                });
                            }
                            Swal.fire({
                                icon: 'error',
                                title: window.trans_error || 'Error',
                                text: response.errors.join('\n')
                            });
                        }
                    }
                }
            };
            xhr.send(formData);
        });
    };

    var pricingSelect = document.querySelector('#pricingTypeSelect input[name="pricing_type"]');
    var pricePerKmWrapper = document.getElementById('pricePerKmWrapper');
    var pricePerHourWrapper = document.getElementById('pricePerHourWrapper');

    function updatePricingFields() {
        var value = pricingSelect ? pricingSelect.value : '';
        if (value === 'distance') {
            pricePerKmWrapper.style.display = 'block';
            pricePerHourWrapper.style.display = 'none';
        } else if (value === 'hourly') {
            pricePerKmWrapper.style.display = 'none';
            pricePerHourWrapper.style.display = 'block';
        } else {
            pricePerKmWrapper.style.display = 'none';
            pricePerHourWrapper.style.display = 'none';
        }
    }

    if (pricingSelect) {
        pricingSelect.addEventListener('change', updatePricingFields);
        updatePricingFields();
    }

    var offerForm = document.getElementById('offerForm');
    if (offerForm) {
        window.handleOfferForm('offerForm');
    }
});
