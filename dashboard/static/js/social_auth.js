document.addEventListener("DOMContentLoaded", () => {
    const editProviderForm = document.getElementById("editProviderForm");

    document.querySelectorAll(".edit-provider-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            document.getElementById("editProviderPk").value = btn.dataset.pk;
            document.getElementById("editProviderName").value = btn.dataset.provider;
            document.getElementById("editClientId").value = btn.dataset.clientId;
            document.getElementById("editSecretInput").value = btn.dataset.secret;
            
            const pk = btn.dataset.pk;
            editProviderForm.action = `/dashboard/social-auth/${pk}/update/`;
        });
    });

    document.querySelectorAll(".delete-provider-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const pk = btn.dataset.pk;
            const providerName = btn.dataset.provider;

            Swal.fire({
                title: "Delete Configuration?",
                text: `Are you sure you want to delete the ${providerName} configuration? This action cannot be undone!`,
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!",
                cancelButtonText: "Cancel",
                reverseButtons: true,
            }).then(async (result) => {
                if (result.isConfirmed) {
                    Swal.fire({
                        allowOutsideClick: false,
                        didOpen: () => Swal.showLoading()
                    });

                    try {
                        const response = await fetch(`/dashboard/social-auth/${pk}/delete/`, {
                            method: "POST",
                            headers: {
                                "X-Requested-With": "XMLHttpRequest",
                                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                                               document.querySelector('meta[name="csrf-token"]')?.content,
                            },
                        });

                        const data = await response.json();

                        if (data.success) {
                            Swal.fire({
                                icon: "success",
                                title: "Deleted!",
                                text: data.message,
                            }).then(() => {
                                window.location.reload();
                            });
                        } else {
                            Swal.fire({
                                icon: "error",
                                title: "Error",
                                text: data.message,
                            });
                        }
                    } catch (error) {
                        Swal.fire({
                            icon: "error",
                            title: "Error",
                            text: error.message,
                        });
                    }
                }
            });
        });
    });
});
