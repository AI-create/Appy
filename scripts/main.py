import subprocess
import os
import json
import sqlite3
import plotly.graph_objs as go
import plotly.io as pio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
import sys
import asyncio
from celery import Celery
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

# FastAPI app setup
app = FastAPI()

# Celery app setup
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",  # Redis as the message broker
    backend="redis://localhost:6379/0",  # Redis as the result backend
)

# Path to the JSON file in the C:\Appy\scripts directory
json_file_path = os.path.join(os.getcwd(), 'device_info.json')

# Path to the SQLite database
ddb_path = os.path.join(os.getcwd(), 'device_data.db')

adb_path = os.path.join(os.getcwd(), 'apk_metadata.db')

# Create and initialize SQLite database table for device information
def init_db():
    try:
        conn = sqlite3.connect(ddb_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            about_device TEXT,
            device_name TEXT,
            model TEXT,
            processor TEXT,
            ram TEXT,
            battery_capacity TEXT,
            battery_level INTEGER,
            timestamp TEXT
        )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

# Function to insert data into SQLite
def insert_into_db(data):
    try:
        conn = sqlite3.connect(ddb_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO device_info (about_device, device_name, model, processor, ram, battery_capacity, battery_level, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get("About device", "N/A"),
            data.get("Device name", "N/A"),
            data.get("Model", "N/A"),
            data.get("Processor", "N/A"),
            data.get("RAM", "N/A"),
            data.get("Battery capacity", "N/A"),
            int(data.get("Battery level", 0)),
            data.get("Timestamp", "N/A")
        ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting data into database: {e}")
    finally:
        conn.close()

# Initialize the database on startup
init_db()

# Celery task to fetch data and insert it into SQLite
@celery_app.task(bind=True, retry_backoff=10, max_retries=5)
def fetch_and_store_data(self):
    try:
        # Read JSON file and insert data into SQLite
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        # Insert each entry into the database
        for entry in data:
            insert_into_db(entry)
        
        print("Data inserted successfully into the database.")
        return "Success"

    except Exception as exc:
        # Retry the task if it fails
        raise self.retry(exc=exc)


# HTML Template for displaying device information and battery insights
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Device Information and Battery Insights</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        h1, h2 {{ color: #2c3e50; }}
        .container {{ width: 80%; margin: 0 auto; }}
        .info-box {{ border: 1px solid #ddd; padding: 10px; margin-bottom: 20px; background-color: #f9f9f9; }}
        .graph-box {{ text-align: center; }}
        #batteryGraph {{ max-width: 100%; height: auto; }}
    </style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>Device Information</h1>
        <div class="info-box">
            <p><strong>About device:</strong> {about_device}</p>
            <p><strong>Device Name:</strong> {device_name}</p>
            <p><strong>Model:</strong> {model}</p>
            <p><strong>Processor:</strong> {processor}</p>
            <p><strong>RAM:</strong> {ram}</p>
            <p><strong>Battery Capacity:</strong> {battery_capacity}</p>
        </div>
        
        <h2>Battery Insights</h2>
        <div class="graph-box">
            <div id="batteryGraph"></div>
        </div>
    </div>
    <script>
        var ws = new WebSocket("ws://localhost:8000/ws");

        // Variables to store the current zoom state
        var currentXRange = null;
        var currentYRange = null;

        ws.onmessage = function(event) {{
            var data = JSON.parse(event.data);

            // Initialize the graph only once
            if (!currentXRange && !currentYRange) {{
                Plotly.newPlot('batteryGraph', data.data, {{
                    title: 'Battery Level Over Time',
                    hovermode: 'closest',
                    xaxis: {{
                        title: 'Time',
                        tickangle: 45,
                    }},
                    yaxis: {{
                        title: 'Battery Level (%)'
                    }},
                }});
            }} else {{
                // Update data while preserving the zoom state
                Plotly.update('batteryGraph', data.data, {{
                    xaxis: {{ range: currentXRange }},
                    yaxis: {{ range: currentYRange }},
                }});
            }}

            var graphDiv = document.getElementById('batteryGraph');

            // Save the zoom/pan state on interaction (e.g., zoom or pan)
            graphDiv.on('plotly_relayout', function(eventData) {{
                currentXRange = eventData['xaxis.range'] || currentXRange;
                currentYRange = eventData['yaxis.range'] || currentYRange;
            }});

            // Double-click to reset zoom to the original state
            graphDiv.on('plotly_doubleclick', function(eventData) {{
                currentXRange = null;
                currentYRange = null;
                Plotly.relayout('batteryGraph', {{
                    'xaxis.autorange': true,
                    'yaxis.autorange': true
                }});
            }});
        }};
    </script>
</body>
</html>
"""

# Lifespan event handler to manage subprocess
@asynccontextmanager
async def lifespan(app: FastAPI):
    processes = []

    try:
        # Path to the Python executable
        python_executable = sys.executable

        # Define the scripts to run
        scripts_to_run = [
            r'C:\Appy\scripts\uiautomator_deviceinfo.py',
            r'C:\Appy\scripts\zeb.py',
            r'C:\Appy\scripts\chrome_analysis.py'
        ]

        # Launch each script as a subprocess
        for script in scripts_to_run:
            try:
                process = subprocess.Popen([python_executable, script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                processes.append(process)
                print(f"Started {script} successfully!")

            except Exception as e:
                print(f"Error starting {script}: {e}")

    except Exception as e:
        print(f"Error during subprocess initialization: {e}")

    yield

    # Terminate all subprocesses on shutdown
    for process in processes:
        if process.poll() is None:  # Check if process is still running
            process.terminate()
            print(f"Terminated subprocess: {process.args}")

app = FastAPI(lifespan=lifespan)

# Endpoint to get the device info and battery insights
@app.get("/", response_class=HTMLResponse)
async def get_device_info():
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        latest_entry = data[-1] if isinstance(data, list) else data

        # Insert the data into the database
        insert_into_db(latest_entry)

        about_device = latest_entry.get("About device", "N/A")
        device_name = latest_entry.get("Device name", "N/A")
        model = latest_entry.get("Model", "N/A")
        processor = latest_entry.get("Processor", "N/A")
        ram = latest_entry.get("RAM", "N/A")
        battery_capacity = latest_entry.get("Battery capacity", "N/A")

        html_content = html_template.format(
            about_device=about_device,
            device_name=device_name,
            model=model,
            processor=processor,
            ram=ram,
            battery_capacity=battery_capacity
        )

        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

# WebSocket endpoint for live updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        try:
            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)

            # Filter data for only the past 2 hours
            current_time = datetime.now()
            two_hours_ago = current_time - timedelta(hours=24)

            filtered_data = [
                entry for entry in data
                if datetime.strptime(entry["Timestamp"], "%Y-%m-%d %H:%M:%S") >= two_hours_ago
            ]

            timestamps = [entry["Timestamp"] for entry in filtered_data]
            battery_levels = [int(entry["Battery level"]) for entry in filtered_data]

            if len(timestamps) == 0 or len(battery_levels) == 0:
                print("No data for the past 2 hours, waiting for current data...")
                await asyncio.sleep(60)  # Wait for 1 minute and retry
                continue  # Retry the loop to check for new data

            # Prepare Plotly trace for the graph
            trace = go.Scatter(
                x=timestamps,
                y=battery_levels,
                mode='lines+markers',
                name='Battery Level',
                marker=dict(color='blue'),
                hoverinfo='x+y',
                line=dict(shape='linear')
            )

            layout = go.Layout(
                title="Battery Level Over Time (Past 2 Hours)",
                xaxis=dict(title='Time', tickangle=45),
                yaxis=dict(title='Battery Level (%)'),
                hovermode='closest'
            )

            figure_json = pio.to_json({'data': [trace], 'layout': layout})

            await websocket.send_text(figure_json)

            await asyncio.sleep(5)

        except Exception as e:
            print(f"WebSocket Error: {e}")
            await websocket.close()
            break

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
