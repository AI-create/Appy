import requests
import time
import json
import random
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# List of proxies to rotate through
proxies = [
    {"https": "http://85.210.121.11:8080"},
    {"https": "http://20.26.249.29:8080"},
    {"https": "http://211.104.20.205:8080"},
    {"https": "http://116.99.173.71:8118"},
    {"https": "http://40.76.69.94:8080"},
    {"https": "http://3.230.127.137:3128"},
    {"https": "http://114.129.2.82:8081"},
    {"https": "http://72.10.160.92:5635"},
    {"https": "http://165.232.129.150:80"},
    {"https": "http://144.126.216.57:80"}
]

# Open APIs (No sign-in or API key required)
target_urls = [
    "https://dog.ceo/api/breeds/image/random",  # Dog API (random dog images)
    "https://catfact.ninja/fact",  # Cat Facts API (random cat facts)
    "https://api.thecatapi.com/v1/images/search",  # Cat API (random cat images)
    "https://randomuser.me/api/",  # Random User API (generate random user)
    "https://jsonplaceholder.typicode.com/posts/1"  # JSONPlaceholder (fake post)
]

# Number of max retries for failed proxies
MAX_RETRIES = 3

# Delay between requests (in seconds)
DELAY_BETWEEN_REQUESTS = 5

# Number of requests allowed per proxy
MAX_REQUESTS_PER_PROXY = 10

# File to save the successful scraped data
output_json_file = "scraped_data.json"

# Mobile User-Agent Header
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G950F Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36'
}

# Function to save scraped data to the JSON file immediately
def save_data_immediately(data):
    try:
        with open(output_json_file, 'a') as outfile:
            json.dump(data, outfile, indent=4)
            outfile.write("\n")  # Newline for better readability
            print(f"Data saved to {output_json_file}")
    except Exception as e:
        print(f"Error while saving the data: {str(e)}")

# Function to make a request using a proxy
def make_request(proxy, url, retries=0):
    try:
        print(f"Using proxy: {proxy}")
        response = requests.get(url, proxies=proxy, headers=headers, timeout=15, verify=False)
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
        for proxy in proxies:
            proxy_key = proxy["https"]
            if request_count[proxy_key] >= MAX_REQUESTS_PER_PROXY:
                print(f"Max requests reached for {proxy}, moving to next proxy.")
                continue

            for url in target_urls:
                success = make_request(proxy, url)
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
