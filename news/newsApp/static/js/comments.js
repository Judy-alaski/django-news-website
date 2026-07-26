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

let activePlaceholder = null;

function toggleReplyForm(commentId) {

    const placeholder = document.getElementById(
        `reply-placeholder-${commentId}`
    );

    const template = document.getElementById(
        "reply-form-template"
    );

    // Close the currently open reply form
    if (activePlaceholder && activePlaceholder !== placeholder) {
        activePlaceholder.innerHTML = "";
    }

    // Toggle current reply form
    if (placeholder.innerHTML.trim() !== "") {
        placeholder.innerHTML = "";
        activePlaceholder = null;
        return;
    }

    placeholder.innerHTML = template.innerHTML;

    placeholder.querySelector("#reply-parent-id").value = commentId;

    activePlaceholder = placeholder;

    attachReplyHandler();
}

function closeReplyForm() {

    if (activePlaceholder) {

        activePlaceholder.innerHTML = "";

        activePlaceholder = null;

    }

}

function attachReplyHandler() {

    const replyForm = document.getElementById("reply-form");

    if (!replyForm) return;

    replyForm.addEventListener("submit", function (e) {

        e.preventDefault();

        const formData = new FormData(replyForm);

        fetch(commentForm.action, {

            method: "POST",

            headers: {
                "X-CSRFToken":
                    document.querySelector("[name=csrfmiddlewaretoken]").value
            },

            body: formData

        })

        .then(response => response.json())

        .then(data => {

            if (data.success) {

                alert(data.message);

                replyForm.reset();

                closeReplyForm();

            } else {

                alert("Please check your input.");

            }

        })

        .catch(() => {

            alert("Something went wrong.");

        });

    });

}