""" This script is supposed to do the complete symbolication and
convert the JSON into JSONP.
"""
import json

if __name__ == '__main__':
    with open("clusters.json") as in_file:
        data = json.load(in_file)
        data.sort(key=lambda dct: dct["count"], reverse=True)
        
        with open("clusters.jsonp", "w") as out_file:
            out_file.write("load_data(%s);" % json.dumps(data))
