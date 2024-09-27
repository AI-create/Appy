import uiautomator2 as u2
import time

# Connect to the Android device
device = u2.connect('emulator-5554')  # Automatically connect to the first available device

# Verify connection
if device.info:
    print("Device connected successfully!")
else:
    raise ConnectionError("Failed to connect to device")

# Launch Google Chrome
app_package = "com.android.chrome"
device.app_start(app_package)
print(f"App {app_package} launched successfully!")

# Wait for Chrome to load
time.sleep(3)

# Click on the URL bar using its resource ID
if device(resourceId="com.android.chrome:id/search_box_text").exists:
    device(resourceId="com.android.chrome:id/search_box_text").click()
    print("Search box found! Entering URL...")
else:
    raise Exception("Search or type URL box not found")

# Wait for the search field to focus
time.sleep(2)

# Directly set the URL text without clipboard
device(resourceId="com.android.chrome:id/url_bar").set_text("https://www.google.com")
print("URL typed in successfully")

# Press the "Enter" key to submit the URL
device.press("enter")  # Simulate pressing "Enter"
print("Navigated to Google.com")

# Wait for the page to load
time.sleep(5)

# Extract the URL from the URL bar to verify navigation
url = device(resourceId="com.android.chrome:id/url_bar").get_text()
print(f"Current URL: {url}")

# Optional: Close Chrome
device.app_stop(app_package)
print("App closed.")
