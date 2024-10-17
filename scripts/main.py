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
    broker="redis://localhost:6379/0", 
    backend="redis://localhost:6379/0",  
)

# Paths
json_file_path = os.path.join(os.getcwd(), 'device_info.json')
ddb_path = os.path.join(os.getcwd(), 'device_data.db')
adb_path = os.path.join(os.getcwd(), 'apk_metadata.db')
crypto_db_path = os.path.join(os.getcwd(), 'zebpay_data.db')  # Crypto data DB path

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

# APK metadata table function
def get_latest_apk_metadata():
    try:
        conn = sqlite3.connect(adb_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM apk_metadata ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        if row:
            return {
                'package_name': row[1],
                'version': row[2],
                'permissions': row[3],
                'activities': row[4],
                'services': row[5],
                'receivers': row[6],
                'providers': row[7],
                'files': row[8],
                'timestamp': row[9]
            }
        else:
            return {}
    except sqlite3.Error as e:
        print(f"Error fetching data from APK metadata: {e}")
    finally:
        conn.close()

# Function to fetch cryptocurrency data from SQLite
def get_crypto_data():
    try:
        conn = sqlite3.connect(crypto_db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM zebpay_data ORDER BY id DESC LIMIT 10')
        rows = cursor.fetchall()
        crypto_data = []
        for row in rows:
            crypto_data.append({
                'market': row[1],
                'volumeEx': row[2],
                'volumeQt': row[3],
                'pricechange': row[4],
                'quickTradePrice': row[5],
                'pair': row[6],
                'virtualCurrency': row[7],
                'currency': row[8],
                'volume': row[9]
            })
        return crypto_data
    except sqlite3.Error as e:
        print(f"Error fetching cryptocurrency data: {e}")
        return []
    finally:
        conn.close()

# Initialize the database on startup
init_db()

# HTML Template for displaying device information, battery insights, APK analysis, and crypto data
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Device Information, Battery Insights, APK Analysis, and Cryptocurrency Data</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        h1, h2 {{ color: #2c3e50; }}
        .container {{ width: 80%; margin: 0 auto; }}
        .info-box, .table-box {{ border: 1px solid #ddd; padding: 10px; margin-bottom: 20px; background-color: #f9f9f9; }}
        .graph-box {{ text-align: center; margin-bottom: 20px; }}
        #batteryGraph {{ max-width: 100%; height: auto; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ text-align: left; padding: 8px; border: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        td {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
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

        <h2>APK Analysis</h2>
        <div class="table-box">
            <table>
                <tr>
                    <th>Package Name</th>
                    <th>Version</th>
                    <th>Permissions</th>
                    <th>Activities</th>
                    <th>Services</th>
                    <th>Receivers</th>
                    <th>Providers</th>
                    <th>Files</th>
                    <th>Timestamp</th>
                </tr>
                <tr>
                    <td>{package_name}</td>
                    <td>{version}</td>
                    <td>{permissions}</td>
                    <td>{activities}</td>
                    <td>{services}</td>
                    <td>{receivers}</td>
                    <td>{providers}</td>
                    <td>{files}</td>
                    <td>{timestamp}</td>
                </tr>
            </table>
        </div>

        <h2>Cryptocurrency Data</h2>
        <div class="table-box">
            <table>
                <tr>
                    <th>Market</th>
                    <th>VolumeEx</th>
                    <th>VolumeQt</th>
                    <th>Price Change</th>
                    <th>Quick Trade Price</th>
                    <th>Pair</th>
                    <th>Virtual Currency</th>
                    <th>Currency</th>
                    <th>Volume</th>
                </tr>
                {crypto_rows}
            </table>
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

# Endpoint to get the device info, battery insights, APK analysis, and cryptocurrency data
@app.get("/", response_class=HTMLResponse)
async def get_device_info():
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        latest_entry = data[-1] if isinstance(data, list) else data

        insert_into_db(latest_entry)

        about_device = latest_entry.get("About device", "N/A")
        device_name = latest_entry.get("Device name", "N/A")
        model = latest_entry.get("Model", "N/A")
        processor = latest_entry.get("Processor", "N/A")
        ram = latest_entry.get("RAM", "N/A")
        battery_capacity = latest_entry.get("Battery capacity", "N/A")

        # Get APK metadata
        apk_metadata = get_latest_apk_metadata()

        # Get cryptocurrency data
        crypto_data = get_crypto_data()

        crypto_rows = ''.join([
            f"<tr><td>{row['market']}</td><td>{row['volumeEx']}</td><td>{row['volumeQt']}</td><td>{row['pricechange']}</td><td>{row['quickTradePrice']}</td><td>{row['pair']}</td><td>{row['virtualCurrency']}</td><td>{row['currency']}</td><td>{row['volume']}</td></tr>"
            for row in crypto_data
        ])

        html_content = html_template.format(
            about_device=about_device,
            device_name=device_name,
            model=model,
            processor=processor,
            ram=ram,
            battery_capacity=battery_capacity,
            package_name=apk_metadata.get("package_name", "N/A"),
            version=apk_metadata.get("version", "N/A"),
            permissions=apk_metadata.get("permissions", "N/A"),
            activities=apk_metadata.get("activities", "N/A"),
            services=apk_metadata.get("services", "N/A"),
            receivers=apk_metadata.get("receivers", "N/A"),
            providers=apk_metadata.get("providers", "N/A"),
            files=apk_metadata.get("files", "N/A"),
            timestamp=apk_metadata.get("timestamp", "N/A"),
            crypto_rows=crypto_rows  # Adding the crypto rows here
        )

        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        try:
            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)

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
                await asyncio.sleep(60) 
                continue  

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

# Start the mobile automation script as a subprocess
def run_mobile_automation():
    subprocess.Popen([sys.executable, "mobile_automation.py"])

def run_uiautomator_deviceinfo():
    subprocess.Popen([sys.executable, "uiautomator_deviceinfo.py"])

def run_zeb():
    subprocess.Popen([sys.executable, "zeb.py"])


if __name__ == "__main__":
    run_mobile_automation()  # Launch mobile automation as a subprocess
    run_uiautomator_deviceinfo()  # Launch uiautomator_deviceinfo as a subprocess
    run_zeb() # Launch zebpay crypto script as a subprocess
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
