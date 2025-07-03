from x_DefaultClasses import *
import x_DefaultClasses

####################################################################################################
# Magic sauce is BYTE255 BYTE255 BYTE255 BYTE255 BYTE2 <message bytes>
# BYTE255 = 0xff (255 in decimal / 11111111)
# BYTE2   = 0x2  (2 in decimal   / 00000010)
# construct byte arrays (rcon magic 5-byte header + message encoded in ASCII bytes)
message = "debug"

user_input_bytes = bytearray(message,'ascii')
rcon_header_bytes = bytearray()

# 4x 0xff bytes followed by 1x 0x2 byte
for _ in range(4) : rcon_header_bytes.append(0xff)
rcon_header_bytes.append(0x2)

# combine byte arrays to create the completed payload for UDP packet
payload_bytes = rcon_header_bytes + user_input_bytes
####################################################################################################

# update from default class
class Mohaa(x_DefaultClasses.GameServer):
    def __init__(self,server_ip=None,server_port=None,rcon_key=None,network_protocol=None,version=None,server_state=None,is_reborn_enabled=False,is_openmohaa_enabled=False,is_foresight_enabled=False,players=[]):
        super().__init__(server_ip,server_port,rcon_key,network_protocol,version,server_state,players)
        self.game = 'mohaa'
        self.features = {
            "is_reborn_enabled" : is_reborn_enabled,
            "is_openmohaa_enabled" : is_openmohaa_enabled,
            "is_foresight_enabled" : is_foresight_enabled
        }

        self.map = Map_extended_by_mohaa(self)
    #def 
    name = __qualname__
    network_protocol = 'UDP'

    def update_client_list(self,action,client_ip,client_name,client_id):
            print('! Not implemented yet !')

    def deserialise_payload(self,command_components):
        #pass
        # join command components. if svr_var, populate with required variables
        # returns:
        # byte array
        # (?) protocol
        return {"protocol" : "udp", "byte_array" : byte_array}


    def PUBLIC_API_getStatus(self):
        return [ApiMethodOutput_extended_by_mohaa(f"status",True,True)]

    def PUBLIC_API_getPublicDetails(self):
        return [ApiMethodOutput_extended_by_mohaa(f"getstatus",True)]


class Map_extended_by_mohaa(x_DefaultClasses.Map):
    def __init__(self,map_name=None,game_type=None):
        super().__init__(map_name)
        if game_type != None : self.game_type = game_type

    def PUBLIC_API_changeGametype(self,new_game_type):
        return [ApiMethodOutput_extended_by_mohaa(f"set g_gametype {new_game_type}",True,True)]

    def PUBLIC_API_changeMap(self,new_map_name):
        return [ApiMethodOutput_extended_by_mohaa(f"map {new_map_name}",True,True)]

    def PUBLIC_API_getMaplist(self):
        return [ApiMethodOutput_extended_by_mohaa("sv_maplist",True,True)]

class Client_extended_by_mohaa(Client):
    def __init__(self,name=None,client_ip=None,client_id=None):
        super().__init__(name,client_ip,client_id)
        

    def PUBLIC_API_kickClient(self,client_id):
        return_object_list = []

        return_object_list += ApiMethodOutput_extended_by_mohaa((f"clientkick {client_id}"),True,True,{},0)
        return_object_list += ApiMethodOutput_extended_by_mohaa((f"ad_clientkick {client_id}"),True,True,{"is_reborn_enabled":True},1)
        
        return return_object_list

    def PUBLIC_API_getClientDetails(self,client_name):
        
        return ApiMethodOutput_extended_by_mohaa((f"dumpuser \"{client_name}\""),True,True)

class ApiMethodOutput_extended_by_mohaa(ApiMethodOutput): #/ ApiMethodTranslation
    def __init__(self, rcon_command,is_gameserver_response_required,is_rcon_priv_required=False, feature_dependencies=None, priority=0):
    #def __init__(self, command, is_rcon_priv_required, is_reborn_required, is_foresight_required, is_openmohaa_required, priority=0):
        super().__init__(rcon_command, is_rcon_priv_required, priority)
        self.feature_dependencies = feature_dependencies