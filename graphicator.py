import requests, json
from os.path import exists
import hashlib
from termcolor import colored
import urllib3
import time
from tqdm import tqdm
import threading
import argparse
from os import mkdir


targets = []
proxies = None
failed_req = []

headers = {
    "Content-Type":"application/json",
    "User-Agent": "graphicator"
}

def openTargets(filename):
    f = open(filename, "r")
    l = f.read().split("\n")
    f.close()
    l = [i for i in l if len(i) > 0]
    return l


print('''
  _____                  __    _             __           
 / ___/____ ___ _ ___   / /   (_)____ ___ _ / /_ ___   ____
/ (_ // __// _ `// _ \ / _ \ / // __// _ `// __// _ \ / __/
\___//_/   \_,_// .__//_//_//_/ \__/ \_,_/ \__/ \___//_/   
               /_/                                         

By @fand0mas
''')

parser = argparse.ArgumentParser(description='Graphicator - GraphQL Extractor')
parser.add_argument('--use-tor', dest='tor', action='store_true', help='Configure to use tor @ 9150')
parser.add_argument('--insecure', dest='k', action='store_true', help='Disable certificate warnings', default=False)
parser.add_argument('--use-proxy', dest='proxyurl', action='store_true', help='Configure proxy url')
parser.add_argument('--default-burp-proxy', dest='proxyburp', action='store_true', help='Configure to default burp proxy settings')
parser.add_argument('--target', dest='url', action='append')
parser.add_argument('--header', dest='header', action='append', help="HEADER_KEY:HEADER_VALUE")
parser.add_argument('--file', dest='file', help='Read targets from the designated file [content format: http://.../graphql]')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Verbose mode', default=False)
parser.add_argument('--multi', dest='t', action='store_true', help='Multi Threaded Extraction (per target)', default=False)
parser.add_argument('--no-cache', dest='cache', action='store_false', help="Don't use cahce", default=True)
args = parser.parse_args()

if args.url is None and args.file is None:
	print("[!] No target provided. Use --target TARGET or --file FILE options")
	exit(1)

if args.tor:
	proxies = {'http':  'socks5://127.0.0.1:9150', 'https': 'socks5://127.0.0.1:9150'}
elif args.proxyurl is not None:
	proxies = {'http':  args.proxyurl, 'https': args.proxyurl}
elif args.proxyburp is not None:
	proxies = {'http':  '127.0.0.1:8080', 'https': '127.0.0.1:8080'}

if args.url is None and args.file is not None:
	targets = openTargets(args.file)

if args.k:
	urllib3.disable_warnings()

verbose = args.verbose
multi_t = args.t
use_cache = args.cache

if args.file is None:
	for t in args.url:
		targets.append(t)

if args.header is not None:
	for header in args.header:
		h = header.split(":")
		if len(h) > 1:
			headers[h[0]] = h[1]


print("[-] Targets: " , len(targets))
print("[-] Headers: " , str(list(headers.keys()))[1:-1])

if verbose:
	print("[-] Verbose")
if args.tor:
	print("[-] Using Tor as proxy")
if args.proxyurl or args.proxyburp:
	print("[-] Proxy is configured")
if not multi_t:
	print("[-] Multi-threaded: Disabled")
print("[-] Using cache: " + str(use_cache))
print("*"*60)

for d in ["reqcache","reqcache-intro","reqcache-queries"]:
	if not exists(d): mkdir(d)


def openFailedRequests():
    global failed_req
    if not exists("failed_req.json"):
        saveFailedRequests()
    else:
        failed_req = json.loads(open("failed_req.json", "r").read())

def saveFailedRequests():
    f = open("failed_req.json", "w")
    f.write(json.dumps(failed_req))
    f.close()


