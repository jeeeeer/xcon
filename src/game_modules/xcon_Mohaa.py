import xcon_default_controller_classes as xc
import xcon_default_object_classes as xo
import selectors
import typing
import socket
import re

game_id = 'mohaa'
network_protocol = 'udp' # [udp | tcp]

def send_to_gameserver(payload:str,server_ip:str,server_port:type[str|int],is_response_required:bool=True,response_byte_length:int=2500,timeout_seconds:int=2):
    '''
    Magic sauce is BYTE255 BYTE255 BYTE255 BYTE255 BYTE2 <message bytes>
    BYTE255 = 0xff (255 in decimal / 11111111)
    BYTE2   = 0x2  (2 in decimal   / 00000010)
    construct byte arrays (rcon magic 5-byte header + message encoded in ASCII bytes)

    TODO: Implement a time-out threshold
    '''
    bad_rcon_password = bytearray() # TODO: Define this (bytes for "bad password" response)
    payload_byte_frame = bytearray()

    # build pre-pended secret byte sauce
    for _ in range(4) :
        payload_byte_frame.append(0xff)
    payload_byte_frame.append(0x2)
    # add payload to byte frame
    payload_byte_frame.extend((bytearray(payload,'ascii')))
    # no byte appends required for MOHAA
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock: # UDP
        sock.sendto(payload_byte_frame, (server_ip, server_port))
    
        if is_response_required == False:
            return xo.ClientResponse(200)    
        response_bytes = sock.recv(response_byte_length)
    # socket collapses here
    if not response_bytes:
        return xo.ClientResponse(444)
    
    if response_bytes == bad_rcon_password:
        #return {"data" : None,"status_code" : 403}
        pass # TODO: complete this block
    
    # slicing off the 1st 11 bytes, as they are just the usual bytes prepend and not actual data
    if not response_bytes[11:]:
        return xo.ClientResponse(204)
    return xo.ClientResponse(200,response_bytes[11:])

class Map(xo.Map):
    def __init__(self,map_name=None,game_type=None,**kwargs):
        super().__init__(map_name)
        self.game_type = game_type

class Client(xo.Client):
    def __init__(self,identity:type[str|int]=None,client_ip:str=None,client_port:type[str|int]=None,client_name:type[str|int]=None,client_gameid:int=None,client_ping:int=None,client_score:int=None,client_lastmsg:int=None,client_qport:int=None,client_rate:int=None,**kwargs):
        super().__init__(identity,client_ip,client_port,client_name)
        self.identity = identity
        self.client_gameid = client_gameid
        self.client_ping = client_ping
        self.client_score = client_score
        self.client_lastmsg = client_lastmsg
        self.client_qport = client_qport
        self.client_rate = client_rate

class Server(xo.Server):
    def __init__(self,game_id:type[str|int]=None, server_ip:str=None, server_port:type[str|int]=None, server_name:type[str|int]=None, server_state:str=None, version:type[str|int]=None, map:Map=None, clients:list[Client]=[], cvars:dict=None, rcon_key:str=None,**kwargs):
        super().__init__(game_id,server_ip,server_port,server_name,server_state,version,map,clients,rcon_key)
        if cvars != None: self.cvars = cvars

