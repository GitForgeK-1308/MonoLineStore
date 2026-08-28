from django.contrib.auth.password_validation import (
    CommonPasswordValidator,
    MinimumLengthValidator,
    NumericPasswordValidator,
    UserAttributeSimilarityValidator,
    get_default_password_validators,
)
from django.core.exceptions import ValidationError

VALIDATOR_RULES = (
    (
        MinimumLengthValidator,
        "min_length",
    ),
    (
        UserAttributeSimilarityValidator,
        "similarity",
    ),
    (
        CommonPasswordValidator,
        "common_password",
    ),
    (
        NumericPasswordValidator,
        "numeric",
    ),
)


def get_password_requirements(
    password,
    *,
    user=None,
):
    requirements = {rule_name: None for _, rule_name in VALIDATOR_RULES}

    for validator in get_default_password_validators():
        rule_name = next(
            (
                name
                for validator_class, name in VALIDATOR_RULES
                if isinstance(
                    validator,
                    validator_class,
                )
            ),
            None,
        )

        if rule_name is None:
            continue

        try:
            validator.validate(
                password,
                user=user,
            )
        except ValidationError:
            requirements[rule_name] = False
        else:
            requirements[rule_name] = True

    return requirements
