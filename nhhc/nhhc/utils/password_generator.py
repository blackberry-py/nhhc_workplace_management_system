import random
import string


class RandomPasswordGenerator:
    """
    A class for generating random passwords.

    Attributes:
    min_length (int): The minimum length of the generated password.
    max_length (int): The maximum length of the generated password.
    """

    # Set minimum and maximum password length
    min_length = 8
    max_length = 12

    @staticmethod
    def generate() -> str:
        """
        Generates a random password.
        Args:
            None

        Returns:
            str: A randomly generated password.

        Rasies:
            None
        """
        # Define the character sets to be used for password generation
        # Use all lowerzcase, uppercase, and punctuation characters
        chars = string.ascii_lowercase + string.ascii_uppercase + string.punctuation

        # Generate a random password length between min_length and max_length
        password_length = random.randint(RandomPasswordGenerator.min_length, RandomPasswordGenerator.max_length)

        # Generate a random password by randomly selecting a character from the character set
        # and repeating this process until the desired password length is reached
        random_password = "".join(random.choice(chars) for i in range(password_length))

        return random_password
