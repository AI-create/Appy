
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Appium options
options = UiAutomator2Options()
options.platform_name = 'Android'
options.udid = 'emulator-5554'
options.app_package = 'com.google.android.youtube'
options.app_activity = 'com.google.android.youtube.app.honeycomb.Shell$HomeActivity'
options.device_name = 'Pixel_4_API_33'
options.automation_name = 'UiAutomator2'
options.platformVersion = '13'
options.auto_grant_permissions = True
options.adb_exec = 'C:/Users/Asus-2022/AppData/Local/Android/Sdk/platform-tools/adb.exe'

# Initialize Appium driver
driver = webdriver.Remote('http://127.0.0.1:4723', options=options)

# Function to handle screen orientation change
def handle_orientation():
    current_orientation = driver.orientation
    if current_orientation == 'LANDSCAPE':
        driver.orientation = 'PORTRAIT'
    else:
        driver.orientation = 'LANDSCAPE'

# Function to adjust based on screen size (example handling different sizes)
def adjust_for_screen_resolution():
    screen_size = driver.get_window_size()
    width = screen_size['width']
    height = screen_size['height']
    
    if width < 1080 or height < 1920:
        print("Low-resolution device detected, adjusting interactions.")
    else:
        print("Standard resolution, proceeding as usual.")

# Simulate login process
def simulate_login():
    try:
        # Try locating the sign-in button first using ACCESSIBILITY_ID, fallback to XPATH if necessary
        try:
            login_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Sign in"))
            )
        except:
            login_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.Button[@text='Sign in']"))
            )
        login_button.click()

        # Enter email
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.EditText[@text='Email or phone']"))
        )
        email_field.send_keys("your-email@gmail.com")

        # Click next
        next_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.Button[@text='Next']"))
        )
        next_button.click()

        # Enter password
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.EditText[@text='Enter your password']"))
        )
        password_field.send_keys("your-password")

        # Click next to submit password
        login_submit_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.Button[@text='Next']"))
        )
        login_submit_button.click()

    except Exception as e:
        print(f"Login process failed: {e}")

# Navigate the app after login
def navigate_and_search():
    try:
        # Click on the search icon
        search_icon = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Search"))
        )
        search_icon.click()

        # Type in the search bar
        search_bar = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.ID, "com.google.android.youtube:id/search_edit_text"))
        )
        search_bar.send_keys("Rick Rolled (Short Version)")

        # Select search suggestion
        new_xpath = '//android.widget.TextView[@text="rick rolled (short version)"]'
        search_suggestion = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.XPATH, new_xpath))
        )
        search_suggestion.click()

    except Exception as e:
        print(f"Search navigation failed: {e}")

# Simulate data submission: Posting a comment
def submit_comment():
    try:
        # Click on the video from search result
        title_xpath = '//android.view.ViewGroup[contains(@content-desc, "Rick Rolled (Short Version)")]'
        search_result = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.XPATH, title_xpath))
        )
        search_result.click()

        # Scroll down to comments section
        driver.swipe(500, 1500, 500, 500)

        # Click on comment section
        comment_section = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Add a public comment…"))
        )
        comment_section.click()

        # Type a comment
        comment_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.ID, "com.google.android.youtube:id/comment_edit_text"))
        )
        comment_field.send_keys("This is an automated comment!")

        # Submit the comment
        submit_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.Button[@text='Comment']"))
        )
        submit_button.click()

    except Exception as e:
        print(f"Comment submission failed: {e}")

# Execute the steps
adjust_for_screen_resolution()
handle_orientation()
navigate_and_search()  # Simulates navigation after login
simulate_login()  # Simulates logging into the YouTube app
submit_comment()  # Simulates submitting a comment

# Close the driver at the end
driver.quit()
