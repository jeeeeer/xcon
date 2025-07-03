import typing
import inspect

class SuperDaddyObject:
    '''
    IMPORTANT: any object classes that may end up in a list (i.e. Clients/players) must use the 'id' attribute,
    as they need a JSON-compatible way to be represented.
    '''
    def __init__(self,id=None):
        self.id = id # to be utilised for internal use. Not to be settable from API calls

    def to_dictionary(self):
        '''
        this function was from when i was retarded and didn't know that foo.__dict__ was a thing LOL
        however realised i'd need to recursively __dict__ everything anyway, and since we wanted to strictly
        check value types (keeping in mind JSON will be the final destination) I thought I may as well just
        roll with it since it had everything I was going to have to re-write anyway.
        '''
        # JSON     | Python
        # ---------------------
        # string     str
        # number     int/float
        # object     dict
        # array      list
        # boolean    bool
        # null       'None'

        dictionary = {}
        childs = [x for x in inspect.getmembers(self) if not x[0].startswith('_') and type(x[1]).__name__ != 'method']
            
        def recursively_convert_element(attribute):
            # I exist because a recursive function was required
            if isinstance(attribute, (str,int,float,bool,type(None))):
                return attribute
        
            if isinstance(attribute, list):
                return_list = []
                
                for x in attribute:
                    dictionary = {}
                    print("REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE       ")
                    print(x)
                    if isinstance(x, SuperDaddyObject):
                        print('fuck cunt')
                        dictionary[x.id] = (x.to_dictionary())
                        print(dictionary)
                        return_list.append(dictionary)
                        #return_list += recursively_convert_element(x)
                    else:
                        #bad
                        print('CUNTCUNTCUNTCUNTCUNTCUNTCUNTCUNT\nCUNTCUNTCUNTCUNTCUNTCUNTCUNTCUNT\nCUNTCUNTCUNTCUNTCUNTCUNTCUNTCUNT\nCUNTCUNTCUNTCUNTCUNTCUNTCUNTCUNT\nCUNTCUNTCUNTCUNTCUNTCUNTCUNTCUNT\n')
                        return_list += recursively_convert_element(x)
                
                return return_list
        
            if isinstance(attribute, dict):
                return_dict = {}
                for key,value in attribute.items():
                    return_dict[key] = recursively_convert_element(value)
                return return_dict
            
            if isinstance(attribute, SuperDaddyObject):
                return (attribute.to_dictionary())
            # ultimately, returns either a primitive type (i.e. [int/str/bool/float/None]), a list, or a dictionary
            print('!!!!!!! NONONONONONONO !!!!!!!!!!')
            raise 'exception' # if we get this far, it can only mean one thing...
            # the user is fucking braindead - i.e. we've somehow been fed some poopoo data and so its time to fucking rage


        for attribute in childs :
            print(f"!!! Checking attribute : '{attribute[0]}'")
            print(f"!!! Attribute type     : {str(type(attribute[1]))}")
            print(f"!!! Attribute value    : {attribute[1]}")
            print("------------------------------------------")            
            dictionary[attribute[0]] = recursively_convert_element(attribute[1])
            # not sure if attribute.__name__ works - this might fail / use another attribute perhaps
        
        return dictionary
            


class Map(SuperDaddyObject):
    def __init__(self,map_name:str=None,**kwargs):
        super().__init__()
        self.map_name = map_name

class Client(SuperDaddyObject):
    def __init__(self,id=None,client_ip:str=None,client_port:type[str|int]=None,client_name:type[str|int]=None,**kwargs):
        super().__init__(id)
        self.client_ip = client_ip
        self.client_port = client_port
        self.client_name = client_name


class Server(SuperDaddyObject):
    def __init__(self, game_id:type[str|int]=None, server_ip:str=None, server_port:type[str|int]=None, rcon_key:str=None, server_state:str=None, version:type[str|int]=None, map:Map=None, clients:list[Client]=[], **kwargs):
        super().__init__()
        self.game_id = game_id
        self.rcon_key = rcon_key # odd one out? Does this even need to be stored in memory? don't think so - can't we just have it as a required parameter for everything that needs it?
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_state = server_state
        self.version = version
        self.map = map
        self.clients = clients
        
    #def 

class ApiMethodOutput: #/ ApiMethodTranslation
    def __init__(self,rcon_command,is_server_response_required,is_rcon_priv_required=False,priority=0,**kwargs):
        self.rcon_command = rcon_command
        self.is_server_response_required = is_server_response_required
        self.is_rcon_priv_required = is_rcon_priv_required
        self.priority = priority


class Packet:
    def __init__(self,plaintext_payload=None,encoding=None,protocol=None,**kwargs):
        if encoding != None : self.byte_array = bytearray(plaintext_payload,encoding)
        pass

class ClientResponse:
    def __init__(self,status_code,data=None):
        self.status_code = status_code
        self.data = data