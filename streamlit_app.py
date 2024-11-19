import streamlit as st
import json
from collections import Counter
import subprocess

# Development mode flag
DEV_MODE = True

# Page config
st.set_page_config(page_title="Spellverse Tracker", layout="wide")

# Add banner image
st.image("banner.png", use_container_width=True)
st.title("Spellverse Dashboard")
st.write("Welcome to the Spellverse Dashboard! This dashboard shows quest data from the [Taproot Wizards Spellverse](https://spellverse.taprootwizards.com/) - a magical realm where wizards complete quests and collect stars. Use this dashboard to explore participation stats and search through all the quest submissions.")

# URLs and headers for fetching data
base_url_list = "https://spellverse.taprootwizards.com/spellverse-data/list.json?v=ea1042984c22ce6e3e2052a8aaa47f5b"
base_url_post = "https://spellverse.taprootwizards.com/spellverse-data/posts/"
HEADERS = [
    "-H", "Accept: application/json",
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
]

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
        st.error(f"Error fetching URL {url}: {e}")
        return None

# Load data with progress bar
if DEV_MODE:
    with open('large_data.json', 'r') as f:
        data = json.load(f)
else:
    with st.spinner('Fetching latest Spellverse data...'):
        # Try to fetch fresh data
        raw_list_data = fetch_text_with_curl(base_url_list)
        if raw_list_data:
            try:
                entry_list = raw_list_data.strip('[]"\n ').split('","')
                data = []
                progress_bar = st.progress(0)
                
                for i, entry in enumerate(entry_list):
                    try:
                        id0, id1, _ = entry.split("/")
                        post_url = f"{base_url_post}{id0}_{id1}.json"
                        post_data = fetch_text_with_curl(post_url)
                        if post_data:
                            data.append(json.loads(post_data))
                        progress_bar.progress((i + 1) / len(entry_list))
                    except Exception as e:
                        st.warning(f"Error processing entry {entry}: {e}")
                
                progress_bar.empty()
                st.success('Successfully fetched latest data!')
                
                # Save as backup
                with open('large_data.json', 'w') as f:
                    json.dump(data, f, indent=4)
                    
            except Exception as e:
                st.error(f"Error processing fetched data: {e}")
                st.info("Loading from backup file...")
                with open('large_data.json', 'r') as f:
                    data = json.load(f)
        else:
            st.warning("Could not fetch fresh data. Loading from backup file...")
            with open('large_data.json', 'r') as f:
                data = json.load(f)

# Initialize counter for names
name_counter = Counter()

# Process each entry
for entry in data:
    # Add the main user (removing @ if present)
    user = entry['user'].lstrip('@')
    name_counter[user] += 1
    
    # Add all teammates
    for teammate in entry['teammates']:
        name_counter[teammate] += 1

st.write("")
st.write("")

# Let user choose how many top wizards to display
top_n = st.number_input("How many top wizards would you like to see?", min_value=1, max_value=50, value=10, step=1)

# Get the top N most common names
top_wizards = name_counter.most_common(top_n)

# Display top N
st.header(f"Top {top_n} Spellverse Star Collectors")
st.write("These rankings include all quests where a wizard appeared either as the main submitter or as a teammate on someone else's submission.")
for i, (name, count) in enumerate(top_wizards, 1):
    st.write(f"{i}. {name}: **{count}**")

# Search functionality
st.header("Search Wizards")
search_term = st.text_input("Enter a username to search all quests for that wizard:")

if search_term:
    search_term = search_term.lower()
    found_quests = []
    
    for entry in data:
        user = entry['user'].lstrip('@').lower()
        teammates = [t.lower() for t in entry['teammates']]
        
        if search_term in user or search_term in teammates:
            # Get the slug without the mission part
            base_slug = '/'.join(entry['slug'].split('/')[:-1])
            quest_link = f"https://spellverse.taprootwizards.com/post/{base_slug}"
            
            found_quests.append({
                'date': entry['date'],
                'mission': entry['mission'],
                'user': entry['user'],
                'teammates': entry['teammates'],
                'text': entry['text'],
                'link': quest_link
            })
    
    if found_quests:
        st.subheader(f"Found {len(found_quests)} quests for '{search_term}'")
        for quest in found_quests:
            with st.expander(f"{quest['mission'].capitalize()} on {quest['date'][:10]}"):
                st.write(f"**Main User:** {quest['user']}")
                st.write("**Teammates:**")
                for teammate in quest['teammates']:
                    st.write(f"- {teammate}")
                st.write("**Quest Text:**")
                st.write(quest['text'])
                st.write("**Spellverse Link:**")
                st.write(quest['link'])
    else:
        st.warning("No quests found for this user.")
