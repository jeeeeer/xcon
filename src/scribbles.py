
# Get Server Status:
# 1. API call comes from client
# 2. Appropriate controller is found and assigned to x
# 3. Corresponding method is looked up and called
# 4. Method output == rcon_string
# 5. x.send_payload(rcon_string) # expecting response
# 6. - response received
# 7. Serialise response into .json form
# 8. Respond to original api call (step#1) with the request fulfilment:

# [ ] HURDLE: how do we deal with traffic-control when a certain 'get' API call is made, and it needs to be formatted/serialised in a specific fashion?
#             i.e. where should this processing be done? .. if it's not done within the X-Controller instance, the only other option is for
#             the responsibility of fulfilling that procedure call to be split.

# game_id:type[str|int]=None, server_ip:str=None, server_port:type[str|int]=None, rcon_key:str=None, version:type[str|int]=None, server_state:str=None, clients:dict={}, **kwargs):
{
    'game_id' : 'mohaa',
    'server_ip' : '32.119.43.6',
    'server_port' : 12203,
    'rcon_key' : 'yourMumSucks',
    'version' : '1.12',
    'server_state' : 'Running',
    

}
message = "rcon " + rcon_key + " status"

supported_games = [
    "mohaa"
]

gameserver_overrides = [
    {'mohaa' : 'GameServer_extendedBy_MOHAA'}
]

#############################################
#   PREVIOUS CODE IN 'listen()' MAIN LOOP:  #
#############################################

                
                # 2. Serialise and security-check the JSON payload, and pack into variable
                
                # 3. Build relevant Server object (i.e. buffered_server = xcon_Mohaa.Mohaa)
                #      - Object attributes will be populated with any parameters provided in payload
                match request_namespaces[0]:
                    case 'Mohaa' : buffered_server = xcon_Mohaa.Mohaa(request_namespaces,request_method,**api_request['args'])
                    #case ['Bf2',*remaining_namespaces] : buffered_server = x_Bf2.Bf2
                    #case ['Minecraft',*remaining_namespaces] : buffered_server = x_Minecraft.Minecraft
                    case _ : print(('No module found for : ' + api_call_namespaces[0])); continue
                
                # OK GUYS NEW PLAN : instead of creating a new instance once every new request, load instances ONCE on startup (they'll effectively be immutable)
                # and then any time we need to interface with a Server instance, we just look for suitable class instance, getting them by game id attribute

                # 4. If other namespaces need to get involved in order for the chosen method to be reached, now is the time
                #    (example) Mohaa.Client.kick() was called, and the default [Server] 'Mohaa' object we made earlier was initiated with an empty client list. Therefore, in order
                #              to call a method on the client, we'd need to instantiate the [Client] object now. buffered_server.update_client_list('add','10.0.0.0','bartholemew','84176')
                
                # *CHECK    - reason that #3 and #4 are sequenced as such is that we need to make all relevant methods available (e.g. valid) before we can fully validate and action the request
                
                # 5. After confirming that the requested method is valid and available in the specified namespace,
                #    CALL METHOD (buffered_server.map.change(buffered_server,'dm/mohdm6'))
                #       - send_packet to server
                #       - if one is received, hand back server response to user; if none is received, return status code
                
                #payload_object = buffered_server.deserialise_payload(command_plaintext)
                
                # execute method - this returns a) a string "map dm/mohdm6" b) is_rcon_required=True
                # buffered_server.map.changeMap('dm/mohdm6')

                # sendcommand(payload_object)
                # server_response = buffered_server.sendcommand(payload_object)
                
                # 1. If payload, deserialize payload (convert from json)
                match api_call_namespaces:
                    # TODO: ALSO - WHILE WE ARE HERE, upon initializing inside the class, we should be building any required instances of classes we need now
                    case ['Mohaa',*remaining_namespaces] : buffered_server = xcon_Mohaa.Mohaa(**request_parameters)
                    #case ['Bf2',*remaining_namespaces] : buffered_server = x_Bf2.Bf2
                    #case ['Minecraft',*remaining_namespaces] : buffered_server = x_Minecraft.Minecraft
                    case _ : print(('Unsupported namespace : ' + api_call_namespaces[0])); continue
                
                class_names = []
                class_list = (x for x in (inspect.getmembers(sys.modules[__name__], inspect.isclass)) if not x[0][0].startswith('_'))
                for x in class_list: class_names += x
                class_names = class_names[0::2]

                # for x in class_list: print(x)
                if api_call_method in class_list:
                    print('wahoo')

                buffered_server.list_available_api_methods
                getattr(buffered_server,request_method)
                # craft up a response, and then send it:
                buffered_server.populate_rcon_payload(string_array)
                

                # if response_required == True : deal with response now, otherwise the request is considered dealt with.
                client_connection.sendall(response_data)
##################################################
#   PREVIOUS CODE IN 'listen()' MAIN LOOP: END   #
##################################################

