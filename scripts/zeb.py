import requests
import time
import json
import random
import urllib3
import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# List of Indian proxies to rotate through
proxies = [
    {"https": "http://103.65.202.209:8080"},
    {"https": "http://103.93.193.141:58080"},
    {"https": "http://114.69.225.6:82"},
    {"https": "http://188.208.141.184:1080"},
    {"https": "http://103.156.201.170:83"},
    {"https": "http://103.163.244.206:83"},
    {"https": "http://14.142.36.210:1111"},
    {"https": "http://103.255.147.102:83"},
    {"https": "http://103.179.46.49:6789"},
    {"https": "http://103.69.21.192:58080"}
]

# ZebPay API endpoint (replace with actual endpoint)
zebpay_api_url = "https://www.zebapi.com/pro/v1/market/"

# Number of max retries for failed proxies
MAX_RETRIES = 2

# Delay between requests (in seconds)
DELAY_BETWEEN_REQUESTS = 5

# Number of requests allowed per proxy
MAX_REQUESTS_PER_PROXY = 10

# File to save the successful scraped data
output_json_file = "zebpay_data.json"

# Mobile User-Agent Header
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G950F Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36'
}

# Function to save scraped data to the JSON file immediately
def save_data_immediately(data):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["timestamp"] = timestamp  # Add timestamp for better tracking
        with open(output_json_file, 'a') as outfile:
            json.dump(data, outfile, indent=4)
            outfile.write("\n")  # Newline for better readability
            print(f"Data saved to {output_json_file} at {timestamp}")
    except Exception as e:
        print(f"Error while saving the data: {str(e)}")

# Function to make a request using a proxy
def make_request(proxy, url, retries=0):
    try:
        print(f"Using proxy: {proxy}")
        response = requests.get(url, proxies=proxy, headers=headers, timeout=30, verify=False)
        response.raise_for_status()

        # Check if response is JSON
        if 'application/json' in response.headers.get('Content-Type', ''):
            response_json = response.json()
            print(f"JSON Response from {url}: {response_json}")

            # Save the successful request along with proxy IP details
            data = {
                "proxy": proxy,
                "url": url,
                "response": response_json
            }

            # Immediately save to file
            save_data_immediately(data)
            return True
        else:
            print(f"Non-JSON response from {url}: {response.text}")
            return False

    except requests.RequestException as e:
        print(f"Error with {proxy}, skipping...: {str(e)}")
        if retries < MAX_RETRIES:
            print(f"Retrying... (Attempt {retries + 1}/{MAX_RETRIES})")
            return make_request(proxy, url, retries=retries + 1)
        return False

# Main function to rotate proxies and make requests
def rotate_proxies_and_scrape():
    # Dictionary to track requests made per proxy
    request_count = {proxy["https"]: 0 for proxy in proxies}

    while any(count < MAX_REQUESTS_PER_PROXY for count in request_count.values()):
        random.shuffle(proxies)  # Shuffle the proxies list to randomize selection
        for proxy in proxies:
            proxy_key = proxy["https"]
            if request_count[proxy_key] >= MAX_REQUESTS_PER_PROXY:
                print(f"Max requests reached for {proxy}, moving to next proxy.")
                continue

            success = make_request(proxy, zebpay_api_url)
            if success:
                request_count[proxy_key] += 1

            # Delay between requests to prevent overwhelming the proxy or server
            time.sleep(DELAY_BETWEEN_REQUESTS)

            # Break the loop if we've reached the max requests for this proxy
            if request_count[proxy_key] >= MAX_REQUESTS_PER_PROXY:
                break

# Entry point for the script
if __name__ == "__main__":
    rotate_proxies_and_scrape()
