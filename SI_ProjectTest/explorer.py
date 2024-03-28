from asyncio.windows_events import NULL
from msilib import sequence
from shutil import move
import sys
import os
import random
import math
import copy
from vs.abstract_agent import AbstAgent
from abc import ABC, abstractmethod
from vs.constants import VS

class Explorer(AbstAgent):
    def __init__(self, env, config_file, seq):
        """ Construtor do agente on-line dfs
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        """
        
        super().__init__(env, config_file)
        self.set_state(VS.ACTIVE)
        self.x = 0
        self.y = 0
        
        ## Primeira tentativa
        #if seq == 1:
        #    self.sequence = [0, 1, 2, 3, 4, 5, 6, 7] 
        #elif seq == 2:
        #    self.sequence = [7, 6, 5, 4, 3, 2, 1, 0]
        #elif seq == 3:
        #    self.sequence = [3, 2, 1, 0, 7, 6, 5, 4]
        #elif seq == 4:
        #    self.sequence = [5, 4, 3, 2, 1, 0, 7, 6]

        #if seq == 1:
        #    self.sequence = [3, 6, 1, 4, 7, 2, 5, 0]
        #elif seq == 2:
        #    self.sequence = [7, 2, 5, 0, 3, 6, 1, 4]
        #elif seq == 3:
        #    self.sequence = [1, 6, 3, 0, 5, 2, 7, 4]
        #elif seq == 4:
        #    self.sequence = [5, 2, 7, 4, 1, 6, 3, 0]

        # Neste código tem um problema q trava o agente 4 na posição inicial no terceiro mapa    
        #if seq == 1:
        #    self.sequence = [3, 6, 1, 4, 7, 2, 5, 0]
        #elif seq == 2:
        #    self.sequence = [7, 2, 5, 0, 3, 6, 1, 4]
        #elif seq == 3:
        #    self.sequence = [1, 4, 7, 2, 5, 0, 3, 6]
        #elif seq == 4:
        #    self.sequence = [5, 0, 3, 6, 1, 4, 7, 2]
        
        # Agente 4 n fica travado, mas no quarto mapa perde 2 vitimas
        if seq == 1:
            self.sequence = [3, 6, 1, 4, 7, 2, 5, 0]
        elif seq == 2:
            self.sequence = [7, 2, 5, 0, 3, 6, 1, 4]
        elif seq == 3:
            self.sequence = [1, 4, 7, 2, 5, 0, 3, 6]
        elif seq == 4:
            self.sequence = [5, 2, 7, 4, 1, 6, 3, 0]
        """
        AC_INCR = {
        0: (0, -1),  #  u: Up
        1: (1, -1),  # ur: Upper right diagonal
        2: (1, 0),   #  r: Right
        3: (1, 1),   # dr: Down right diagonal
        4: (0, 1),   #  d: Down
        5: (-1, 1),  # dl: Down left left diagonal
        6: (-1, 0),  #  l: Left
        7: (-1, -1)  # ul: Up left diagonal
        }
        """
        
        self.untried = {(self.x,self.y) : copy.copy(self.sequence)}
        self.unbacktracked = {(self.x,self.y) : [0,0]}
        
        
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""
        
        consumed_time = self.TLIM - self.get_rtime()
        if consumed_time < self.get_rtime():   
            if not (self.x,self.y) in self.untried:
                self.untried[((self.x,self.y))] = copy.copy(self.sequence)

            if self.untried[(self.x,self.y)]:   
                act = self.untried[(self.x,self.y)].pop(0)
                dire = Explorer.AC_INCR[act]
                result = self.walk(dire[0],dire[1])
                if result == VS.BUMPED:
                    print(f"{self.NAME}: bumped at ({self.x+dire[0]}, {self.y+dire[1]}) , rtime: {self.get_rtime()}")
                elif result == VS.EXECUTED:
                    # update the agent's position relative to the origin
                    print(f"{self.NAME}: moved from ({self.x}, {self.y}) to ({self.x+dire[0]}, {self.y+dire[1]}) , rtime: {self.get_rtime()}")
                    if not (self.x + dire[0], self.y + dire[1]) in self.unbacktracked:
                        self.unbacktracked[(self.x + dire[0],self.y + dire[1])] = (dire[0],dire[1])
                    self.x += dire[0]
                    self.y += dire[1]
                
                    if not self.check_for_victim() == VS.NO_VICTIM:
                        self.read_vital_signals()
            else:
                back = self.unbacktracked[(self.x,self.y)]
                self.walk(-back[0], -back[1])
                print(f"{self.NAME}: moved BACK from ({self.x}, {self.y}) to ({self.x-back[0]}, {self.y-back[1]}) , rtime: {self.get_rtime()}")
                self.x -= back[0]
                self.y -= back[1]
        elif self.x == 0 and self.y == 0:
                return False
        else:
            back = self.unbacktracked[(self.x,self.y)]
            self.walk(-back[0], -back[1])
            print(f"{self.NAME}: moved BACK from ({self.x}, {self.y}) to ({self.x-back[0]}, {self.y-back[1]}) , rtime: {self.get_rtime()}")
            self.x -= back[0]
            self.y -= back[1] 

        return True