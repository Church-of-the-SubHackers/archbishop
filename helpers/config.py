import os

from dotenv import load_dotenv, find_dotenv


class Config:
    """
    Implements methods that abstracts interaction with configuration files
    and provides a contract for accessing configuration variables that is
    agnostic to changing in the format of configurations.

    Attributes
    ----------

    Methods
    -------
    get(key)
        Gets a configuration variable
    """

    def __init__(self):
        """
        Placeholder for future initialization tasks like taking in a path to
        a configuration file.
        """

    def load_config(self):
        load_dotenv(find_dotenv(usecwd=True))

    # @classmethod
    def get(self, key):
        """Gets a configuration variable

        Retrieves the value of a configuration variable. Currently uses
        environment variables but this is subject to change.

        Parameters
        ----------
        key : str
            The name, or key of a key/value pair in the configuration

        Raises
        ------
        ValueError
            If no key was passed as a parameter
        """
        if not isinstance(key, str):
            print("Key was not string")
            raise ValueError("Key must be a string")
        elif key == "":
            print("Key was empty")
            raise ValueError("Key cannot be empty")

        return os.getenv(key)
