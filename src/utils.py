import logging
from ping3 import ping
import string
import random
import courier
from config import Config

from courier.client import Courier
from courier.core import ApiError


logger = logging.getLogger(__name__)


def probe_device(host):
    """Probe a device to check if it is reachable

    Args:
        host (str): The IP address of the device

    Returns:
        bool: True if the device is reachable, False otherwise
    """
    logger.info(f"Probing device {host}")
    duration = ping(host, timeout=1)
    if duration is None:
        logger.warn(f"Device {host} is not reachable")
        send_email(
            subject="Device unreachable",
            body=f"Device {host} is unreachable",
            recipient="ackermanncedi@gmail.com",
        )
        return False
    if duration > 1:
        logger.warn(f"Device {host} is reachable but slow ({duration} s)")
        return True
    logger.info(f"Device {host} is reachable")
    return True


def setup_logging(config):
    """Setup the logging configuration

    Args:
        config (str): The configuration object

    Raises:
        ValueError: if the log level is not a string
        ValueError: if the log file is not a string
    """
    level = config["logging.log_level"]
    if type(level) is not str:
        raise ValueError("Log level must be a string")
    log_file = config["logging.log_file"]
    if type(log_file) is not str:
        raise ValueError("Log file must be a string")
    logging.basicConfig(filename=log_file, level=level)
    
    
def send_email(subject, body, recipient):
    """Send an email using the Courier API

    Args:
        subject (str): Subject of the email
        body (str): Body of the email
        recipient (str): Email address of the recipient
    """
    config = Config()
    logger.info(f"Sending email to {recipient}")
    client = Courier(
        authorization_token=config["email.courier_token"]
    )
    try:
        emailResponse = client.send(
            message=courier.ContentMessage(
                to=courier.UserRecipient(
                    email=config["email.email_address"],
                ),
                content=courier.ElementalContentSugar(
                    title=subject,
                    body=body,
                ),
                routing=courier.Routing(method="all", channels=["inbox", "email"]),
            )
        )
    except ApiError as e:
        logger.error(f"Failed to send email: {e}")



# Credit: https://stackoverflow.com/a/2257449
def id_generator(size=8, chars=string.ascii_lowercase + string.digits):
    """Generate a random string

    Args:
        size (int, optional): length of random string . Defaults to 8.
        chars (_type_, optional): range of characters for random string . Defaults to string.ascii_lowercase+string.digits.

    Returns:
        str: random string
    """
    return "".join(random.choice(chars) for _ in range(size))
