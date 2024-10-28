import os
import json
import requests
import concurrent.futures
from datetime import datetime, timedelta
from pathlib import Path

# Constants
BASE_URL = "https://iiif-auth.onb.ac.at/presentation/ANNO/"
START_YEAR = 1901
END_YEAR = 1939
SAVE_PATH = ""
LOG_FILE = "log.txt"
USERNAME = ""
PASSWORD = ""
AUTH_TUPLE = (USERNAME, PASSWORD)

# Function to generate manifest URLs with valid dates
def generate_manifest_urls():
    urls = []
    start_date = datetime(START_YEAR, 1, 1)
    end_date = datetime(END_YEAR, 12, 31)

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        url = f"{BASE_URL}{date_str}/manifest/"
        urls.append(url)
        current_date += timedelta(days=1)  # Increment the day

    return urls

# Function to download XML file
def download_xml(url, date_part, auth_tuple):
    xml_name = url.split('/')[-1]
    new_xml_name = f"{date_part}_{xml_name}"
    xml_dir = Path(SAVE_PATH)
    xml_dir.mkdir(parents=True, exist_ok=True)
    xml_file_path = xml_dir / new_xml_name
    
    if xml_file_path.exists():
        print(f"File {new_xml_name} already exists. Skipping...")
        return

    print(f"Downloading {url}...")
    xml_data = requests.get(url, auth=auth_tuple).content
    
    with open(xml_file_path, 'wb') as xml_file:
        xml_file.write(xml_data)
    print(f"Downloaded {url}")

# Function to process each manifest URL
def process_manifest(manifest_url):
    try:
        # Fetching the manifest JSON
        response = requests.get(manifest_url, auth=AUTH_TUPLE)
        if response.status_code != 200:
            log_error(f"Manifest not found: {manifest_url}")
            return

        manifest = response.json()
        date_part = manifest_url.split('/')[-3]  # Extracting date part from the URL

        # Extract the first 6 XML URLs from the manifest
        sequences = manifest.get('sequences', [{}])
        xml_urls = []
        for seq in sequences:
            canvases = seq.get('canvases', [])
            for canvas in canvases:
                other_content = canvas.get('otherContent', [{}])
                for content in other_content:
                    resources = content.get('resources', [])
                    for resource in resources:
                        xml_id = resource.get('resource', {}).get('@id', None)
                        if xml_id and xml_id.endswith('.xml'):
                            xml_urls.append(xml_id)
                            if len(xml_urls) >= 6:  # Limit to first 6 XML files
                                break
                    if len(xml_urls) >= 6:
                        break
                if len(xml_urls) >= 6:
                    break
            if len(xml_urls) >= 6:
                break

        # Download XMLs in parallel
        if xml_urls:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(download_xml, url, date_part, AUTH_TUPLE) for url in xml_urls]
                concurrent.futures.wait(futures)
        else:
            log_error(f"No XML URLs found in manifest: {manifest_url}")
    except Exception as e:
        log_error(f"Error processing manifest {manifest_url}: {str(e)}")

# Function to log errors
def log_error(message):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{message}\n")

# Main script execution
def main():
    manifest_urls = generate_manifest_urls()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_manifest, url) for url in manifest_urls]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()
