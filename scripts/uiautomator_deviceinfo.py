import uiautomator2 as u2
import time
import json
from datetime import datetime
import schedule

# Function to run the automation script
def run_automation_script():
    # Connect to the Android device
    device = u2.connect('c26d8eaa')  # Automatically connect to the first available device

    # Verify connection
    if device.info:
        print("Device connected successfully!")
    else:
        raise ConnectionError("Failed to connect to device")

    # Launch Settings
    app_package = "com.android.settings"
    device.app_start(app_package)
    print(f"App {app_package} launched successfully!")

    # Wait for the app to load
    time.sleep(2)

    # Path to save the JSON file
    json_file_path = 'device_info.json'

    # Dictionary to store extracted data
    device_info = {}

    try:
        print("Attempting to find and click on 'About device'")

        # Scroll to About device and click it
        if device(scrollable=True).scroll.to(text="About device"):
            time.sleep(1)  # Stabilize the page
            device(text="About device").click()
            print("Successfully clicked on 'About device'")
        else:
            raise Exception("'About device' not found during scroll")

        # Adding time to ensure the page loads completely
        time.sleep(3)

        # Extract visible text elements
        print("Extracting device information:")
        text_elements = [element.get_text().strip() for element in device(className="android.widget.TextView")]

        # Helper function to handle key-value pairs and multi-line entries
        def pair_key_value(elements):
            info = {}
            i = 0
            while i < len(elements):
                key = elements[i]
                if i + 1 < len(elements):
                    value = elements[i + 1]
                    if ":" in key or key.endswith(":"):
                        # If a key appears with a colon or ends with a colon, skip it
                        i += 1
                        continue
                    if value in ["Front", "Rear"]:
                        # Handle special case for Cameras
                        camera_type = value
                        if i + 2 < len(elements):
                            camera_value = elements[i + 2]
                            info[f"Cameras {camera_type}"] = camera_value
                            i += 3
                        else:
                            i += 2
                    else:
                        # General key-value extraction
                        info[key] = value
                        i += 2
                else:
                    i += 1
            return info

        # Process the extracted text elements
        device_info = pair_key_value(text_elements)

        # Get the current battery level
        battery_info = device.shell('dumpsys battery | grep level').output.strip().split(": ")
        if len(battery_info) > 1:
            battery_level = battery_info[1]
        else:
            battery_level = "N/A"
        device_info["Battery level"] = battery_level

        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        device_info["Timestamp"] = timestamp

        # Print the extracted information in the terminal
        print("\nDevice Information:")
        for key, value in device_info.items():
            print(f"{key}: {value}")

        # Load existing data from the JSON file, if any
        try:
            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)

                # If the data is a dictionary (from earlier runs), convert it to a list
                if isinstance(data, dict):
                    data = [data]

        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        # Append the new device info to the list
        data.append(device_info)

        # Save the updated list to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

        print("\nDevice information saved to 'device_info.json'")

    except Exception as e:
        print(f"Error: {e}")

    # Close the Settings app
    device.app_stop(app_package)
    print("App closed.")

# Run the automation script immediately at startup
run_automation_script()

# Schedule the script to run every 1 minute
schedule.every(1).minutes.do(run_automation_script)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
