const commentForm = document.getElementById("comment-form");

if (commentForm) {

    commentForm.addEventListener("submit", function (e) {

        e.preventDefault();

        const formData = new FormData(commentForm);

        fetch(commentForm.action, {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {

            const message = document.getElementById("comment-message");

            if (data.success) {

                message.innerHTML = `
                    <div class="alert alert-success alert-dismissible fade show">
                        ${data.message}
                        <button type="button"
                                class="btn-close"
                                data-bs-dismiss="alert">
                        </button>
                    </div>
                `;

                commentForm.reset();

            } else {

                let errors = "";

                for (const field in data.errors) {
                    errors += data.errors[field].join("<br>");
                }

                message.innerHTML = `
                    <div class="alert alert-danger alert-dismissible fade show">
                        ${errors}
                        <button type="button"
                                class="btn-close"
                                data-bs-dismiss="alert">
                        </button>
                    </div>
                `;
            }

        })
        .catch(() => {

            document.getElementById("comment-message").innerHTML = `
                <div class="alert alert-danger">
                    Something went wrong.
                </div>
            `;

        });

    });

}

function toggleReplyForm(commentId) {

    const form = document.getElementById(`reply-form-${commentId}`);

    if (form.style.display === "none") {
        form.style.display = "block";
    } else {
        form.style.display = "none";
    }

}