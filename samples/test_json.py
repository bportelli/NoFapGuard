import json

# def save_json():
#     data = {
#         'name': 'John',
#         'age': 25,
#         'city': 'London'
#     }

#     with open('data.txt', 'w') as f:
#         json.dump(data, f)

def load_config():
    with open('config.txt', 'r') as f:
        data = json.load(f)

        for item in data: # data.keys() or data.values() or data.items()
            print(item)
    return data

d = load_config()
print(d)