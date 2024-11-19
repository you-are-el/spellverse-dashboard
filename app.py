import subprocess
import json

# URLs
base_url_list = "https://spellverse.taprootwizards.com/spellverse-data/list.json?v=ea1042984c22ce6e3e2052a8aaa47f5b"
base_url_post = "https://spellverse.taprootwizards.com/spellverse-data/posts/"

# Headers to mimic a real browser request
HEADERS = [
    "-H", "Accept: application/json",
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
]

# Function to fetch raw text using curl with headers
def fetch_text_with_curl(url):
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "GET", *HEADERS, url],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error fetching URL {url}: {e}")
        return None

# Step 1: Fetch the raw list data as plain text
raw_list_data = fetch_text_with_curl(base_url_list)
if not raw_list_data:
    print("Failed to fetch the list data.")
    exit()

# Step 2: Treat the raw text as a plain string and split into entries
entry_list = raw_list_data.strip('[]"\n ').split('","')  # Handle it as plain text and split manually

# Step 3: Fetch and aggregate data for each entry
all_data = []
for entry in entry_list:
    try:
        id0, id1, _ = entry.split("/")
        post_url = f"{base_url_post}{id0}_{id1}.json"
        print(f"Fetching data for {post_url}...")
        post_data = fetch_text_with_curl(post_url)
        if post_data:
            # Append the raw JSON string directly
            all_data.append(json.loads(post_data))
        else:
            print(f"Failed to fetch data for {post_url}.")
    except Exception as e:
        print(f"Error processing entry {entry}: {e}")

# Step 4: Save the aggregated data to a JSON file
output_file = "large_data.json"
with open(output_file, "w") as f:
    json.dump(all_data, f, indent=4)

print(f"Data saved to {output_file}.")
