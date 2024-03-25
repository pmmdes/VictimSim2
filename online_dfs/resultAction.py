# Map Class
# @Author: Cesar A. Tacla, UTFPR
#
## A map representing the explored region of the 2D grid
## The map is a dictionaire whose keys are pairs (x, y).
## The map contains only visited positions.
##
## Associated to each key, there are:
## - the degree of difficulty to access the cell
## - the victim seq number (if there is one) or VS.NO_VICTIM if there is no victim
## - the known actions' results from the cell represented as vector of 8 integers, in the following
##   order: [up, up-right, right, down-right, down, down-left, left, up-left]. Each position may
##   have the following values:
##   VS.UNK  the agent ignores if it is possible to go towards the direction (useful if you want
##           to not use the check_walls_and_lim method of the AbstAgent and save only tried actions)
##   VS.WALL the agent cannot execute the action (there is a wall),
##   VS.END  the agent cannot execute the action (end of grid)
##   VS.CLEAR the agent can execute the action

from vs.constants import VS

class ResultAction:
    def __init__(self):
        self.map_data = {}

    def in_map(self, coord):
        if coord in self.map_data:
            return True

        return False

    def get(self, coord):
        """ @param coord: a pair (x, y), the key of the dictionary"""        
        return self.map_data.get(coord)

    def update(self, coord, action_res_index, action_res_coord):
        """ @param coord: a pair (x, y), the key of the dictionary
            @param action_res_index: indice que corresponde a direção movimentada
            @param action_res_index: a coordenada da ação resultante
        """
        self.map_data.get(coord)[action_res_index] = action_res_coord

    def add(self, coord):
        """ @param coord: a pair (x, y) """

        # cria automaticamente um vetor action_res com coordenadas "desconhecidas"

        self.map_data[coord] = [(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1),(-1,-1)]

    


    
