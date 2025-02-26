import json
import os


file_path = r'output/churches_with_coordinates.json'
churches_with_detailed_address = []

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for church in data:
    if church.get('detailed_address') == True:
        churches_with_detailed_address.append(church)


with open('output/churches_with_detailed_address.json', 'w', encoding='utf-8') as f:
    json.dump(churches_with_detailed_address, f, indent=4, ensure_ascii=False)

    print(f'{len(churches_with_detailed_address)} churches have detailed address.')
    print('created output/churches_with_detailed_address.json')

