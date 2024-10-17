import subprocess
import sys
import time
import threading

def stream_output(process, name):
    """Stream output from the process to monitor logs in real-time."""
    for line in iter(process.stdout.readline, b''):
        print(f"[{name}] {line.decode().strip()}")
    process.stdout.close()

def start_processes():
    # Start FastAPI server
    fastapi_process = subprocess.Popen(
        [sys.executable, "main.py"], 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    print("FastAPI server started...")

    # Start Celery worker
    celery_process = subprocess.Popen(
        ["celery", "-A", "main.celery_app", "worker", "--loglevel=info"], 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    print("Celery worker started...")

    # Return both processes
    return fastapi_process, celery_process

def monitor_processes(fastapi_process, celery_process):
    """Monitor FastAPI and Celery processes in parallel."""
    fastapi_thread = threading.Thread(target=stream_output, args=(fastapi_process, "FastAPI"), daemon=True)
    celery_thread = threading.Thread(target=stream_output, args=(celery_process, "Celery"), daemon=True)

    fastapi_thread.start()
    celery_thread.start()

    return fastapi_thread, celery_thread

if __name__ == "__main__":
    fastapi_process, celery_process = start_processes()
    fastapi_thread, celery_thread = monitor_processes(fastapi_process, celery_process)

    try:
        # Keep `start_worker.py` running until manually terminated
        while True:
            time.sleep(10)  # Adjust sleep time as necessary
    except KeyboardInterrupt:
        print("Shutting down...")

        # Terminate both processes when the script is interrupted
        fastapi_process.terminate()
        celery_process.terminate()

        # Wait for processes to terminate properly
        fastapi_process.wait()
        celery_process.wait()

        print("Processes terminated successfully.")
