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
    '''
    bad_rcon_password = bytearray() # r"bad rcon password" # TODO: Define this
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
        pass # todo: complete this block
    
    # slicing off the 1st 11 bytes, as they are just the usual bytes prepend and not actual data
    if not response_bytes[11:]:
        return xo.ClientResponse(204)
    return xo.ClientResponse(200,response_bytes[11:])

class Map(xo.Map):
    def __init__(self,map_name=None,game_type=None,**kwargs):
        super().__init__(map_name)
        self.game_id = game_id
        self.game_type = game_type

class Client(xo.Client):
    def __init__(self,client_ip:str=None,client_port:type[str|int]=None,client_name:type[str|int]=None,client_gameid:int=None,client_ping:int=None,client_score:int=None,client_lastmsg:int=None,client_qport:int=None,client_rate:int=None,**kwargs):
        super().__init__(id,client_ip,client_port,client_name)
        self.id = f"{client_ip}:{client_port}"
        self.game_id = game_id
        self.client_gameid = client_gameid
        self.client_ping = client_ping
        self.client_score = client_score
        self.client_lastmsg = client_lastmsg
        self.client_qport = client_qport
        self.client_rate = client_rate

class Server(xo.Server):
    def __init__(self,game_id:type[str|int]=None, server_ip:str=None, server_port:type[str|int]=None, rcon_key:str=None, server_state:str=None, version:type[str|int]=None, map:Map=None, clients:list[Client]=[], **kwargs):
        super().__init__(game_id,server_ip,server_port,rcon_key,server_state,version,map,clients,**kwargs)


class ServerController(xc.ServerController):

    def __init__(self,map_controller=None,client_controller=None,**kwargs):
        super().__init__(map_controller,client_controller)
        self.game_id = game_id


    def getMethods():
        return [ApiMethodOutput("! not implemented yet !")]

    def getAll(self):
        pass

    def getInfo(self,server_ip,server_port):
        # 'getstatus' (no rcon needed)
        pass

    def getStatus(self,server_ip,server_port,rcon_key):
        """
        map: obj/obj_team1
        num score ping name            lastmsg address               qport rate
        --- ----- ---- --------------- ------- --------------------- ----- -----
          8     0    0 =[v]= mist            0 119.18.4.211:12203    10991 20000
        """
        rcon_command = f"rcon {rcon_key} status"

        response = send_to_gameserver(rcon_command,server_ip,server_port,True)
        
        response_string = response.data.decode('utf-8')
        response_string_list = response_string.splitlines()
        
        map_name = (re.search(r"^map: (?P<map_name>.*$)",response_string_list[0]).group('map_name')).strip()

        for x in response_string_list[1:]: print(x) # debug
        
        client_states: list[Client] = []
        client_rows = response_string_list[3:]
        
        for line in client_rows:
            if line.strip() == '':
                break
            client_data = line.split()
            client_ip,client_port = client_data[-3].split(':')
            
            client_states.append(Client(
                client_ip      = client_ip,
                client_port    = client_port,
                client_gameid  = client_data[0],
                client_score   = client_data[1],
                client_ping    = client_data[2],
                client_name    = " ".join(client_data[3:-4]),
                client_lastmsg = client_data[-4],
                client_qport   = client_data[-2],
                client_rate    = client_data[-1]
            ))

        server_state = Server(
            map         = Map(map_name),
            clients     = client_states,
            game_id     = self.game_id,
            server_ip   = server_ip,
            server_port = server_port,
            rcon_key    = rcon_key
        )            
        return xo.ClientResponse(200,server_state.to_dictionary())


class MapController(xc.MapController):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.game_id = game_id

    def PUBLIC_API_changeMap(self,new_map_name):
        
        print('! not implemented yet !')
        return [ApiMethodOutput("! not implemented yet !")]
    
    def PUBLIC_API_getMaplist(self):
        print('! not implemented yet !')
        return [ApiMethodOutput("! not implemented yet !")]

    print('we good fam fuck you')

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
        
        if re.search(r"was kicked",response_string):
            return xo.ClientResponse(204)
        else:
            return xo.ClientResponse(500)


    def kickAll(self,server_ip,server_port,rcon_key):
        pass

server_controller = ServerController(MapController(),ClientController())