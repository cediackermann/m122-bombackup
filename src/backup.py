import os
import logging
from argparse import ArgumentParser
from paramiko import SSHClient
from scp import SCPClient
from tempfile import gettempdir
from datetime import datetime
from tarfile import TarFile
import shutil
import boto3

from utils import id_generator, setup_logging, send_email
from config import Config


logger = logging.getLogger(__name__)


def main(key: str):
    config = Config()
    setup_logging(config)

    backup = config["backup"]
    device = backup.get(key)

    if not device:
        raise ValueError(f"Device {key} not found in configuration")

    # Format as: {device_name}_{datetime}_{unique_id}
    backup_name = (
        f"{key}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{id_generator()}"
    )
    backup_location = f"{gettempdir()}/{backup_name}"

    # Transfer files
    if device["type"] == "scp":
        with SSHClient() as ssh:
            try:
                ssh.load_system_host_keys()
                ssh.connect(
                    device["host"],
                    username=device["user"],
                    password=device["password"],
                )

                transport = ssh.get_transport()

                if not transport:
                    send_email("Backup failed", "Could not get transport", config["email"]["email_address"])
                    raise ValueError("Could not get transport")

                with SCPClient(transport) as scp:
                    scp.get(
                        device["remote_dir"],
                        local_path=backup_location,
                        recursive=True,
                        preserve_times=True,
                    )
            except Exception as e:
                logger.error(f"Failed to transfer files: {e}")
                send_email("Backup failed", f"Failed to transfer files: {e}", config["email"]["email_address"])
                return
    else:
        send_email("Backup failed", "Backup type not supported", config["email"]["email_address"])
        raise ValueError("Backup type not supported")

    # Compress files
    with TarFile.open(f"{backup_location}.tar.gz", "w:gz") as tar:
        tar.add(backup_location, arcname=backup_name)
        
    
    # Upload to S3
    client = boto3.client(
        's3',
        aws_access_key_id=config["storage"]["access_key"],
        aws_secret_access_key=config["storage"]["secret_key"],
    )
    
    try:
        response = client.upload_file(f"{backup_location}.tar.gz", config["storage"]["bucket"], f"{backup_name}.tar.gz")
    except Exception as e:
        logger.error(f"Failed to upload backup to S3: {e}")
        send_email("Backup failed", f"Failed to upload backup to S3: {e}", config["email"]["email_address"])
        return

    logger.info(f"Backup {backup_name} completed successfully")


if __name__ == "__main__":
    config = Config()

    parser = ArgumentParser(prog="Bombackup")
    parser.add_argument(
        "device", help="The device key to backup", choices=config["backup"].keys()
    )

    args = parser.parse_args()

    main(args.device)
