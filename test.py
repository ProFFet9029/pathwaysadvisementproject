import json

file = open('Utilities/majors/major_paths.json')
offerings = json.load(file)
print(offerings.keys())
file.close()
