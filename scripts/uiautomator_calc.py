import uiautomator2 as u2
import time

# Connect to the Android device
device = u2.connect()  # Automatically connect to the first available device

# Verify connection
if device.info:
    print("Device connected successfully!")
else:
    raise ConnectionError("Failed to connect to device")

# Launch the Calculator app
app_package = "com.miui.calculator"
device.app_start(app_package)
print(f"App {app_package} launched successfully!")

# Wait for the app to load
time.sleep(2)

# Wait for the digit '2' button and click
if device(resourceId="com.miui.calculator:id/btn_2_s").wait(timeout=5):
    device(resourceId="com.miui.calculator:id/btn_2_s").click()  # Click '2'
else:
    raise Exception("Button '2' not found")

# Wait for the '+' button and click
if device(resourceId="com.miui.calculator:id/btn_plus_s").wait(timeout=5):
    device(resourceId="com.miui.calculator:id/btn_plus_s").click()  # Click '+'
else:
    raise Exception("Button '+' not found")

# Wait for the digit '3' button and click
if device(resourceId="com.miui.calculator:id/btn_3_s").wait(timeout=5):
    device(resourceId="com.miui.calculator:id/btn_3_s").click()  # Click '3'
else:
    raise Exception("Button '3' not found")

# Wait for the '=' button and click
if device(resourceId="com.miui.calculator:id/btn_equal_s").wait(timeout=5):
    device(resourceId="com.miui.calculator:id/btn_equal_s").click()  # Click '='
else:
    raise Exception("Button '=' not found")

# Extract the result (Adjust the resourceId if needed for the result field)
result = device(resourceId="com.miui.calculator:id/expression").get_text()
print(f"Calculation Result: {result}")

# Close the Calculator app after task completion
device.app_stop(app_package)
print("App closed.")
