from __future__ import division
from __future__ import print_function

import sys
import json
import multiprocessing

import requests
from pyquery import PyQuery as pq


def fetch_error_pages(account, project_id, auth_token):
    page = 1
    base_url = "http://%s.airbrake.io/" % (account,)
    while True:
        print("Fetching page %d" % page)
        url = "%s/projects/%d/groups.xml" % (base_url, project_id)
        params = {'page': page, 'auth_token': auth_token}
        
        try:
            resp = requests.get(url, params=params)
        except requests.exceptions.ConnectionError:
            print("requests.exceptions.ConnectionError")
            continue

        if resp.ok:
            # print("got: %r" % (resp.text,))
            d = pq(resp.content)
            groups = d("groups group")
            yield groups

            if len(groups) < 30:
                break
            else:
                page += 1
        else:
            print("Request for %s failed: %s", (url, resp.text))
            break


def fetch_error(args):
    account, error_id, auth_token, i = args

    url = "http://%s.airbrake.io/errors/%s.xml" % (account, error_id)
    params = {'auth_token': auth_token}

    try:
        resp = requests.get(url, params=params)

        print("%d " % i, end="")
        sys.stdout.flush()
        
    except requests.exceptions.ConnectionError:
        print("ConnectionError ", end="")
        return None
    
    if resp.ok:
        return resp.text
    else:
        print("Request for %s failed: %s" % (url, resp.text))


if __name__ == "__main__":
    all_errors = dict()

    def save_errors():
        with open('errors.json', 'w') as out:
            json.dump(all_errors, out)

    try:
        with open("config.json") as f:
            config = json.load(f)
            auth_token = config['auth_token']
            account = config['account']
            project = int(config['project_id'])

            pool = multiprocessing.Pool(processes=30)

            for page in fetch_error_pages(account, project, auth_token):

                arguments = [(account, pq(group)("id").text(), auth_token, i) for i, group in enumerate(page)]
                results = pool.map(fetch_error, arguments)
                
                for error_data, args in zip(results, arguments):
                    error_id = args[1]
                    all_errors[error_id] = error_data

                print()

    except KeyboardInterrupt:
        print("Caught CTRL-C")

    save_errors()
