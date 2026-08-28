(() => {
    const STATE_CLASSES = [
        "is-neutral",
        "is-valid",
        "is-invalid",
    ];

    function setRuleState(element, state) {
        element.classList.remove(...STATE_CLASSES);

        if (state === true) {
            element.classList.add("is-valid");
            return;
        }

        if (state === false) {
            element.classList.add("is-invalid");
            return;
        }

        element.classList.add("is-neutral");
    }

    function resetRequirements(container) {
        container
            .querySelectorAll("[data-password-rule]")
            .forEach((element) => {
                setRuleState(element, null);
            });
    }

    function initPasswordRequirements(container) {
        const passwordInput = document.getElementById(
            container.dataset.passwordInput,
        );

        const emailInputId = container.dataset.emailInput;

        const emailInput = emailInputId
            ? document.getElementById(emailInputId)
            : null;

        const form = container.closest("form");

        const csrfInput = form?.querySelector(
            '[name="csrfmiddlewaretoken"]',
        );

        if (!passwordInput || !csrfInput) {
            return;
        }

        let timeoutId = null;
        let controller = null;

        async function validatePassword() {
            const password = passwordInput.value;

            if (!password) {
                controller?.abort();
                resetRequirements(container);
                return;
            }

            controller?.abort();
            controller = new AbortController();

            const body = new FormData();

            body.append("password", password);
            body.append(
                "mode",
                container.dataset.mode,
            );

            if (emailInput) {
                body.append(
                    "email",
                    emailInput.value,
                );
            }

            try {
                const response = await fetch(
                    container.dataset.validationUrl,
                    {
                        method: "POST",
                        body,
                        credentials: "same-origin",
                        headers: {
                            "X-CSRFToken": csrfInput.value,
                        },
                        signal: controller.signal,
                    },
                );

                if (!response.ok) {
                    throw new Error(
                        "Не удалось проверить пароль.",
                    );
                }

                const data = await response.json();

                Object.entries(
                    data.requirements,
                ).forEach(([ruleName, state]) => {
                    const element = container.querySelector(
                        `[data-password-rule="${ruleName}"]`,
                    );

                    if (element) {
                        setRuleState(
                            element,
                            state,
                        );
                    }
                });
            } catch (error) {
                if (error.name === "AbortError") {
                    return;
                }

                resetRequirements(container);
            }
        }

        function scheduleValidation() {
            clearTimeout(timeoutId);

            if (!passwordInput.value) {
                controller?.abort();
                resetRequirements(container);
                return;
            }

            timeoutId = setTimeout(
                validatePassword,
                300,
            );
        }

        passwordInput.addEventListener(
            "input",
            scheduleValidation,
        );

        if (emailInput) {
            emailInput.addEventListener(
                "input",
                scheduleValidation,
            );
        }

        if (passwordInput.value) {
            scheduleValidation();
        }
    }

    document
        .querySelectorAll(
            "[data-password-requirements]",
        )
        .forEach(initPasswordRequirements);
})();