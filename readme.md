

## Graphicator

Graphicator is a GraphQL "scraper" / extractor. The tool iterates over the introspection document returned by the targeted GraphQL endpoint, and then re-structures the schema in an internal form so it can re-create the supported queries. When such queries are created is using them to send requests to the endpoint and saves the returned response to a file.

Erroneous responses are not saved. By default the tool caches the correct responses and also caches the errors, thus when re-running the tool it won't go into the same queries again.

Use it wisely and use it only for targets you have the permission to interact with.

We hope the tool to automate your own tests as a penetration tester and gives some push even to the ones that don't do GraphQLing test yet.

To learn how to perform assessments on GraphQL endpoints: https://cybervelia.com/?p=736&preview=true

## Installation

### Install on your system

```
python3 install -r requirements.txt
```

### Using a container instead

```
docker run --rm -it -p8005:80 cybervelia/graphicator --target http://the-target:port/graphql --verbose
```

When the task is done it zips the results and such zip is provided via a webserver served on port 8005. To kill the container, provide CTRL+C. When the container is stopped the data are deleted too. Also you may change the host port according to your needs.

## Usage

```
python3 graphicator.py [args...]
```

### Setting up a target

The first step is to configure the target. To do that you have to provide either a `--target` option or a file using `--file`.

**Setting a single target via arguments**

```
python3 graphicator.py --target https://subdomain.domain:port/graphql
```

**Setting multiple targets**

```
python3 graphicator.py --target https://subdomain.domain:port/graphql --target https://target2.tld/graphql
```

**Setting targets via a file**

```
python3 graphicator.py --file file.txt
```

The file should contain one URL per line as such:

```
http://target1.tld/graphql
http://sub.target2.tld/graphql
http://subxyz.target3.tld:8080/graphql
```

### Using a Proxy

You may connect the tool with any proxy.

**Connect to the default burp settings (port 8080)**

```
python3 graphicator.py --target target --default-burp-proxy
```

**Connect to your own proxy**

```
python3 graphicator.py --target target --use-proxy
```

**Connect via Tor**

```
python3 graphicator.py --target target --use-tor
```

### Using Headers

```
python3 graphicator.py --target target --header "x-api-key:60b725f10c9c85c70d97880dfe8191b3"
```

### Enable Verbose

```
python3 graphicator.py --target target --verbose
```

### Enable Multi-threading

```
python3 graphicator.py --target target --multi
```

### Disable warnings for insecure and self-signed certificates

```
python3 graphicator.py --target target --insecure
```

### Avoid using cached results

```
python3 graphicator.py --target target --no-cache
```

### Example

```
python3 graphicator.py --target http://localhost:8000/graphql --verbose --multi

  _____                  __    _             __           
 / ___/____ ___ _ ___   / /   (_)____ ___ _ / /_ ___   ____
/ (_ // __// _ `// _ \ / _ \ / // __// _ `// __// _ \ / __/
\___//_/   \_,_// .__//_//_//_/ \__/ \_,_/ \__/ \___//_/   
               /_/                                         

By @fand0mas

[-] Targets:  1
[-] Headers:  'Content-Type', 'User-Agent'
[-] Verbose
[-] Using cache: True
************************************************************
  0%|                                                     | 0/1 [00:00<?, ?it/s][*] Enumerating... http://localhost:8000/graphql
[*] Retrieving... => query {getArticles  { id,title,views } }
[*] Retrieving... => query {getUsers  { id,username,email,password,level } }
100%|█████████████████████████████████████████████| 1/1 [00:00<00:00, 35.78it/s]
```

```
$ cat reqcache/9652f1e7c02639d8f78d1c5263093072fb4fd06c.json 
{
    "data": {
        "getUsers": [
            {
                "id": 1,
                "username": "theo",
                "email": "theo@example.com",
                "password": "1234",
                "level": 1
            },
            {
                "id": 2,
                "username": "john",
                "email": "john@example.com",
                "password": "5678",
                "level": 1
            }
        ]
    }
}
```

```
$ cat reqcache-queries/9652f1e7c02639d8f78d1c5263093072fb4fd06c.query 
query {getUsers  { id,username,email,password,level } }
```



## Output Structure

Three folders are created:

- reqcache: The response of each valid query is stored in JSON format
- reqcache-intro: All introspection queries are stored in a separate file in this directory
- reqcache-queries: All queries are stored in a separate file in this directory. The filename of each query will match with the corresponding filename in the reqcache directory that holds the query's response.

The filename is the hash which takes account the query and the url.

## License & EULA

Copyright 2023 Cybervelia Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the  "Software"), to deal in the Software without restriction, including  without limitation the rights to use, copy, modify, merge, publish,  distribute, sublicense, and/or sell copies of the Software, and to  permit persons to whom the Software is furnished to do so, subject to  the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Maintainer

The tools has been created and maintained by (@fand0mas).

Contribution is also welcome.