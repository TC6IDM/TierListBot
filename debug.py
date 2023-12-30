import json
import jsonpickle
import os
def debug(item: object, location: str = "debug.json") -> None:
    '''
    debugs a given object
    
    :param item:
        the object to debug
    :param location: 
        the file to write the debug to
    '''
    json_object = jsonpickle.encode(item)
    if not os.path.exists(f'debug/'):
        os.makedirs(f'debug/')
    with open(f'debug/{location}', "w") as outfile:
        outfile.write(json.dumps(json.loads(json_object), indent=4))