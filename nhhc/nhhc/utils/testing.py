import io
import random
import string

import gnupg
from django.conf import settings
from faker import Faker
from loguru import logger

MockData = Faker()


def generate_mock_PhoneNumberField() -> str:
    """
    This function generates a random 11-digit phone number field,
    which is used in testing as the Fixture library `model_bakery` does  not support the3 PhoneNumberField model field for `web.models.EmploymentApplicationModel` and `web.models.ClientIntrerestModels`
    The first digit is '+1', the next three digits represent the area code,
    and the remaining digits represent the local phone number.

    Args:
        None

    Returns:
        static_number: string = random 11-digit digit string in the format that meets the constraints of the field class phonenumber_field.modelfields.PhoneNumberField

    Raises:
        None
    """

    phone_number = "+1"

    for _ in range(3):
        phone_number += str(random.randint(0, 9))

    for _ in range(3):
        phone_number += str(random.randint(0, 9))

    for _ in range(4):
        phone_number += str(random.randint(0, 9))

    return phone_number


def generate_mock_ZipCodeField() -> str:
    """
    This function generates a random 5-digit zip code field in the format 21217.
    It will return the zip code as a string.
    Args:
        None

    Returns:
        postal_code: string = random 5-digit string in the format that constraints of the field class localflavor.us.models.USZipCodeField
    """
    # Initializes the zip code with a random 5-digit integer
    postal_code = str(random.randint(10000, 99999))

    # Checks if the generated zip code is either "10000" or "99999" and recureively regenerates a nw random 5 digit sequence.
    if postal_code in ["10000", "99999"]:
        return generate_mock_ZipCodeField()

    return postal_code


def generate_mock_USSocialSecurityNumberField() -> str:
    """Generates a mock  9- digit US Social Security Number (SSN) in the hypenated string format.

    Args:
        None

    Returns:
        str: The generated SSN in the format "123-45-6789", that constraints of the field class localflavor.us.models.USSocialSecurityNumberField

    Raises:
        None
    """
    while True:
        # Generates the first three digits of the Social Security Number (SSN)
        first_three_digits = random.randint(1, 799)

        # If the first three digits are greater than or equal to 666, we generate a new SSN
        if first_three_digits >= 666:
            continue

        # Generates the middle two digits of the SSN
        middle_two_digits = random.randint(0, 99)

        # Generates the last four digits of the SSN
        last_four_digits = random.randint(1, 9999)

        # Returns the generated SSN in the correct format: "123-45-6789"
        return f"{first_three_digits:03d}-{middle_two_digits:02d}-{last_four_digits:04d}"


def generate_mock_PhoneNumberField() -> str:
    """
    This function generates a random 11-digit phone number field,
    which is used in testing as the Fixture library `model_bakery` does  not support the3 PhoneNumberField model field for `web.models.EmploymentApplicationModel` and `web.models.ClientIntrerestModels`
    The first digit is '+1', the next three digits represent the area code,
    and the remaining digits represent the local phone number.

    Args:
        None

    Returns:
        static_number: string = random 11-digit digit string in the format that meets the constraints of the field class phonenumber_field.modelfields.PhoneNumberField

    Raises:
        None
    """

    phone_number = "+1"

    for _ in range(3):
        phone_number += str(random.randint(0, 9))

    for _ in range(3):
        phone_number += str(random.randint(0, 9))

    for _ in range(4):
        phone_number += str(random.randint(0, 9))

    return phone_number


def generate_mock_ZipCodeField() -> str:
    """
    This function generates a random 5-digit zip code field in the format 21217.
    It will return the zip code as a string.
    Args:
        None

    Returns:
        postal_code: string = random 5-digit string in the format that constraints of the field class localflavor.us.models.USZipCodeField
    """
    # Initializes the zip code with a random 5-digit integer
    postal_code = str(random.randint(10000, 99999))

    # Checks if the generated zip code is either "10000" or "99999" and recureively regenerates a nw random 5 digit sequence.
    if postal_code in ["10000", "99999"]:
        return generate_mock_ZipCodeField()

    return postal_code


def generate_mock_USSocialSecurityNumberField() -> str:
    """Generates a mock  9- digit US Social Security Number (SSN) in the hypenated string format.

    Args:
        None

    Returns:
        str: The generated SSN in the format "123-45-6789", that constraints of the field class localflavor.us.models.USSocialSecurityNumberField

    Raises:
        None
    """
    while True:
        # Generates the first three digits of the Social Security Number (SSN)
        first_three_digits = random.randint(1, 799)

        # If the first three digits are greater than or equal to 666, we generate a new SSN
        if first_three_digits >= 666:
            continue

        # Generates the middle two digits of the SSN
        middle_two_digits = random.randint(0, 99)

        # Generates the last four digits of the SSN
        last_four_digits = random.randint(1, 9999)

        # Returns the generated SSN in the correct format: "123-45-6789"
        return f"{first_three_digits:03d}-{middle_two_digits:02d}-{last_four_digits:04d}"


def generate_random_encrypted_email():
    """Generates a random encrypted email address."""

    gpg = gnupg.GPG()
    raw_email = MockData.email()
    private_key = settings.ENCRYPT_PRIVATE_KEY
    public_key = settings.ENCRYPT_PUBLIC_KEY
    import_result = gpg.import_keys(public_key)
    if import_result.count == 0:
        logger.error("Error: No keys imported. Make sure the public key file is correct.")
        raise ValueError()

    recipient_key_id = import_result.results[0]["fingerprint"]

    ciphertext = gpg.encrypt(raw_email, recipients=[recipient_key_id], always_trust=True)

    if ciphertext.ok:
        return ciphertext.data
    else:
        logger.error("Error: Encryption failed.")
        raise RuntimeError("Value Not Encrypted")


def generate_random_encrypted_char():
    """Generates a random encrypted email address."""

    gpg = gnupg.GPG()
    chars = string.ascii_lowercase + string.ascii_uppercase
    length = random.randint(1, 60)
    raw_char = "".join(random.choice(chars) for i in range(length))
    private_key = settings.ENCRYPT_PRIVATE_KEY
    public_key = settings.ENCRYPT_PUBLIC_KEY
    import_result = gpg.import_keys(public_key)
    if import_result.count == 0:
        logger.error("Error: No keys imported. Make sure the public key file is correct.")
        raise ValueError()

    recipient_key_id = import_result.results[0]["fingerprint"]

    ciphertext = gpg.encrypt(raw_char, recipients=[recipient_key_id], always_trust=True)

    if ciphertext.ok:
        return ciphertext.data
    else:
        logger.error("Error: Encryption failed.")
        raise RuntimeError("Value Not Encrypted")