# should we define each PUBLIC_API_ method as (r) / (rw)

# send me a lawsuit because gosh dang is this class getting some action
#def __new__(cls):
# !! OI !! Instead of fluffing around with creating instances of dependants purely just so we can access their methods,
# lets start moving toward a controller instance. in fact maybe treating these classes as being primarily controllers and secondarily
# as object representations of their counterparts instead of the other way round is the way to go. 
#
# - idea: upon __init__, instantiate all dependancies available to us as controller interfaces, i.e.
# self.map = Map()
# self.client = Client() # representational client
#
# and then, we can have actual slots for actual player instances if we need to:
# self.loaded_clients = []
# self.loaded_map = Map()
#
#
# alternatively,
# split into two classes: [ServerController] and [Server]
# [ServerController]    To be used for all 'get' and 'set' API calls, (all methods reside on the controller). Can be a subclass of a super [Controller] daddy class
# [ServerController] is the big sexy daddy that all other xcon classes reside underneath, and is the class that contains the methods to actually send the packets to servers
# [ServerController] which is what makes this sex icon of a class something pretty special
# [ServerController]    To craft the packets exactly how your server likes them (mmm yeah), you'll need to overriding the respective methods in class
# [ServerController] > gsc = ServerController
# [ServerController] > gsc.client.pet.suicide(server_ip=10.0.0.21,server_port=2313,rcon_key='yamum',client_id=3,pet_id=432)
# [ServerController] - each [<xcon>Controller] is a representation of the accompanying <xcon> namespace
# [Server] to be used if a object representation of the actual server's gamestate is required. i.e. fleshed-out client lists, full cvar report, etc.
# [Server] can contain methods to to convert the object representation of itself into a json http payload
#

# Magic sauce is BYTE255 BYTE255 BYTE255 BYTE255 BYTE2 <message bytes>
# BYTE255 = 0xff (255 in decimal / 11111111)
# BYTE2   = 0x2  (2 in decimal   / 00000010)
# construct byte arrays (rcon magic 5-byte header + message encoded in ASCII bytes)
user_input_bytes = bytearray(message,'ascii')
rcon_header_bytes = bytearray()

# 4x 0xff bytes followed by 1x 0x2 byte
for _ in range(4) : rcon_header_bytes.append(0xff)
rcon_header_bytes.append(0x2)

# combine byte arrays to create the completed payload for UDP packet
payload_bytes = rcon_header_bytes + user_input_bytes

# why split namespaces the way that I did?
#
# seemed logical to split them into dependent subclasses - game servers seem to lend themselves well to being represented like this
# also I thought that for generic method names like "getStatus()" etc., we would run into overlapping names sooner than later


# IF A CALL IS MADE: (i.e., HTTP POST api.mohaa.online/server.game.map.change)
# json: {
#   game = 'mohaa'  
#   ip_address = 10.0.0.10
#   port = 12203
#   rcon_pw = 'supersecret'
#   new_map_name = 'dm/mohdm6'
#}
# 1. Create a new server object
#   - buffered_server = Server('mohaa') ( Empty MOHAA server instance which creates an empty Game(mohaa) instance which creates an empty Map(mohaa) instance )
# 2. Populate the server object
# 3. Call method (i.e. buffered_server.game.map.change(new_map_name,server))
# 4. Send status response (+ actual response, if any) back to client

# HTTP POST api.mohaa.online/map/set/json {
#   ip_address = "10.0.1.132"
#   port = 4411
#   game = 'mohaa'
#   
# }
# ─└┐┌┘│
#                      GameServer                       
# ┌───────────────────────────────────────────────────┐ 
# │                                                   │ 
# │  - Game = MOHAA                                   │ 
# │  - Network protocol = UDP                         │ 
# │  - Version = 1.12                                 │ 
# │  - State = running                                │ 
# │  - RCON key = "qldsucks"                          │ 
# │  - IP = 10.0.0.69                                 │ 
# │  - Port = 12203                                   │ 
# │                                                   │ 
# │                                                   │ 
# │            Map                   Player           │ 
# │ ┌──────────────────────┐ ┌──────────────────────┐ │ 
# │ │ - Name = dm/mohdm6   │ │ - Name = jeer        │ │ 
# │ │ - Type = Deathmatch  │ │ - IP = 10.0.0.42     │ │ 
# │ │                      │ │                      │ │ 
# │ └──────────────────────┘ └──────────────────────┘ │ 
# │          Player                  Player           │ 
# │ ┌──────────────────────┐ ┌──────────────────────┐ │ 
# │ │ - Name = mynemesis   │ │ - Name = yourmum     │ │ 
# │ │ - IP = 10.0.0.7      │ │ - IP = 10.0.0.69     │ │ 
# │ │                      │ │                      │ │ 
# │ └──────────────────────┘ └──────────────────────┘ │ 
# │                                                   │ 
# └───────────────────────────────────────────────────┘ 
