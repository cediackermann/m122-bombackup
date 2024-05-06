import toml
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class Config:
    config_file = "config.toml"

    def __init__(self, config_file=None):
        """Initialize the Config class

        Raises:
            FileNotFoundError: If the config file is not found
        """
        self.config_file = config_file or self.config_file

        script_path = Path(__file__).parent.resolve()

        self.config_file = os.path.abspath(
            os.path.join(str(script_path), "..", self.config_file)
        )

        if not os.path.isfile(self.config_file):
            raise FileNotFoundError(f"Config file not found: {self.config_file}")

    def __getitem__(self, key):
        """Get a config value by key

        Returns:
            str: The value of the key
        """
        logger.info(f"Reading config key: {key}")
        parts = key.split(".")
        with open(self.config_file) as f:
            config = toml.load(f)
            for part in parts:
                config = config[part]
            return config
