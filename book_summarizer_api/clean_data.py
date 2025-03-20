import json

# Load the data
with open('data_backup.json', 'r') as f:
    data = json.load(f)

# Clean the data by removing null characters
for item in data:
    if item.get('model') == 'booksummary.chapter':
        for field in ['text', 'title']:
            if field in item['fields'] and item['fields'][field]:
                item['fields'][field] = item['fields'][field].replace('\x00', '')
    
    # Clean other text fields as well
    for field_name, field_value in item['fields'].items():
        if isinstance(field_value, str):
            item['fields'][field_name] = field_value.replace('\x00', '')

# Save the cleaned data
with open('data_backup_clean.json', 'w') as f:
    json.dump(data, f)

print("Data cleaned and saved to data_backup_clean.json") 