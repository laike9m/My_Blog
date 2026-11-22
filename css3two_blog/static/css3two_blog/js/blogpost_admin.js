(function () {
    "use strict";

    function getCsrfToken() {
        const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (tokenInput && tokenInput.value) {
            return tokenInput.value;
        }
        const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : "";
    }

    function setStatus(statusEl, message, state) {
        if (!statusEl) {
            return;
        }
        statusEl.textContent = message;
        statusEl.classList.remove("is-error", "is-success");
        if (state === "error") {
            statusEl.classList.add("is-error");
        } else if (state === "success") {
            statusEl.classList.add("is-success");
        }
    }

    async function getArticleBody(bodyField, mdFileField) {
        const bodyText = bodyField ? bodyField.value.trim() : "";
        if (bodyText) {
            return bodyText;
        }
        if (mdFileField && mdFileField.files && mdFileField.files.length > 0) {
            return (await mdFileField.files[0].text()).trim();
        }
        return "";
    }

    document.addEventListener("DOMContentLoaded", function () {
        const btn = document.getElementById("summarize-description-btn");
        const descriptionField = document.getElementById("id_description");
        const bodyField = document.getElementById("id_body");
        const titleField = document.getElementById("id_title");
        const mdFileField = document.getElementById("id_md_file");
        const statusEl = document.getElementById("summarize-description-status");

        if (!btn || !descriptionField) {
            return;
        }

        const originalLabel = btn.textContent.trim();

        btn.addEventListener("click", async function () {
            const url = btn.dataset.summarizeUrl;
            if (!url) {
                return;
            }

            let bodyText = "";
            try {
                bodyText = await getArticleBody(bodyField, mdFileField);
            } catch (err) {
                setStatus(statusEl, "Failed to read markdown file: " + err.message, "error");
                return;
            }

            if (!bodyText) {
                setStatus(statusEl, "Please enter article body first.", "error");
                if (bodyField) {
                    bodyField.focus();
                }
                return;
            }

            btn.disabled = true;
            btn.textContent = "Summarizing...";
            setStatus(statusEl, "Generating summary with DeepSeek Flash...", "info");

            try {
                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    credentials: "same-origin",
                    body: JSON.stringify({
                        title: titleField ? titleField.value : "",
                        body: bodyText,
                    }),
                });

                const contentType = response.headers.get("content-type") || "";
                const data = contentType.includes("application/json")
                    ? await response.json()
                    : { error: "Server returned HTTP " + response.status };

                if (!response.ok) {
                    throw new Error(data.error || "Request failed (HTTP " + response.status + ")");
                }

                descriptionField.value = data.summary || "";
                descriptionField.dispatchEvent(new Event("input", { bubbles: true }));
                descriptionField.dispatchEvent(new Event("change", { bubbles: true }));
                setStatus(statusEl, "Summary generated.", "success");
            } catch (err) {
                setStatus(statusEl, err.message || "Failed to generate summary.", "error");
            } finally {
                btn.disabled = false;
                btn.textContent = originalLabel;
            }
        });
    });
})();

