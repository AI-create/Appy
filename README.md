
# Project Documentation

## Overview

This project automates various tasks using Appium, Celery, SQLite, and FastAPI. The tasks range from mobile automation and data scraping from APIs to APK analysis and creating a FastAPI server that provides real-time communication through WebSockets. The skills demonstrated include:

- **Mobile Automation** using Appium and UIAutomator2.
- **Task Queueing and Scheduling** with Celery.
- **Data Management** with SQLite.
- **WebSocket Communication** using FastAPI for real-time updates.
- **Proxy Handling** to rotate requests for scraping data from APIs.

## Scripts Overview and Purpose

### 1. `start_worker.py`
- **Purpose**: Launches both the FastAPI server and the Celery worker for asynchronous task processing.
- **Details**:
  - Starts the FastAPI server that serves a web dashboard for displaying device info, cryptocurrency data, and APK metadata.
  - Starts a Celery worker to run background tasks such as fetching data from APIs or mobile automation tasks.
- **Key Functionality**: 
  - Uses threading to monitor the FastAPI server and Celery worker processes in real-time.

### 2. `main.py`
- **Purpose**: Acts as the main application, setting up the FastAPI routes, Celery tasks, and database interaction.
- **Details**:
  - Displays real-time data like device information, APK metadata, and cryptocurrency data using FastAPI's web interface.
  - Processes background tasks using Celery for efficient data processing.
- **Key Functionality**:
  - Provides an HTML interface to display device information, battery status, and APK analysis results.
  - Supports WebSocket communication for real-time updates.
  - Launches `mobile_automation.py` as a subprocess to perform mobile automation tasks.

### 3. `uiautomator_deviceinfo.py`
- **Purpose**: Automates device information extraction using UIAutomator2.
- **Details**:
  - Automates interactions with an Android device by scrolling through the settings menu and extracting detailed device information.
- **Key Functionality**:
  - Retrieves information like device model, RAM, processor, and battery level.
  - Saves the extracted device information into `device_info.json`.
  - Schedules the script to run periodically using the `schedule` library.

### 4. `chrome_analysis.py`
- **Purpose**: Analyzes an APK file and extracts metadata such as permissions, activities, and package information.
- **Details**:
  - Uses the `androguard` library to analyze the APK's internal structure and extracts key details.
- **Key Functionality**:
  - Retrieves APK metadata like permissions, version, activities, and services.
  - Stores the extracted metadata in the `apk_metadata.db` SQLite database.

### 5. `zeb.py`
- **Purpose**: Scrapes cryptocurrency data from the ZebPay API using rotating proxies.
- **Details**:
  - Rotates through a list of Indian proxies to make requests to the ZebPay API, which is restricted to Indian IP addresses.
- **Key Functionality**:
  - Uses free proxies to avoid being blocked by the API.
  - Stores the scraped cryptocurrency data in `zebpay_data.db`.
  
**Note**: Free proxies may have inconsistent uptime due to their unreliable nature.

### 6. `mobile_automation.py`
- **Purpose**: Automates user interactions on a mobile app (YouTube) using Appium.
- **Details**:
  - Simulates user interactions like logging in, searching for a video, and submitting a comment.
- **Key Functionality**:
  - Adjusts interactions based on the device’s screen resolution and orientation.
  - Automates the process of logging into the YouTube app, searching for a video, and posting a comment.

## Project Structure

```
Project Root
|
|- main.py                 : Main FastAPI and Celery integration script
|- start_worker.py         : Script to start the FastAPI server and Celery worker
|- mobile_automation.py    : Appium script for automating mobile interactions
|- uiautomator_deviceinfo.py: Script to extract device info using UIAutomator2
|- chrome_analysis.py      : APK analysis using androguard
|- zeb.py                  : Cryptocurrency scraping with proxy rotation
|- requirements.txt        : List of dependencies
|- device_data.db          : SQLite database for device information
|- apk_metadata.db         : SQLite database for APK analysis
|- zebpay_data.db          : SQLite database for crypto data
|- device_info.json        : JSON file storing the extracted device information
```

## Execution Workflow

1. **Start the Project**: Use `start_worker.py` to initiate the FastAPI server and Celery worker.
2. **Device Information Extraction**: Run `uiautomator_deviceinfo.py` to collect and save Android device details.
3. **APK Analysis**: Execute `chrome_analysis.py` to extract and store metadata from an APK file.
4. **Cryptocurrency Data**: Run `zeb.py` to scrape cryptocurrency data from the ZebPay API.
5. **Mobile Automation**: Use `mobile_automation.py` to simulate interactions in the YouTube mobile app using Appium.
6. **Access the Dashboard**: Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) to view device info, APK analysis, and cryptocurrency data in real-time.

## Database Setup

This project uses SQLite databases for persistent data storage:

- `device_data.db`: Stores information about the Android device extracted using `uiautomator_deviceinfo.py`.
- `apk_metadata.db`: Saves APK metadata, including package name, version, permissions, and activities, extracted using `chrome_analysis.py`.
- `zebpay_data.db`: Stores cryptocurrency data scraped from the ZebPay API using `zeb.py`.

## Install Dependencies

To install the required libraries, use:

```
pip install -r requirements.txt
```

Alternatively, manually install the required dependencies:

```
pip install fastapi celery plotly appium uiautomator2 androguard requests schedule
```

## Running the Project

### Activate Virtual Environment:

Ensure you are in the correct virtual environment:

```
source venv/bin/activate  # For Linux/Mac
.env\Scriptsctivate    # For Windows
```

### Start the Celery Worker and FastAPI Server:

Run the following command to start the project:

```
python start_worker.py
```

### Navigate to Dashboard:

Open your web browser and visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to view the real-time dashboard displaying:

- Device information
- APK analysis
- Cryptocurrency data

## Notes on Proxies and API

- **Cryptocurrency Data**: The ZebPay API is restricted to Indian IP addresses, so the project uses free Indian proxies to access the API. Free proxies can be unreliable, and their uptime may vary.
- **Mobile Automation**: Appium is used for simulating interactions with mobile apps. Ensure you have the necessary Android SDKs and Appium setup for this to work correctly.

## Dashboard Details

- **Device Information**: Shows detailed information about the connected Android device, such as the device name, model, processor, RAM, and battery level.
- **Battery Insights**: A real-time graph shows battery levels over time, updated using WebSockets.
- **APK Metadata**: Displays details from the analyzed APK file, including package name, permissions, activities, and services.
- **Cryptocurrency Data**: Lists the most recent cryptocurrency data fetched from the ZebPay API.
