import json
import jsonpickle
import os
def debug(item,location = "debug.json"):
    json_object = jsonpickle.encode(item)
    if not os.path.exists(f'/debug/{location}'):
        os.makedirs(f'/debug/{location}')
    with open(f'/debug/{location}', "w") as outfile:
        outfile.write(json.dumps(json.loads(json_object), indent=4))