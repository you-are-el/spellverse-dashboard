import json
from collections import Counter

# Read the JSON data
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

# Get the top 10 most common names
top_10 = name_counter.most_common(10)

# Print results
print("\nTop 10 Most Active Users:")
print("-" * 30)
for i, (name, count) in enumerate(top_10, 1):
    print(f"{i}. {name}: {count} appearances")
