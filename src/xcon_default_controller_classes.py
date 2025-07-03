import typing
import xcon_default_object_classes
game_id = None
# should we define each PUBLIC_API_ method as (r) / (rw)

#def send_payload(rcon_string,server_ip,server_port):
    #pass

class BigSuperDaddyController:
    # wait does this even make sense? We can just declare the send_payload as global in this namespace?

    # I am the big daddy super class and all other controllers are my bitch
    # but fr though I exist so payload sending/receiving methods can be available to all my mangy children
    # Can't imagine there'd ever be a reason to instantiate me that would be kinda weird man
    def __init__(self):
        pass

class ServerController(BigSuperDaddyController):
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
    # $$$$$$$$$$$$$$$$$$$$$$       alternatively       $$$$$$$$$$$$$$$$$$$$$$
    # split into two classes: [ServerController] and [Server]
    # [ServerController]    To be used for all 'get' and 'set' API calls, (all methods reside on the controller). Can be a subclass of a super [Controller] daddy class
    # [ServerController] is the big sexy daddy that all other xcon classes reside underneath, and is the class that contains the methods to actually send the packets to servers
    # [ServerController] which is what makes this sex icon of a class something pretty special
    # [ServerController]    To craft the packets exactly how your server likes them (mmm yeah), you'll need to overriding the respective methods in class
    # [ServerController] > gsc = ServerController
    # [ServerController] > gsc.client.pet.suicide(server_ip=10.0.0.21,server_port=2313,rcon_key='yamum',client_gameid=3,pet_id=432)
    # [ServerController] - each [<xcon>Controller] is a representation of the accompanying <xcon> namespace
    # [Server] to be used if a object representation of the actual server's gamestate is required. i.e. fleshed-out client lists, full cvar report, etc.
    # [Server] can contain methods to to convert the object representation of itself into a json http payload
    #

    def __init__(self,map_controller=None,client_controller=None,**kwargs):
        super().__init__()
        self.game_id = ''
        self.map = map_controller
        self.client = client_controller


    #network_protocol = Server.network_protocol  # should be a static variable

    def getMethods():
        pass

    def getStatus(self,server_ip,server_port,rcon_key=None):
        #1 craft together a nice little payload (i.e. string, along with necessary server args)
        payload = 'rcon yamum status'
        response = self.send_payload()

        
        # now we have to parse / serialise / deserialise (idk man) the response
        # - BUILD DEPENDENT OBJECTS FIRST:
        # .build map object
        # .build client array, filled with client objects
        # .finally, build gameserver object, passing map and client array
        
        # response = gameserverobject.to_dictionary()
        # convert response to .json (should be piss easy)
        # ship off response to caller (might need another or class to deal with sockets for APIServer <-> Client connections? not sure)

class MapController:
    def __init__(self,**kwargs):
        self.game_id = ''
        
    def changeMap(new_map_name: str):
        pass
    
    def getMaplist():
        pass

    print('we good fam fuck you')

class ClientController:
    def __init__(self,**kwargs):
        self.game_id = ''
        
    def kickClient(self,client_gameid: str=None):
        pass


# HTTP POST api.mohaa.online/Mohaa.Map.change() { 
#   server_ip = "10.0.1.132"
#   server_port = 4411
#   new_map_name = 'dm/mohdm6'
#   rcon_key = "yaMum"
# }

# ALTERNATIVELY:
# HTTP POST api.mohaa.online/Mohaa.Map.change(game=mohaa,server_ip=10.0.1.132,server_port=4411,new_map_name=dm/mohdm6,rcon_key=yaMum) {

# HTTP POST api.mohaa.online/Mohaa.Client.kick() {
#   game = 'mohaa'
#   server_ip = "10.0.1.132"
#   server_port = 4411
#   client_ip = '52.119.41.23'
#   client_gameid = '74'
#  -foresight = True
#  -reborn = True
#  -version = '1.12'
#   rcon_key = "yaMum"
# }


# HTTP POST api.mohaa.online/Bf2.getStatus() {
#   server_ip = "10.0.1.132"
#   server_port = 4411
#   rcon_key = "yaMum"
# }

# RETURNS:
# json {
#     Server = {
#         "game": 'mohaa',
#         "server_ip": "10.0.1.132",
#         "server_port": 4411,
#         "version": "1.12",
#         "server_state": 'running',
#         "map" : {
#             "map_name": 'dm/mohdm6'
#             "map_list": 'dm/mohdm6,dm/mohdm7'
#             "game_type": 'Deathmatch'
#         },
#         "players" = [
#             {
#                 client_ip = "40.54.1.220",
#                 client_name = "ass"
#                 client_gameid = 5
#                 client_ping = 420
#                 session_duration = "14732" # seconds
#             },
#         ]
#     }
# }

## ! IMPORTANT !
# new_map = "dm/mohdm6"
# buffered_server.game.map.change_map(new_map,buffered_server)

#retard1 = ServerController()
#retard2 = Map()
#retard3 = Client()

#instances = {
#    "ServerController" : ServerController(),
#    "MapController" : MapController(),
#    "ClientController" : ClientController()
#}