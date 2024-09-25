# scripts/celery_worker.py
from celery import Celery
import subprocess

celery = Celery(
    "celery_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery.task(bind=True)
def fetch_battery_info(self):
    try:
        # Run the UIAutomator script to get device info and battery level
        subprocess.run(["python", "scripts/uiautomator_deviceinfo.py"], check=True)
    except Exception as exc:
        self.retry(exc=exc, countdown=60)  # Retry in 60 seconds if it fails
