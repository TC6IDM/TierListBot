import json, jsonpickle
def debug(item,location = "debug.json"):
    json_object = jsonpickle.encode(item)
    with open(f'/debug/{location}', "w") as outfile:
        outfile.write(json.dumps(json.loads(json_object), indent=4))