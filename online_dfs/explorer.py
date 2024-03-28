# EXPLORER AGENT
# @Author: Tacla, UTFPR
#
### It walks randomly in the environment looking for victims. When half of the
### exploration has gone, the explorer goes back to the base.

import sys
import os
import random
import math
from abc import ABC, abstractmethod
from vs.abstract_agent import AbstAgent
from vs.constants import VS
from map import Map
from resultAction import ResultAction
from colorama import Fore

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0

class Explorer(AbstAgent):
    def __init__(self, env, config_file, resc, map, type):
        """ Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
        self.walk_stack = Stack()  # a stack to store the movements
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.resc = resc           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0
        self.time_to_comeback = math.ceil(self.TLIM * 0.6)  # set the time to come back to the base
        self.map = map           # create a map for representing the environment
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals

        self.resultActions = ResultAction()
        self.lastMove = (0,0)
        self.type = type



        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())
    
        
    def get_next_position(self):
        """ Randomically, gets the next position that can be explored (no wall and inside the grid)
            There must be at least one CLEAR position in the neighborhood, otherwise it loops forever.
        """
        # Check the neighborhood walls and grid limits
        obstacles = self.check_walls_and_lim()        
    
        # Loop until a CLEAR position is found
        while True:

            # se a posição atual não existe no dicionário de ações
            if not( self.resultActions.in_map((self.x, self.y))):
                self.resultActions.add((self.x,self.y))            
            
            #print(self.resultActions.get((self.x, self.y)).index((-1,-1)))

            # verifica se há direção nao explorada
            try:
                direction = self.resultActions.get((self.x, self.y)).index((-1,-1))
            except ValueError:
                dx, dy = self.lastMove
                dx = dx * -1
                dy = dy * -1                
                return Explorer.ac_incr(self.type)[ list(Explorer.ac_incr(self.type).values()).index((dx,dy)) ]            

            # verifica se a direção é válida para andar
            if obstacles[direction] == VS.CLEAR:

                dx, dy = Explorer.ac_incr(self.type)[direction]
                considered_position = (self.x + dx, self.y + dy)
                
                print(f"considered position {considered_position}" )                                       

                # se a ação resultante de uma determinada direção ainda não tiver sido explorada                    
                if (self.resultActions.get((self.x, self.y))[direction] == (-1,-1) ):

                    # atualiza o índice da direção com a coordenada resultante da ação 
                    self.resultActions.update((self.x, self.y), direction, considered_position)    
                    # explora
                    self.lastMove = Explorer.ac_incr(self.type)[direction]
                    return Explorer.ac_incr(self.type)[direction]                    
                
                # em caso de tentar voltar a uma posição ja visitada, verifica se ainda existem ações não tentadas nela                    
                if ( self.resultActions.in_map(considered_position) ):
                    if ((-1,-1) in self.resultActions.get(considered_position) and (-1,-1) not in self.resultActions.get((self.x, self.y))):
                        self.lastMove = Explorer.ac_incr(self.type)[direction]
                        return Explorer.ac_incr(self.type)[direction]
                    #else:
                        #print(Fore.GREEN + f"No more actions in: {considered_position}")

            
            # consideramos que "bateu" e guardamos esse resultado
            else:                   
                self.resultActions.update((self.x, self.y), direction, VS.WALL)
                #print( Fore.RED + f"{self.resultActions.get((self.x,self.y))}")            
                
        
    def explore(self):
        # get an random increment for x and y       
        dx, dy = self.get_next_position()

        # Moves the body to another position
        rtime_bef = self.get_rtime()
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()

        # Test the result of the walk action
        # Should never bump, but for safe functionning let's test
        if result == VS.BUMPED:
            # update the map with the wall
            self.map.add((self.x + dx, self.y + dy), VS.OBST_WALL, VS.NO_VICTIM, self.check_walls_and_lim())
            print(self.OUTPUT_COLOR + f"{self.NAME}: Wall or grid limit reached at ({self.x + dx}, {self.y + dy})")

        if result == VS.EXECUTED:
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            self.walk_stack.push((dx, dy))

            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy          

            # Check for victims
            seq = self.check_for_victim()
            if seq != VS.NO_VICTIM:
                vs = self.read_vital_signals()
                self.victims[vs[0]] = ((self.x, self.y), vs)
                print(self.OUTPUT_COLOR + f"{self.NAME} Victim found at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
                print(self.OUTPUT_COLOR + f"{self.NAME} Seq: {seq} Vital signals: {vs}")
            
            # Calculates the difficulty of the visited cell
            difficulty = (rtime_bef - rtime_aft)
            if dx == 0 or dy == 0:
                difficulty = difficulty / self.COST_LINE
            else:
                difficulty = difficulty / self.COST_DIAG

            # Update the map with the new cell
            self.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())
            print(self.OUTPUT_COLOR + f"{self.NAME}:at ({self.x}, {self.y}), diffic: {difficulty:.2f} vict: {seq} rtime: {self.get_rtime()}")

        return

    # volta pelo mesmo caminho que andou
    def come_back(self):
        dx, dy = self.walk_stack.pop()
        dx = dx * -1
        dy = dy * -1

        result = self.walk(dx, dy)
        if result == VS.BUMPED:
            print(f"{self.NAME}: when coming back bumped at ({self.x+dx}, {self.y+dy}) , rtime: {self.get_rtime()}")
            return
        
        if result == VS.EXECUTED:
            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy
            #print(f"{self.NAME}: coming back at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
        
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        consumed_time = self.TLIM - self.get_rtime()
        if consumed_time < self.get_rtime():
            #tecla = input(">> ")
            self.explore()
            return True

        # time to come back to the base
        if self.walk_stack.is_empty() or (self.x == 0 and self.y == 0):
            # time to wake up the rescuer
            # pass the walls and the victims (here, they're empty)
            print(f"{self.NAME}: rtime {self.get_rtime()}, invoking the rescuer")
            #input(f"{self.NAME}: type [ENTER] to proceed")
            #self.resc.go_save_victims(self.map, self.victims)
            return False

        self.come_back()
        return True

