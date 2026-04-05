document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    function getCsrfToken() {
        var token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) return token.value;
        var metaToken = document.querySelector('meta[name="csrf-token"]');
        return metaToken ? metaToken.content : '';
    }

    function getOfferUrls() {
        var container = document.querySelector('[data-offer-urls]');
        if (!container) return {};
        return {
            approve: container.dataset.urlApprove || '',
            reject: container.dataset.urlReject || '',
            delete: container.dataset.urlDelete || '',
            list: container.dataset.urlList || '',
            edit: container.dataset.urlEdit || '',
            details: container.dataset.urlDetails || ''
        };
    }

    function buildUrl(template, offerId) {
        return template.replace('0', offerId);
    }

    window.approveOffer = function (offerId) {
        var urls = getOfferUrls();
        var url = urls.approve ? buildUrl(urls.approve, offerId) : '/dashboard/offers/' + offerId + '/approve/';
        Swal.fire({
            icon: "question",
            title: typeof window.trans_approve_confirm_title !== "undefined" ? window.trans_approve_confirm_title : "Approve Offer",
            text: typeof window.trans_approve_confirm_text !== "undefined" ? window.trans_approve_confirm_text : "Are you sure you want to approve this offer?",
            showCancelButton: true,
            confirmButtonColor: "#198754",
            cancelButtonColor: "#6c757d",
            confirmButtonText: typeof window.trans_yes_approve !== "undefined" ? window.trans_yes_approve : "Yes, approve it",
            cancelButtonText: typeof window.trans_cancel !== "undefined" ? window.trans_cancel : "Cancel"
        }).then(function (result) {
            if (result.isConfirmed) {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", url);
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
                                location.reload();
                            });
                        } else {
                            Swal.fire({
                                icon: "error",
                                title: typeof window.trans_error !== "undefined" ? window.trans_error : "Error",
                                text: response.message
                            });
                        }
                    }
                };
                xhr.send();
            }
        });
    };

    window.rejectOffer = function (offerId) {
        var urls = getOfferUrls();
        var url = urls.reject ? buildUrl(urls.reject, offerId) : '/dashboard/offers/' + offerId + '/reject/';
        Swal.fire({
            icon: "warning",
            title: typeof window.trans_reject_confirm_title !== "undefined" ? window.trans_reject_confirm_title : "Reject Offer",
            text: typeof window.trans_reject_confirm_text !== "undefined" ? window.trans_reject_confirm_text : "Please provide a reason for rejection:",
            input: "textarea",
            inputPlaceholder: typeof window.trans_rejection_reason !== "undefined" ? window.trans_rejection_reason : "Enter rejection reason...",
            showCancelButton: true,
            confirmButtonColor: "#dc3545",
            cancelButtonColor: "#6c757d",
            confirmButtonText: typeof window.trans_yes_reject !== "undefined" ? window.trans_yes_reject : "Yes, reject it",
            cancelButtonText: typeof window.trans_cancel !== "undefined" ? window.trans_cancel : "Cancel",
            inputValidator: function (value) {
                if (!value) {
                    return typeof window.trans_reason_required !== "undefined" ? window.trans_reason_required : "Please enter a reason";
                }
            }
        }).then(function (result) {
            if (result.isConfirmed) {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", url);
                xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
                xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
                xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
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
                                location.reload();
                            });
                        } else {
                            Swal.fire({
                                icon: "error",
                                title: typeof window.trans_error !== "undefined" ? window.trans_error : "Error",
                                text: response.message
                            });
                        }
                    }
                };
                xhr.send("reason=" + encodeURIComponent(result.value));
            }
        });
    };

    window.deleteOffer = function (offerId) {
        var urls = getOfferUrls();
        var url = urls.delete ? buildUrl(urls.delete, offerId) : '/dashboard/offers/' + offerId + '/delete/';
        var redirectUrl = urls.list || '/dashboard/offers/';
        Swal.fire({
            icon: "warning",
            title: typeof window.trans_delete_confirm_title !== "undefined" ? window.trans_delete_confirm_title : "Delete Offer",
            text: typeof window.trans_delete_confirm_text !== "undefined" ? window.trans_delete_confirm_text : "Are you sure you want to delete this offer? This action cannot be undone.",
            showCancelButton: true,
            confirmButtonColor: "#dc3545",
            cancelButtonColor: "#6c757d",
            confirmButtonText: typeof window.trans_yes_delete !== "undefined" ? window.trans_yes_delete : "Yes, delete it",
            cancelButtonText: typeof window.trans_cancel !== "undefined" ? window.trans_cancel : "Cancel"
        }).then(function (result) {
            if (result.isConfirmed) {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", url);
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
                                window.location.href = redirectUrl;
                            });
                        } else {
                            Swal.fire({
                                icon: "error",
                                title: typeof window.trans_error !== "undefined" ? window.trans_error : "Error",
                                text: response.message
                            });
                        }
                    }
                };
                xhr.send();
            }
        });
    };
});