def graphql_query(url, gquery, introsp=False):
    dirname = "reqcache"
    dirintro = "reqcache-intro"
    querydir = "reqcache-queries"
    sha_1 = hashlib.sha1()
    sha_1.update(url.encode() + gquery.encode() + "Q".encode())
    cached_fname = sha_1.hexdigest()
    cache_dir = ""
    
    if not introsp:
        file_ext = ".json"
        cache_dir = dirname
    else:
        file_ext = ".intro"
        cache_dir = dirintro
	
    filename = cache_dir + "/" + cached_fname + file_ext
    
    if use_cache:
        if cached_fname in failed_req:
            return None
    if not exists(filename) or not use_cache:
        if verbose and not introsp:
            print("[*] Retrieving... => " + gquery)
        try:
            r = requests.post(url, headers=headers, data='{"query":"' + gquery + '"}', verify=False, proxies=proxies, timeout=(15,120))
            if r.status_code == 200:
                try:
                    json_response = json.loads(r.text)
                    if "data" not in json_response or "errors" in json_response:
                        failed_req.append(cached_fname)
                        if verbose:
                            print(colored(" > SOFT-ERROR (" + str(r.status_code) + ") - " + gquery[:500], 'yellow'))
                        saveFailedRequests()
                        return None
                except:
                    return None
                
                f = open(filename, "w")
                f.write(json.dumps(json.loads(r.text), indent=4))
                f.flush()
                f.close()
                
                f = open(querydir + "/" + cached_fname + ".query", "w")
                f.write(gquery)
                f.flush()
                f.close()
                return json.loads(r.text)
            else:
                failed_req.append(cached_fname)
                if verbose:
                    print(colored("[!]  ERROR (" + str(r.status_code) + ") - " +  gquery[:500], 'red'))
                return None
        except Exception as ex:
            failed_req.append(cached_fname)
            print(colored("[!]  Exception (" + url + ") - " + gquery[:500], 'red') + " " + str(ex))
            return None
            pass
    else:
        print("[*] Using cache...")
        f = open(filename, "r")
        j = json.loads(f.read())
        f.close()
        return j

def make_simple_introspection(url):
    q = "query {  __schema {    types {      name      fields {        name      }    }  } }"
    return graphql_query(url, q, True)

def make_full_introspection(url):
    introspection_full = 'query IntrospectionQuery {    __schema {      queryType { name }      mutationType { name }      subscriptionType { name }      types {        ...FullType      }      directives {        name        description        args {          ...InputValue        }        locations      }    }  }  fragment FullType on __Type {    kind    name    description    fields(includeDeprecated: true) {      name      description      args {        ...InputValue      }      type {        ...TypeRef      }      isDeprecated      deprecationReason    }    inputFields {      ...InputValue    }    interfaces {      ...TypeRef    }    enumValues(includeDeprecated: true) {      name      description      isDeprecated      deprecationReason    }    possibleTypes {      ...TypeRef    }  }  fragment InputValue on __InputValue {    name    description    type { ...TypeRef }    defaultValue  }  fragment TypeRef on __Type {    kind    name    ofType {      kind      name      ofType {        kind        name        ofType {          kind          name        }      }    }  }'
    return graphql_query(url, introspection_full, True)

