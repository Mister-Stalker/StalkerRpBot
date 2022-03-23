from files.scripts.npc import NPC


class Battle:
    battle_list = {}
    
    def __init__(self, loc):
        self.location = loc
        
    @staticmethod
    def create_battle(loc, players: list, main_player: int, npc: list):
        Battle.battle_list[loc] = {
            "npc": npc,  # список _id нпс 
            "players": players,  # список id игроков
            "start_players": players,  # список id игроков которые были в начале
            "main_player": main_player  # id "главного" игрока
        }
        
    async def run(self):
        for npc_id in self["npc"]:
            npc = NPC(npc_id)
            npc.attack()
            
        
        
    def __getitem__(self, item):
        return self.battle_list[self.location][item]
    
    def data(self):
        return self.battle_list[self.location]
