import typing
import xcon_default_object_classes

class BigSuperDaddyController:
    def __init__(self):
        pass

class ServerController(BigSuperDaddyController):
    def __init__(self,map_controller=None,client_controller=None,**kwargs):
        super().__init__()
        self.game_id = ''
        self.map = map_controller
        self.client = client_controller

    def getMethods():
        pass

    def getStatus(self,server_ip,server_port,rcon_key=None):
        pass


class MapController:
    def __init__(self,**kwargs):
        self.game_id = ''
        
    def changeMap(new_map_name: str):
        pass
    
    def getMaplist():
        pass


class ClientController:
    def __init__(self,**kwargs):
        self.game_id = ''
        
    def kickClient(self,client_gameid: str=None):
        pass