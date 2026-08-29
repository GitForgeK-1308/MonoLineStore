document.addEventListener("DOMContentLoaded", () => {
    const variantsElement = document.getElementById(
        "available-product-variants",
    );

    const form = document.querySelector(
        ".product-form",
    );

    if (variantsElement && form) {
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
    }

    const mainImage = document.querySelector(
        "[data-main-image]",
    );

    const thumbnails = [
        ...document.querySelectorAll(
            "[data-image]",
        ),
    ];

    if (!mainImage || thumbnails.length === 0) {
        return;
    }

    thumbnails.forEach((thumbnail) => {
        thumbnail.addEventListener(
            "click",
            () => {
                const imageUrl = thumbnail.dataset.image;
                const imageAlt = thumbnail.dataset.alt;

                if (!imageUrl) {
                    return;
                }

                thumbnails.forEach((item) => {
                    item.classList.remove(
                        "product-detail__thumbnail--active",
                    );
                });

                thumbnail.classList.add(
                    "product-detail__thumbnail--active",
                );

                mainImage.classList.add(
                    "is-changing",
                );

                window.setTimeout(() => {
                    mainImage.src = imageUrl;

                    if (imageAlt) {
                        mainImage.alt = imageAlt;
                    }

                    mainImage.classList.remove(
                        "is-changing",
                    );
                }, 120);
            },
        );
    });
});