def enumerate_queries(url):
    simple_intro = make_simple_introspection(url)
    if simple_intro is not None and "data" in simple_intro and simple_intro["data"] is not None and "__schema" in simple_intro["data"]:
        full_intro = make_full_introspection(url)
        if full_intro is not None:

            types = simple_intro["data"]["__schema"]["types"]
            types_map = dict() # type_name to type-dict
            for t in types:
                types_map[t["name"]] = t

            full_query_types = full_intro["data"]["__schema"]["types"]
            full_types_map = dict()  # type_name to type-dict
            query_field_map = dict()  # query_name to query-field-dict
            for t in full_query_types:
                full_types_map[t["name"]] = t

            query_literal = "--non--"
            if "Query" in full_types_map:
                query_literal = "Query"
            elif "RootQueryType"  in full_types_map:
                query_literal = "RootQueryType"
            elif "RootQueryTypes"  in full_types_map:
                query_literal = "RootQueryTypes"
            elif "RootQuery" in full_types_map:
                query_literal = "RootQuery"
            elif "RootQueries" in full_types_map:
                query_literal = "RootQueries"

            if query_literal in full_types_map:
                field_dicts = full_types_map[query_literal]["fields"]
                for field_name_d in field_dicts:
                    field_name = field_name_d["name"]
                    query_field_map[field_name] = field_name_d
            thread_list = []
            if query_literal in types_map:
                query_names = types_map[query_literal]["fields"]
                for query_name_d in query_names:
                    query_name = query_name_d["name"]
                    if query_name in query_field_map:
                        type_name = query_field_map[query_name]["type"]["name"]
                        field_kind = query_field_map[query_name]["type"]["kind"]
                        depth = 1
                        if field_kind not in ["OBJECT", "SCALAR", "ENUM"]:
                            obj = query_field_map[query_name]["type"]
                            if "ofType" not in obj or obj["ofType"] is None:
                                continue
                            while depth > 0:
                                depth += 1
                                type_name = obj["ofType"]["name"]
                                field_kind = obj["ofType"]["kind"]
                                if field_kind in ["OBJECT", "SCALAR", "ENUM"]:
                                    break
                                if depth >= 10:
                                    depth = 0
                                    break
                                if "ofType" not in obj or obj["ofType"] is None:
                                    depth = 0
                                    break
                                obj = obj["ofType"]
                                if "ofType" not in obj or obj["ofType"] is None:
                                    depth = 0
                                    break
                                if obj is None:
                                    depth = 0
                                    break
                            if depth == 0:
                                continue
                        if field_kind == "OBJECT":
                                res = generate_query_of_type(type_name, full_types_map, list())
                                if res is not None:
                                    thread_list.append(threading.Thread(target=graphql_query, args=(url, "query {" + query_name + " " + res + " }")))
                        elif field_kind == "SCALAR" or field_kind == "ENUM":
                                res = type_name
                                if res == None: res = ""
                                thread_list.append(threading.Thread(target=graphql_query, args=(url, "query {" + query_name + " " + res + " }")))
                        
                            
								
            for tinst in thread_list:
                tinst.start()
                if not multi_t:
                    tinst.join()
			
            if multi_t:
                for tinst in thread_list:
                    tinst.join()

def generate_query_of_type(type_name, full_types_map, object_list, qname = ""):
    ret_query = str(qname + " { ")

    if type_name in full_types_map:

        type_dict = full_types_map[type_name]
        type_fields = type_dict["fields"]

        if type_fields == None:
            return type_name

        for field_dict in type_fields:

            field_name = field_dict["name"]
            field_kind = field_dict["type"]["kind"]

            if field_kind == "OBJECT" or field_kind == "LIST" or field_kind == "NON_NULL":

                if field_kind == "OBJECT":
                    if field_name not in object_list:
                        object_list.append(field_name)
                    else:
                        return None
                    ret = generate_query_of_type(field_name, full_types_map, object_list, field_name)
                    if ret is not None:
                        ret_query += ret + ","

                elif field_kind == "LIST" or field_kind == "NON_NULL":
                    inner_kind = field_dict["type"]["ofType"]["kind"]
                    inner_name = field_dict["type"]["ofType"]["name"]
                    if inner_kind == "OBJECT":
                        if field_name not in object_list:
                            object_list.append(field_name)
                        else:
                            return None
                        ret = generate_query_of_type(inner_name, full_types_map, object_list, field_name)
                        if ret is not None:
                            ret_query += ret + ","
                    elif inner_kind != "LIST" and inner_kind != "OBJECT":
                        ret_query += field_name + ","
                    elif inner_kind == "LIST":
                        doubleinner_kind = field_dict["type"]["ofType"]["ofType"]["kind"]
                        doubleinner_name = field_dict["type"]["ofType"]["ofType"]["name"]
                        if doubleinner_kind == "OBJECT": # else ignore it
                            if field_name not in object_list:
                                object_list.append(field_name)
                            else:
                                return None
                            ret = generate_query_of_type(inner_name, full_types_map, object_list, field_name)
                            if ret is not None:
                                ret_query += ret + ","
            elif field_kind != "SCALAR" or field_kind != "LIST":
                ret_query += field_name + ","
        return ret_query[:-1] + " }"
    else:
        return None

openFailedRequests()
for i in tqdm(range(len(targets))):
    target_url = targets[i]
    print("[*] Enumerating...", target_url)
    enumerate_queries(target_url)
saveFailedRequests()
