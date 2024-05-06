import logging
from pathlib import Path
import sys
from crontab import CronTab
from config import Config
from utils import probe_device, setup_logging

logger = logging.getLogger(__name__)


def update_cron():
    """Update the cron jobs for the backup devices
    """
    config = Config()
    backup = config["backup"]
    crontab = CronTab(user=True)  
    logger.info("Removing existing bombackup cron jobs")

    script_path = Path(__file__).parent.resolve()

    crontab.remove_all(comment="bombackup")

    for key, device in backup.items():
        probe_device(device["host"])
        logger.info(f"Creating bombackup cron job for {key}")
        job = crontab.new(
        command=f"{sys.executable} {script_path}/backup.py {key}",            
        comment="bombackup"
        )
        job.setall(device.get("cron_schedule"))
    logger.info("Writing crontab")
    crontab.write()
    


def main():
    """Main entry point for the script
    """
    config = Config()
    setup_logging(config)

    update_cron()


if __name__ == "__main__":
    main()
