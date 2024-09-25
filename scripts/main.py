import json
import os
import matplotlib.pyplot as plt
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import io
from datetime import datetime

# Path to the JSON file containing the device info
JSON_FILE_PATH = 'C:/Appy/scripts/device_info.json'

app = FastAPI()

# Helper function to load JSON data
def load_device_info():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r') as f:
            return json.load(f)
    return []

# Endpoint to fetch device info and dynamic battery graph
@app.get("/device_with_battery_graph")
def get_device_with_battery_graph():
    device_data = load_device_info()
    if not device_data:
        raise HTTPException(status_code=404, detail="No device information found")

    # Get the latest device info (most recent entry)
    latest_device_info = device_data[-1]

    # Extract battery level and timestamps for the graph
    timestamps = []
    battery_levels = []
    for entry in device_data:
        timestamps.append(entry.get("Timestamp"))
        battery_levels.append(int(entry.get("Battery level", 0)))

    # Create the plot dynamically
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot battery level over time
    ax.plot(timestamps, battery_levels, marker='o', linestyle='-', color='b', label='Battery Level')

    # Format the x-axis to show datetime labels
    ax.set_xlabel("Timestamp", fontsize=12)
    ax.set_ylabel("Battery Level (%)", fontsize=12)
    ax.set_title("Battery Level Over Time", fontsize=16)
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels

    # Add a grid for better visualization
    ax.grid(True)

    # Add a box with device info at the top left
    device_info_str = (
        f"Device: {latest_device_info.get('Device name', 'N/A')}\n"
        f"Model: {latest_device_info.get('Model', 'N/A')}\n"
        f"Processor: {latest_device_info.get('Processor', 'N/A')}\n"
        f"RAM: {latest_device_info.get('RAM', 'N/A')}\n"
        f"Storage: {latest_device_info.get('Storage', 'N/A')}\n"
        f"Android version: {latest_device_info.get('Android version', 'N/A')}"
    )

    # Place the device info as a text box in the plot
    plt.text(0.05, 0.95, device_info_str, transform=ax.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="lightyellow"))

    # Ensure the plot fits well
    plt.tight_layout()

    # Save the plot to a BytesIO stream and return it as an image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)  # Close the figure to free memory

    return StreamingResponse(buf, media_type="image/png")

