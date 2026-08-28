document.addEventListener("DOMContentLoaded", () => {
    const variantsElement = document.getElementById(
        "available-product-variants",
    );

    const form = document.querySelector(
        ".product-form",
    );

    if (!variantsElement || !form) {
        return;
    }

    const variants = JSON.parse(
        variantsElement.textContent,
    );

    const colorInputs = [
        ...form.querySelectorAll(
            'input[name="color"]',
        ),
    ];

    const sizeInputs = [
        ...form.querySelectorAll(
            'input[name="size"]',
        ),
    ];

    const submitButton = form.querySelector(
        ".product-form__button",
    );

    const setOptionAvailability = (
        input,
        isAvailable,
    ) => {
        input.disabled = !isAvailable;

        const option = input.closest(
            ".product-option",
        );

        if (option) {
            option.classList.toggle(
                "product-option--disabled",
                !isAvailable,
            );
        }

        if (!isAvailable && input.checked) {
            input.checked = false;
        }
    };

    const availableColors = new Set(
        variants.map(
            (variant) => variant.color,
        ),
    );

    colorInputs.forEach((input) => {
        setOptionAvailability(
            input,
            availableColors.has(input.value),
        );
    });

    sizeInputs.forEach((input) => {
        setOptionAvailability(
            input,
            false,
        );
    });

    const updateSubmitButton = () => {
        if (!submitButton) {
            return;
        }

        const selectedColor = colorInputs.find(
            (input) => input.checked,
        );

        const selectedSize = sizeInputs.find(
            (input) => input.checked,
        );

        const combinationExists = variants.some(
            (variant) =>
                variant.color === selectedColor?.value &&
                variant.size === selectedSize?.value &&
                variant.stock > 0,
        );

        submitButton.disabled = !combinationExists;
    };

    colorInputs.forEach((colorInput) => {
        colorInput.addEventListener(
            "change",
            () => {
                const availableSizes = new Set(
                    variants
                        .filter(
                            (variant) =>
                                variant.color ===
                                    colorInput.value &&
                                variant.stock > 0,
                        )
                        .map(
                            (variant) =>
                                variant.size,
                        ),
                );

                sizeInputs.forEach((sizeInput) => {
                    setOptionAvailability(
                        sizeInput,
                        availableSizes.has(
                            sizeInput.value,
                        ),
                    );
                });

                updateSubmitButton();
            },
        );
    });

    sizeInputs.forEach((sizeInput) => {
        sizeInput.addEventListener(
            "change",
            updateSubmitButton,
        );
    });

    updateSubmitButton();
});