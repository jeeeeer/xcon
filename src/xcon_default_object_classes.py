import typing
import inspect

class SuperDaddyObject:
    '''
    IMPORTANT: any object classes that may end up being represented as an object in a list (i.e. Clients/players)
    must use the 'id' attribute, as they need a JSON-compatible way to be represented.
    '''
    def __init__(self,identity=None):
        if id != None:
            self.identity = identity # to be utilised for internal use. Not to be settable from API calls

    def to_dictionary(self, is_empty_included=False):
        '''
        this function was from when i was retarded and didn't know that foo.__dict__ was a thing LOL,
        however since I realised i'd need to recursively __dict__ everything anyway, and since we
        wanted to strictly check value types (keeping in mind JSON will be the final destination) I
        thought I may as well just roll with it since it had everything I was going to have to re-write anyway.
         ----------------------
        |  JSON   |    Python |
        | --------------------|
        | string  |       str |
        | number  | int/float |
        | object  |      dict |
        | array   |      list |
        | boolean |      bool |
        | null    |      None |
         ---------------------
        '''

        dictionary = {}
        childs = [x for x in inspect.getmembers(self) if not x[0].startswith('_') and type(x[1]).__name__ != 'method']
        print(f"DEBUG : CHILDS = \n{childs}")
        def recursively_convert_element(attribute):
            # I exist because a recursive function was required
            if isinstance(attribute, (str,int,float,bool,type(None))):
                #print(f"DEBUG - ATTRIBUTE")
                return attribute
        
            if isinstance(attribute, list):
                #print(f"DEBUG - LIST")
                return_list = []
                
                for x in attribute:
                    if isinstance(x, SuperDaddyObject):
                        return_list.append({x.identity : x.to_dictionary()})
                    else:
                        return_list += recursively_convert_element(x)
                
                return return_list
        
            if isinstance(attribute, dict):
                #print(f"DEBUG - DICTIONARY")
                return_dict = {}
                for key,value in attribute.items():
                    return_dict[key] = recursively_convert_element(value)
                return return_dict
            
            if isinstance(attribute, SuperDaddyObject):
                return (attribute.to_dictionary())
            # ultimately, returns either a primitive type (i.e. [int/str/bool/float/None]), a list, or a dictionary
            
            # if we've made it this far we've somehow been fed some poopoo data and so its time to fucking rage
            print('ERROR : unexpected type')
            raise 'exception' # if we get this far, it can only mean one thing...
            

        for attribute in childs:
            if attribute[1] not in [None, [], {}]:
                print(f"\n--------------------------------\nDEBUG : Building dictionary.\nattribute name: {attribute[0]}\nattribute value: {attribute[1]}")
                dictionary[attribute[0]] = recursively_convert_element(attribute[1])
        
        return dictionary

class Map(SuperDaddyObject):
    def __init__(self,map_name:str=None,**kwargs):
        super().__init__()
        self.map_name = map_name

class Client(SuperDaddyObject):
    def __init__(self,identity=None,client_ip:str=None,client_port:type[str|int]=None,client_name:type[str|int]=None,**kwargs):
        super().__init__(identity)
        self.client_ip = client_ip
        self.client_port = client_port
        self.client_name = client_name

class Server(SuperDaddyObject):
    def __init__(self, game_id:type[str|int]=None, server_ip:str=None, server_port:type[str|int]=None, server_name:type[str|int]=None, server_state:str=None, version:type[str|int]=None, map:Map=None, clients:list[Client]=[],rcon_key:str=None, **kwargs):
        super().__init__()
        self.game_id = game_id
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_name = server_name
        self.server_state = server_state
        self.version = version
        self.map = map
        self.clients = clients
        self.rcon_key = rcon_key # odd one out? Does this even need to be stored in memory? don't think so - can't we just have it as a required parameter for everything that needs it?
        
class ClientResponse:
    def __init__(self,status_code,data=None):
        self.status_code = status_code
        self.data = data