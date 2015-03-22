import requests
import argparse
import sys
import json

conspectus_url = "http://conspectus-dev.metaarchive.org"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add, delete or modify dc elements for a given collection")
    parser.add_argument('--collection-id', dest='c_id', required=True)
    parser.add_argument('--operation', dest='operation', required=True)
    parser.add_argument('--element-id', dest='e_id')
    parser.add_argument('--term', dest='term')
    parser.add_argument('--value', dest='value')
    parser.add_argument('--user', dest='user', required=True)
    parser.add_argument('--pass', dest='passwd', required=True)
    args = parser.parse_args()

    operation = args.operation.upper()
    if operation not in ('POST', 'PUT', 'GET', 'DELETE'):
        sys.stderr.write("'%s' is not a supported operation\n" % operation)
        sys.exit(1)

    #Authenticate and do the csrf garbage
    login_url = "%s/login" % conspectus_url
    session = requests.Session()
    session.get(login_url)
    cookies = dict(session.cookies)
    token = cookies['csrftoken']
    session.headers.update( {'X-CSRFToken' : token } )
    session.post(login_url, cookies = cookies, data={'username':args.user, 'password':args.passwd})

    response = None
    if operation == 'GET':
        if args.e_id:
            url = "%s/collections/%s/dc_pairs/%s" % (conspectus_url, args.c_id, args.e_id)
        else:
            url = "%s/collections/%s/dc_pairs" % (conspectus_url, args.c_id)
        response = session.get(url)
    elif operation == 'POST' or operation == 'PUT':
        if not args.term or not args.value:
            sys.stderr.write("Adding or modifying requires the --term and --value parameters\n")
            sys.exit(1)
        if operation == 'PUT':
            if not args.e_id:
                sys.stderr.write("You must provide the --element-id parameter to modify an element\n")
                sys.exit(1)
        new_dict = { "term" : args.term, "value" : args.value }
        post_payload = json.dumps(new_dict)
        if operation == 'POST':
            url = "%s/collections/%s/dc_pairs" % (conspectus_url, args.c_id)
            response = session.post(url, data=post_payload)
        else: #PUT
            url = "%s/collections/%s/dc_pairs/%s" % (conspectus_url, args.c_id, args.e_id)
            response = session.put(url, data=post_payload)
    elif operation == 'DELETE':
        if not args.e_id:
            sys.stderr.write("You must provide the --element-id parameter to delete an element\n")
            sys.exit(1)
        url = "%s/collections/%s/dc_pairs/%s" % (conspectus_url, args.c_id, args.e_id)
        response = session.delete(url)
      
    print "(%s) %s" % (response.status_code, response.text)
