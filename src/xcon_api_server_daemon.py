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

#===========================#
#  - BASELINE OBJECTIVES -  #
#===========================#
# [X] Packet >> GameServer sending functionality
# [-] HTTP (client) >> Server API request functionality
# [-] Implement default set of API methods for Mohaa
#     [-] [Server]
#     [ ] [Map]
#     [ ] [Client]

def listen(listen_port=80,listen_address='',verbose=False):
    '''
    Responsible for main xcon API server loop
    - HTTP listening socket
    - deals with all API requests
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_socket: # SOCK_STREAM  = TCP
        listen_socket.bind((listen_address,listen_port))
        
        listen_socket.listen()
        client_connection,your_mum = listen_socket.accept()

        with client_connection:
            while True:
                inbound_payload = client_connection.recv(8192)
                if not inbound_payload:
                    break # .. uhh client what the fuuuuuu
                
                try:
                    return_code = process_client_request(inbound_payload,client_connection,verbose)
                except Exception as error:
                    print(f"\n\nERROR : {str(error)}\n\n")
                    if re.match('something dumb',str(error)):
                        raise # maybe there are some cases where we'd really want to throw?
                    break
                match return_code:
                    case 0 : print('Success')
                    case _ :
                        print('Not so success')
                        break
                # loop end
                
def send_client_response(socket,status_code:type[int|str],data:type[dict|str]=None,verbose=False):
    separator = '----------------------------'
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
        case 406 : headers.append('HTTP/1.1 406 NOT ACCEPTABLE')              #  No content found that conforms to the criteria given by the user agent in the Accept header sent in the request
        case 408 : headers.append('HTTP/1.1 408 REQUEST TIMEOUT')             #  Use when the server did not receive a complete request from the client within the allotted timeout period
        case 413 : headers.append('HTTP/1.1 413 REQUEST ENTITY TOO LARGE')    #  The request entity is larger than the limits defined by the server.
        case 419 : headers.append('HTTP/1.1 419 REQUEST I\'M A TEAPOT')       #  I'm a motherfucking teapot
        case 420 : headers.append('HTTP/1.1 420 ENHANCE YOUR CALM')           #  ........enhance your calm
        case 429 : headers.append('HTTP/1.1 429 TOO MANY REQUESTS')           #  user has sent too many requests in a given amount of time (“rate limiting”).
        case 449 : headers.append('HTTP/1.1 449 RETRY WITH')                  #  The request should be retried after performing the appropriate action.
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
        print('REEEEEEEEE i only like dicts and strs') # TODO: Error handling
        return

    byte_frame = bytearray()
    
    headers.append(f"Content-Length: {len(data_bytes)}\r\n\r\n")
    
    byte_frame.extend(bytearray("\r\n".join(headers),'ascii'))
    byte_frame.extend(data_bytes)
    
    if verbose : print(f"{separator}\nTRANSMITTING HTTP DATA:\n{separator}\n{byte_frame.decode('utf-8')}")
    
    socket.send(byte_frame)

def process_client_request(request_payload,socket,verbose=False):
    '''
    This boi does all the heavy lifting for listen().
    Responsible for the entire process of processing the incoming API request
    packet, and responding to clients.

    In future, move client response logic out into its own function and make it
    way smarter / more verbose to give good feedback to user.
    '''
    json_content = ''
    separator = '----------------------------'

    all_http_content = request_payload.decode('utf-8')
    split_http_content = all_http_content.splitlines()

    if verbose : print(f"\n{separator}\nREQUEST RECEIVED. HTTP data:\n{separator}\n{all_http_content}")
    
    # http://xcon-api.com/mohaa/getServerStatus (example call)
    if not re.search(r"HTTP/1\.\d",(split_http_content[0].split()[2])):
        send_client_response(socket,400,verbose=verbose); print('ERROR : Non-HTTP request received') # debug
        return 400
    
    api_call = split_http_content[0].split()[1].lstrip('/')
    if verbose : print(f"{separator}\nAPI request : {api_call}")
        
    if re.search(r"Content-Type\s{0,2}:\s{0,2}.+/json",all_http_content):
        for x in range(0,len(split_http_content)):
            if split_http_content[x].lstrip() == '' or split_http_content[x].lstrip()[0] != '{':
                continue
            json_content = ''.join(split_http_content[x:])
            
    # Serialise + lightly validate (regex) request
    matches = re.search(r"^(?P<namespaces>[a-zA-Z/]+?)/(?P<method>[a-zA-Z]+)$",api_call.strip())
    if not matches:
        send_client_response(socket,400,verbose=verbose); print(('Syntax error in client request (regex failed)'))
        return 400
    request_namespaces, request_method = matches.group('namespaces').split('/'), matches.group('method')
    
    buffered_controller = server_controller_dict[request_namespaces[0].lower()] # TODO: i dont like this .lower() business

    try:
        for namespace in request_namespaces[1:]:
            buffered_controller = getattr(buffered_controller,namespace.lower()) # TODO: i dont like this .lower() business - see https://stackoverflow.com/questions/51875460/case-insensitive-getattr
    except Exception as error:
        send_client_response(socket,400,"Error resolving request. Verify syntax and spelling is correct and retry",verbose=verbose); print(f"ERROR : {str(error)} ") # debug
        return 400 # TODO: informative answer perhaps. could leverage Python's "did you mean: DUHHH"

    available_methods = [x for x in inspect.getmembers(buffered_controller) if not x[0].startswith('_') and type(x[1]).__name__ == 'method']
    requested_method = [x for x in available_methods if (x[0].casefold()) == (request_method.casefold())]
    if requested_method == []:
        print(f"{separator}\nERROR: Method '{request_method} not found")
        send_client_response(socket,400,f"ERROR: Method '{request_method}' does not exist",verbose=verbose)
        return 400

    if json_content != '':
        request_args_dict = json.loads(json_content)
    else:
        request_args_dict = {}

    try:
        gameserver_response = getattr(buffered_controller,requested_method[0][0])(**request_args_dict)
    except TypeError:
        # TODO: write a function to customise client responses depending on what was wrong with their query
        send_client_response(socket,449,"Missing required parameters (incorrect value type also possible)",verbose=verbose)
        return 449
    except:
        send_client_response(socket,449,"Unknown error. Verify syntax and spelling is correct and retry",verbose=verbose)
        return 1
    
    send_client_response(socket,gameserver_response.status_code,gameserver_response.data,verbose=verbose)
    return 0

#==================#
#    INITIALISE    #
#==================#

server_controller_dict = {}
module_objects = {}

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

if server_controller_dict == {}:
    print(f"No game modules found in modules directory : {game_modules_foldername}")
    exit()

print(f"Imported {len(server_controller_dict)} modules.")

while True:
    listen(listen_port,"127.0.0.1",verbose=True)