
from decimal import ROUND_UP
from email.policy import default
import time
import os
import random
from enum import Enum
import curses
import math
import toml

symbolType = Enum("symbolType", ["Lightning", "Rain", "Snow"])



class Symbol:

    def __init__(self, x:int, y:int, char, type:symbolType, temperatur:int):
        self.x = x
        self.y = y
        self.velocityX = 0.0
        self.velocityY = 0.0
        self.char = char
        self.type = type
        self.temperatur = temperatur







class Physics:
    def __init__(self, wind:float, gravitation:float):
        self.wind = wind
        self.gravitation = gravitation
    
    
    def applyWind(self, symbol:Symbol):
        symbol.velocityX += self.wind
    
    def applyGravitation(self, symbol:Symbol):
        match symbol.type:
            case symbolType.Rain:        
                symbol.velocityX += self.wind
                symbol.velocityY += self.gravitation
            case symbolType.Snow:
                symbol.velocityX += (self.wind *2.5)
                symbol.velocityY += (self.gravitation/10)
                    
        #symbol.x += math.ceil(symbol.velocityX)
        symbol.x += int(max(-1, min(symbol.velocityX, 1)))

        symbol.y += int(max(-1.4, min(symbol.velocityY, 1.4)))
        

    def applyTemperatur(self, symbol: Symbol):
        if symbol.temperatur <=0:
            symbol.char ='❉'
            symbol.type = symbolType.Snow

    def applyPhysics(self, symbol:Symbol):
        match symbol.type:
            case symbolType.Lightning:
                pass
            case default:
                self.applyTemperatur(symbol)
                self.applyWind(symbol)
                self.applyGravitation(symbol)
                



class MainLoop:
    def __init__(self,fps:int,stdscr):

        self.debug = True
        self.config = toml.load("config.toml")
        self.stdscr = stdscr
        curses.curs_set(0)
        stdscr.nodelay(True)
        self.fps = self.config["MainLoop"]["fps"]
        self.symbolList = []
        curses.start_color()
        curses.use_default_colors()
        
        self.height, self.width = stdscr.getmaxyx()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLUE,   -1)  # rain
        curses.init_pair(2, curses.COLOR_WHITE,  -1)  # snow
        curses.init_pair(3, curses.COLOR_YELLOW, -1) 
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)

        self.physics = Physics(self.config["Physics"]["wind"], self.config["Physics"]["gravitation"])
        self.thundertimer = 0
        self.raindropCount = self.config["MainLoop"]["raindropCount"]
        self.debugstring = f" Drops: {len(self.symbolList)} | FPS: {self.fps}"

        self.height, self.width = stdscr.getmaxyx()
    def inbound(self):
        for elements in self.symbolList:
            if elements.x > self.width:
                elements.x = elements.x % self.width
            self.symbolList = [s for s in self.symbolList if 0 <= s.y < self.height]
    
    def spawnDrops(self,):
        for i in range(self.raindropCount):
            x = random.randint(0, self.width - 1)
            char = random.choices(['|', '¦','╿'], [5,5,1])[0]
            symbol = Symbol(x, 0, char, symbolType.Rain, random.randint(0,1))
            
            symbol.velocityY = random.uniform(0.05, 0.15)
            self.symbolList.append(symbol)
    
    def thunder(self):
        symbols = ['█', '▓', '░' ]
        y = 0
        x = random.randint(0, self.width)
        self.thundertimer = 15



        for i in range(0, self.height):
            self.symbolList.append(Symbol(random.randint(x-3,x+3 ),y, random.choice(symbols), symbolType.Lightning, 10))
            y+=1

    def thunderclear(self):
         if self.thundertimer >0:
                self.thundertimer -=1
                if self.thundertimer == 0:
                    self.symbolList = [s for s in self.symbolList if s.type != symbolType.Lightning]
                    self.stdscr.bkgd(' ', curses.color_pair(0))
                    curses.init_pair(1, curses.COLOR_BLUE,   -1)  
                    curses.init_pair(2, curses.COLOR_WHITE,  -1)  
                    curses.init_pair(3, curses.COLOR_YELLOW, -1) 
                elif self.thundertimer%9 in range(3,8):
                    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
                    curses.init_pair(1, curses.COLOR_BLUE,   curses.COLOR_BLACK)  
                    curses.init_pair(2, curses.COLOR_WHITE,  curses.COLOR_BLACK)  
                    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
                else:
                    curses.init_pair(1, curses.COLOR_BLUE, -1)
                    curses.init_pair(1, curses.COLOR_BLUE,   -1)  
                    curses.init_pair(2, curses.COLOR_WHITE,  -1)  
                    curses.init_pair(3, curses.COLOR_YELLOW, -1)



    def draw(self):


            self.stdscr.erase()
            if self.debug == True:
                self.debugstring.join("test")
                self.stdscr.addstr(self.height-1, 0, self.debugstring[:self.width-1], curses.A_REVERSE)
            for s in self.symbolList:
                y, x = int(s.y), int(s.x)
                match s.type:
                    case symbolType.Rain:
                        attr = curses.color_pair(1)
                    case symbolType.Snow:      
                        attr = curses.color_pair(2)
                    case default:                                 
                        attr = curses.color_pair(3)

                try:
                    self.stdscr.addstr(y-1, x, s.char, attr)
                except curses.error:
                    pass

    def handle_input(self):
            
            key = self.stdscr.getch()
            match key:
                case 116:
                    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
                    curses.init_pair(1, curses.COLOR_BLUE,   curses.COLOR_BLACK)  
                    curses.init_pair(2, curses.COLOR_WHITE,  curses.COLOR_BLACK)  
                    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
                    
                    self.stdscr.bkgd(' ', curses.color_pair(1))
                    
                    symbols = ['█', '▓', '░' ]
                    y = 0
                    x = random.randint(0, self.width)
                    self.thundertimer = 18



                    for i in range(0, self.height):
                        self.symbolList.append(Symbol(random.randint(x-2,x+2 ),y, random.choice(symbols), symbolType.Lightning, 10))
                        
                        y+=1
                case 43:
                    self.physics.gravitation += 0.05
                case 45:
                    self.physics.gravitation -= 0.05
 

            return key
            


    def loop(self):
        while(True):
            t = time.time()
            if not self.handle_input():
                 break
            self.thunderclear()
            self.spawnDrops()

            for s in self.symbolList:
                self.physics.applyPhysics(s)
            self.inbound()

            self.draw()
            time.sleep(max(0,(1/self.fps)- (time.time()-t)))
            self.debugstring = f"{str(round(1/(time.time()- t)))} wind: {str(round(self.physics.wind, 2))} gravitation: {str(round(self.physics.gravitation, 2))} Symbole: {len(self.symbolList)}"
def start_engine(stdscr):
    engine = MainLoop(fps=30, stdscr=stdscr)
    engine.loop()

if __name__ == '__main__':
    curses.wrapper(start_engine)