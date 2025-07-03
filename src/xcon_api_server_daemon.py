# https://restfulapi.net/http-status-codes/ - some good ones in here (418/420)
import http.server
import socket
import selectors
import re
import sys
import inspect
import importlib.util
import json
import http
# temp
import os
import glob
# TEMP - just makes console output look pretty
import pprint
os.chdir('C:\\Users\\bradl\\OneDrive\\Code\\Python\\xcon-api\\src')
game_modules_foldername = 'game_modules'
listen_port = 69

server_controller_dict = {}
module_objects = {}
#===========================#
#  - BASELINE OBJECTIVES -  #
#===========================#
# [X] Packet >> GameServer sending functionality
# [-] HTTP (client) >> Server API request functionality
# [-] Implement default set of API methods for Mohaa
#     [-] [Server]
#     [ ] [Map]
#     [ ] [Client]

print(f"Imported {len(server_controller_dict)} modules.")

def listen(listen_port=80,listen_address=''):
    '''
    Responsible for main xcon API server loop
    - HTTP listening socket
    - deals with all API requests
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_socket: # SOCK_STREAM  = TCP
        listen_socket.bind((listen_address,listen_port))
        
        listen_socket.listen()
        client_connection,client_addr = listen_socket.accept()

        with client_connection:
            while True:
                inbound_payload = client_connection.recv(8192)
                if not inbound_payload:
                    break
                print(inbound_payload) # debug
                json_content = ''
                all_http_content = inbound_payload.decode('utf-8')
                split_http_content = all_http_content.splitlines()
                # http://xcon-api.com/mohaa/getServerStatus (example call)
                if not re.search(r"HTTP/1\.\d",(split_http_content[0].split()[2])):
                    send_client_response(client_connection,400); print('ERROR : Non-HTTP request received') # debug
                    break
                
                api_call = split_http_content[0].split()[1].lstrip('/')
                print(api_call) # debug
                
                if re.search(r"Content-Type\s{0,2}:\s{0,2}.+/json",all_http_content):
                    for x in range(0,len(split_http_content)):
                        if split_http_content[x].lstrip() == '' or split_http_content[x].lstrip()[0] != '{':
                            continue
                        json_content = ''.join(split_http_content[x:])
                        
                # Serialise + lightly validate (regex) request
                matches = re.search(r"^(?P<namespaces>[a-zA-Z/]+?)/(?P<method>[a-zA-Z]+)$",api_call.strip())
                if not matches:
                    send_client_response(client_connection,400); print(('Syntax error'))
                    break
                request_namespaces, request_method = matches.group('namespaces').split('.'), matches.group('method')
                
                buffered_controller = server_controller_dict[request_namespaces[0].lower()] # TODO: i dont like this .lower() business

                for namespace in request_namespaces[1:]:
                    buffered_controller = getattr(buffered_controller,namespace.lower()) # TODO: i dont like this .lower() business - see https://stackoverflow.com/questions/51875460/case-insensitive-getattr

                available_methods = [x for x in inspect.getmembers(buffered_controller) if not x[0].startswith('_') and type(x[1]).__name__ == 'method']
                requested_method = [x for x in available_methods if (x[0].casefold()) == (request_method.casefold())]
                if requested_method == []:
                    print('raise exception picture me kicking and screaming right now i simply cannot believe this') # debug
                    send_client_response(client_connection,200)
                    break

                if json_content != '':
                    request_args_dict = json.loads(json_content)
                else:
                    request_args_dict = {}

                gameserver_response = getattr(buffered_controller,requested_method[0][0])(**request_args_dict)
                
                send_client_response(client_connection,gameserver_response.status_code,gameserver_response.data)
                
def send_client_response(socket,status_code:type[int|str],data:type[dict|str]=None):
    headers = []
    
    match int(status_code):
        #> 1xx : Informational
        #> 2xx : Success
        case 200 : headers.append('HTTP/1.1 200 OK')                          #  Request succeeded
        case 204 : headers.append('HTTP/1.1 204 NO CONTENT')                  #  Request fulfilled (OK), no response body
        #> 3xx : Redirection
        case 301 : headers.append('HTTP/1.1 301 MOVED PERMANENTLY')           #  URL has changed permamently. New URL in header (i.e. Location: <new_URI>)
        #> 4xx : Client Error (also funnies)
        case 400 : headers.append('HTTP/1.1 400 BAD REQUEST')                 #  Server could not understand the request due to incorrect syntax
        case 401 : headers.append('HTTP/1.1 401 UNAUTHORIZED')                #  The request requires user authentication info
        case 403 : headers.append('HTTP/1.1 403 FORBIDDEN')                   #  Unauthorised request. The client does not have access rights to the content
        case 404 : headers.append('HTTP/1.1 404 NOT FOUND')                   #  The server can not find the requested resource
        case 405 : headers.append('HTTP/1.1 405 METHOD NOT ALLOWED')          #  Method exists but forbidden
        case 408 : headers.append('HTTP/1.1 408 REQUEST TIMEOUT')             #  Use when the server did not receive a complete request from the client within the allotted timeout period
        case 413 : headers.append('HTTP/1.1 413 REQUEST ENTITY TOO LARGE')    #  The request entity is larger than the limits defined by the server.
        case 419 : headers.append('HTTP/1.1 419 REQUEST I\'M A TEAPOT')       #  I'm a motherfucking teapot
        case 420 : headers.append('HTTP/1.1 420 ENHANCE YOUR CALM')           #  ........enhance your calm
        case 429 : headers.append('HTTP/1.1 429 TOO MANY REQUESTS')           #  user has sent too many requests in a given amount of time (“rate limiting”).
        #> 5xx : Server Error
        case _ :
            print(f"INVALID STATUS CODE : {status_code}")
            return

    if data == None:
        header = (''.join(headers) + '\r\n\r\n')
        payload_bytes = bytearray(header,'ascii')
        print(payload_bytes.decode('utf-8'))
        socket.send(payload_bytes)
        return
    
    if type(data) == dict:
        headers.append('Content-Type: application/json')
        data_json = json.dumps(data,indent=2)
        data_bytes = bytearray(data_json,'ascii')
    elif type(data) == str:
        headers.append('Content-Type: text/plain')
        data_bytes = bytearray(data,'ascii')
    else:
        print('REEEEEEEEE i only like dicts and strs')
        return

    byte_frame = bytearray()
    
    headers.append(f"Content-Length: {len(data_bytes)}\r\n\r\n")
    
    byte_frame.extend(bytearray("\r\n".join(headers),'ascii'))
    byte_frame.extend(data_bytes)
    
    print(byte_frame.decode('utf-8')) # debug
    socket.send(byte_frame)

#==================#
#    INITIALISE    #
#==================#

directory = os.path.abspath(game_modules_foldername)
python_files = glob.glob(os.path.join(directory, '*.py'))

if not python_files:
    print(f"No modules found in '{game_modules_foldername}'")
    sys.exit

for filepath in python_files:
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    if module_name == "__init__":
        continue

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        server_controller_dict[module.game_id] = module.server_controller
        print(f"Imported module: {module_name}")
    else:
        print(f"Failed to load: {filepath}")

while True:
    listen(listen_port,"127.0.0.1")