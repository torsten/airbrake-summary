from __future__ import division
from __future__ import print_function

import sys
import json
import re
from collections import defaultdict

import requests
from pyquery import PyQuery as pq


def parse_error(string):
    error_dict = dict()
    
    doc = pq(string.encode('utf-8'))
    fields = doc("group > *")
    for field in fields:
        if field.tag == "environment":
            fields = {ele.tag: ele.text for ele in pq(field)("environment > *")}
            error_dict[field.tag] = fields
        elif field.tag == "backtrace":
            lines = [line.text for line in pq(field)("line")]
            error_dict[field.tag] = lines
        else:
            error_dict[field.tag] = field.text

    return error_dict


def read_merge_patterns(config):
    merge_patterns = dict()

    string_patterns = config['merge_patterns']
    for pat in string_patterns:
        pattern = re.escape(pat)
        pattern = pattern.replace("\\%x", "(?:0x)?[0-9a-f]+")
        pattern = pattern.replace("\\%d", "\\d+")
        pattern = pattern.replace("\\%S", "\\S+")

        merge_patterns[pat] = re.compile(pattern)

    return merge_patterns


def read_split_patterns(config):
    split_patterns = [re.compile(pat) for pat in config['split_patterns']]
    return split_patterns


def relative_backtrace(backtrace):
    stack_frame_re = re.compile(r"^\s*([^:]+):.+ \+ (\d+)'?\s*$")
    rel = []

    for line in backtrace:
        match = stack_frame_re.match(line)
        if match:
            # Heuristic 0: Cluster by stack trace hard-core
            # rel.append((match.group(1), match.group(2)))
            
            # Heuristic 1: Merge crashes in same lirbary and ignore library addresses
            # if match.group(1) == "Wunderlist":
            #     rel.append((match.group(1), match.group(2)))
            # elif len(rel) == 0 or rel[-1][0] != match.group(1):
            #     rel.append((match.group(1), 0))
            
            # Heuristic 2: Unly walk trace till first appearance of main binary
            if match.group(1) == "Wunderlist":
                rel.append((match.group(1), match.group(2)))
                if len(rel) > 1:
                    break

            elif len(rel) == 0 or rel[-1][0] != match.group(1):
                rel.append((match.group(1), 0))
            # else:
            #     rel.append((match.group(1), 0))

    return tuple(rel)


if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)

    merge_patterns = read_merge_patterns(config)
    split_patterns = read_split_patterns(config)
    
    with open("errors.json") as f:
        all_errors = json.load(f)
        error_ids = all_errors.keys()

        classes = defaultdict(list)

        for error_id in error_ids:
            xml_string = all_errors[error_id]
            if xml_string:
                e = parse_error(xml_string)
                error_class = e['error-class']

                did_merge_or_split = False
                for split_re in split_patterns:
                    if split_re.match(error_class):
                        # print("%s\n\n\t%s--%s--" % (e['error-message'], "\n\t".join(e['backtrace']), relative_backtrace(e['backtrace'])), end="\n\n")
                        
                        did_merge_or_split = True
                        class_key = (error_class, relative_backtrace(e['backtrace']))
                        classes[class_key].append(e)
                        break

                if did_merge_or_split:
                    continue

                for merge_key, merge_re in merge_patterns.iteritems():
                    if merge_re.match(error_class):
                        did_merge_or_split = True
                        classes[(merge_key, tuple())].append(e)
                        break

                if did_merge_or_split:
                    continue

                classes[(error_class, tuple())].append(e)

        output = list()
        for class_key, klass_errors in classes.iteritems():
            title, backtrace = class_key

            output.append({"title":title,
                           "count":len(klass_errors),
                           "sample_message": "" if title.startswith("ALog") else klass_errors[0]["error-message"],
                           "short_trace": backtrace,
                           "errors": klass_errors})

            # print(len(klass_errors), title.encode('utf8'))
            print("%d %s %r // %r // %r" % (len(klass_errors), title, klass_errors[0]["error-message"] if not title.startswith("ALog") else "", " - ".join("%s:%s" % tup for tup in backtrace), repr(klass_errors[0]["environment"])))

            # if re.match(r"NS.*Exception", title):
            #     print("%d %s %s // %s // %s" % (len(klass_errors), title, klass_errors[0]["error-message"], " - ".join("%s:%s" % tup for tup in backtrace), repr(klass_errors[0]["environment"])))
            #     # print(len(klass_errors), title.encode('utf8') + klass_errors[0]["error-message"] + " // " + " - ".join("%s:%s" % tup for tup in backtrace))
            # else:
            #     print(len(klass_errors), title.encode('utf8') + " // " + " - ".join("%s:%s" % tup for tup in backtrace))
        
        output_file = open("clusters.json", "w")
        json.dump(output, output_file)