class ServerController(xc.ServerController):
    def __init__(self,map_controller=None,client_controller=None,**kwargs):
        super().__init__(map_controller,client_controller,**kwargs)
        self.game_id = game_id

    def getAllInfo(self):
        pass

    def getBasicInfo(self,server_ip,server_port):
        rcon_command = f"getstatus"

        cvar_dict = {}
        response = send_to_gameserver(rcon_command,server_ip,server_port,True)

        response_string = response.data.decode('utf-8')
        response_string_split = response_string.split('\\')

        if response_string_split[0] != 'Response\n':
            return xo.ClientResponse(400,'Command failed - unexpected response from game server')

        response_string_split = response_string_split[1:]

        for i in range(0,len(response_string_split)-1,2):
            cvar_dict[response_string_split[i]] = response_string_split[i+1]
        
        # return [server object]
        #   - cvars = []
        #   - map = Map(map_name,game_type)
        #   - server_state = 'online'
        #   - version = 
        
        for x in response_string_split:
            print(x)
        
        server_state = Server(
            server_name  = cvar_dict['sv_hostname'],
            map          = Map(map_name=cvar_dict['mapname'], game_type=cvar_dict['g_gametypestring']),
            game_id      = self.game_id,
            server_ip    = server_ip,
            server_port  = server_port,
            cvars        = cvar_dict,
            version      = cvar_dict['version'],
            server_state ='online'
        )

        return xo.ClientResponse(200,server_state.to_dictionary())

    def getStatus(self,server_ip,server_port,rcon_key):
        """
        Sample return from mohaa rcon status:
        > rcon <rcon_key> status

        map: dm/moh_dm6
        num score ping name            lastmsg address               qport rate
        --- ----- ---- --------------- ------- --------------------- ----- -----
          8    13   13 =[v]= mist            0 119.18.4.211:12203    10991 20000
          5    5    27 =[x]= andys mum       0 21.3.119.23:12203     10964 25000
        """
        rcon_command = f"rcon {rcon_key} status"

        response = send_to_gameserver(rcon_command,server_ip,server_port,True)
        
        response_string = response.data.decode('utf-8')
        response_string_list = response_string.splitlines()
        
        map_name = (re.search(r"^map: (?P<map_name>.*$)",response_string_list[0]).group('map_name')).strip()

        for x in response_string_list[1:]: print(x) # debug
        
        client_states: list[Client] = []
        client_rows = response_string_list[3:]
        
        # this is where we parse the game server's string response
        for line in client_rows:
            if line.strip() == '':
                break
            client_data = line.split()
            client_ip,client_port = client_data[-3].split(':')
            client_name = " ".join(client_data[3:-4])
            client_identity = f"{client_ip}:{client_port}"
            client_states.append(Client(client_identity,client_ip,client_port,client_name,client_data[0],client_data[2],client_data[1],client_data[-4],client_data[-2],client_data[-1]))

        server_state = Server(self.game_id,server_ip,server_port,None,'online',None,Map(map_name),client_states,None)
          
        return xo.ClientResponse(200,server_state.to_dictionary())

class MapController(xc.MapController):
    '''
    '''
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.game_id = game_id

    def changeMap(self,server_ip,server_port,new_map_name,rcon_key):
        rcon_command = f"rcon {rcon_key} map {new_map_name}"
        response = send_to_gameserver(rcon_command,server_ip,server_port,False)
        # DISABLING RESPONSE for now as we don't know what bytes we need yet
        #response_string = response.data.decode('utf-8')
        #response_string_list = response_string.splitlines()
        #if re.search(r"success",response_string): # TODO: make this work
        return xo.ClientResponse(200,"Map change command sent successfully")
        #else:
        #    return xo.ClientResponse(400) # TODO: more appropriate status code / exception handling
        
    def getMaplist(self,server_ip,server_port,rcon_key):
        rcon_command = f"rcon {rcon_key} sv_maplist"
        response = send_to_gameserver(rcon_command,server_ip,server_port,True)
        
        response_string = response.data.decode('utf-8')
        response_string_list = response_string.splitlines()

        return_dictionary = {}
        # TODO: construct dictionary from return results
        
        if re.search(r"success",response_string): # TODO: make this work
            return xo.ClientResponse(200, return_dictionary)
        else:
            return xo.ClientResponse(400) # TODO: more appropriate status code / exception handling

class ClientController(xc.ClientController):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.game_id = game_id
        
    def kickClient(self,server_ip:str,server_port:type[str|int],rcon_key,client_gameid:type[str|int]=None,client_name:type[str|int]=None):
        if client_gameid != None:
            payload = f"rcon {rcon_key} clientkick {client_gameid}"
        elif client_name != None:
            payload = f"rcon {rcon_key} kick {client_name}"
        else:
            print("i'm screaming and shitting myself because neither client_gameid nor client_name were provided")
            return
        
        response = send_to_gameserver(payload,server_ip,server_port,True)
        if response.data != None:
            response_string = response.data.decode('utf-8')
        else:
            return xo.ClientResponse(response.status_code)
        
        if re.search(r"was kicked",response_string): # TODO: verify this phrase
            return xo.ClientResponse(204)
        else:
            return xo.ClientResponse(500)


    def kickAll(self,server_ip,server_port,rcon_key):
        pass

server_controller = ServerController(MapController(),ClientController())