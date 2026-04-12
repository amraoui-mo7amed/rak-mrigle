document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    var transError = document.querySelector('[data-trans-error]')?.dataset.transError || 'Error';
    var transSuccess = document.querySelector('[data-trans-success]')?.dataset.transSuccess || 'Success';
    var transSelectFile = document.querySelector('[data-trans-select-file]')?.dataset.transSelectFile || 'Please select a file first.';
    var transUploading = document.querySelector('[data-trans-uploading]')?.dataset.transUploading || 'Uploading...';
    var transSubmit = document.querySelector('[data-trans-submit]')?.dataset.transSubmit || 'Submit Payment Proof';

    var transApproveTitle = document.querySelector('[data-trans-approve-title]')?.dataset.transApproveTitle || 'Approve Payment';
    var transApproveText = document.querySelector('[data-trans-approve-text]')?.dataset.transApproveText || 'Are you sure you want to approve this payment?';
    var transYesApprove = document.querySelector('[data-trans-yes-approve]')?.dataset.transYesApprove || 'Yes, approve it';
    var transRejectTitle = document.querySelector('[data-trans-reject-title]')?.dataset.transRejectTitle || 'Reject Payment';
    var transRejectText = document.querySelector('[data-trans-reject-text]')?.dataset.transRejectText || 'Please provide a reason for rejection:';
    var transYesReject = document.querySelector('[data-trans-yes-reject]')?.dataset.transYesReject || 'Yes, reject it';
    var transCancel = document.querySelector('[data-trans-cancel]')?.dataset.transCancel || 'Cancel';
    var transReasonPlaceholder = document.querySelector('[data-trans-reason-placeholder]')?.dataset.transReasonPlaceholder || 'Enter rejection reason...';

    function getCsrfToken() {
        var token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) return token.value;
        var metaToken = document.querySelector('meta[name="csrf-token"]');
        return metaToken ? metaToken.content : '';
    }

    var uploadZone = document.getElementById('uploadZone');
    var fileInput = document.getElementById('proofFile');
    var previewContainer = document.getElementById('previewContainer');
    var fileName = document.getElementById('fileName');
    var submitBtn = document.getElementById('submitBtn');
    var removeFileBtn = document.getElementById('removeFile');

    var selectedFile = null;

    if (uploadZone) {
        uploadZone.addEventListener('click', function () {
            if (fileInput) fileInput.click();
        });

        uploadZone.addEventListener('dragover', function (e) {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', function () {
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', function (e) {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                if (fileInput) fileInput.files = e.dataTransfer.files;
                handleFileSelect(e.dataTransfer.files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', function () {
            if (fileInput.files.length) {
                handleFileSelect(fileInput.files[0]);
            }
        });
    }

    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', function () {
            selectedFile = null;
            if (fileInput) fileInput.value = '';
            if (previewContainer) previewContainer.classList.remove('has-file');
            if (submitBtn) submitBtn.disabled = true;
        });
    }

    function handleFileSelect(file) {
        selectedFile = file;
        if (fileName) fileName.textContent = file.name;
        if (previewContainer) previewContainer.classList.add('has-file');
        if (submitBtn) submitBtn.disabled = false;
    }

    if (submitBtn) {
        submitBtn.addEventListener('click', function () {
            if (!selectedFile) {
                Swal.fire({
                    icon: 'error',
                    title: transError,
                    text: transSelectFile
                });
                return;
            }

            var formData = new FormData();
            formData.append('proof_file', selectedFile);

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>' + transUploading;

            var submitUrl = submitBtn.dataset.submitUrl || '';

            fetch(submitUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: transSuccess,
                        text: data.message,
                        showConfirmButton: false,
                        timer: 2000
                    }).then(function () {
                        if (data.redirect_url) {
                            window.location.href = data.redirect_url;
                        }
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: transError,
                        text: data.errors ? data.errors.join(', ') : 'An error occurred'
                    });
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>' + transSubmit;
                }
            })
            .catch(function () {
                Swal.fire({
                    icon: 'error',
                    title: transError,
                    text: 'An error occurred while uploading'
                });
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>' + transSubmit;
            });
        });
    }

    var approveBtn = document.querySelector('[data-action="approve-payment"]');
    if (approveBtn) {
        approveBtn.addEventListener('click', function () {
            var paymentId = approveBtn.dataset.paymentId;
            var approveUrl = approveBtn.dataset.approveUrl || '';

            Swal.fire({
                icon: 'question',
                title: transApproveTitle,
                text: transApproveText,
                showCancelButton: true,
                confirmButtonColor: '#198754',
                cancelButtonColor: '#6c757d',
                confirmButtonText: transYesApprove,
                cancelButtonText: transCancel
            }).then(function (result) {
                if (result.isConfirmed) {
                    fetch(approveUrl, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCsrfToken(),
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(function (response) { return response.json(); })
                    .then(function (data) {
                        if (data.success) {
                            Swal.fire({
                                icon: 'success',
                                title: data.message,
                                showConfirmButton: false,
                                timer: 2000
                            }).then(function () {
                                location.reload();
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: transError,
                                text: data.errors ? data.errors.join(', ') : 'An error occurred'
                            });
                        }
                    });
                }
            });
        });
    }

    var rejectBtn = document.querySelector('[data-action="reject-payment"]');
    if (rejectBtn) {
        rejectBtn.addEventListener('click', function () {
            var paymentId = rejectBtn.dataset.paymentId;
            var rejectUrl = rejectBtn.dataset.rejectUrl || '';

            Swal.fire({
                icon: 'warning',
                title: transRejectTitle,
                text: transRejectText,
                input: 'textarea',
                inputPlaceholder: transReasonPlaceholder,
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: transYesReject,
                cancelButtonText: transCancel
            }).then(function (result) {
                if (result.isConfirmed) {
                    var formData = new FormData();
                    formData.append('reason', result.value || '');

                    fetch(rejectUrl, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCsrfToken(),
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: formData
                    })
                    .then(function (response) { return response.json(); })
                    .then(function (data) {
                        if (data.success) {
                            Swal.fire({
                                icon: 'success',
                                title: data.message,
                                showConfirmButton: false,
                                timer: 2000
                            }).then(function () {
                                location.reload();
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: transError,
                                text: data.errors ? data.errors.join(', ') : 'An error occurred'
                            });
                        }
                    });
                }
            });
        });
    }
});
