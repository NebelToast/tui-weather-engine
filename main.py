
from decimal import ROUND_UP
import time
import random
from enum import Enum
import curses
import toml

particleType = Enum("symbolType", ["Lightning", "Rain", "Snow"])



class Particle:

    def __init__(self, x:float, y:float, symbol:str, type:particleType, temperatur:int):
        self.x = x
        self.y = y
        self.velocityX = 0.0
        self.velocityY = 0.0
        self.symbol = symbol
        self.particleType = type
        self.temperatur = temperatur







class Physics:
    def __init__(self, wind:float, gravitation:float):
        self.wind = wind
        self.gravitation = gravitation
    
    
    def applyGravitation(self, symbol:Particle,fps):
        match symbol.particleType:
            case particleType.Rain:        
                #symbol.velocityX += self.wind
                symbol.velocityY += self.gravitation
            case particleType.Snow:
                symbol.velocityX += (self.wind *2.5)
                symbol.velocityY += (self.gravitation/10)
                    
        symbol.x += min(symbol.velocityX, 30/fps)
        symbol.y += min(symbol.velocityY, 30/fps)
        

    def applyTemperatur(self, symbol: Particle):
        if symbol.temperatur <=0:
            symbol.symbol ='❉'
            symbol.particleType = particleType.Snow

    def applyPhysics(self, symbol:Particle, fps):
        match symbol.particleType:
            case particleType.Lightning:
                pass
            case default:
                self.applyTemperatur(symbol)
                self.applyGravitation(symbol, fps)
                



class MainLoop:
    def __init__(self,stdscr,configFile:str):
        self.debug = True
        self.config = toml.load(configFile)
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
        self.raindropCount = self.config["MainLoop"]["raindropCount"] * (30/self.fps)
        self.debugstring = f" Drops: {len(self.symbolList)} | FPS: {self.fps}"

        self.height, self.width = stdscr.getmaxyx()
    def inbound(self):
        new_symbol_list = []
        for element in self.symbolList:
            if element.y < self.height:
                if element.x > self.width:
                    element.x %= self.width
                new_symbol_list.append(element)        
        self.symbolList = new_symbol_list
    
    def spawnDrops(self,):
        for i in range(int(self.raindropCount)):
            x = random.randint(0, self.width - 1)
            char = random.choices(['|', '¦','╿'], [5,5,1])[0]
            symbol = Particle(x, 0, char, particleType.Rain, random.randint(0,1))
            
            symbol.velocityY = random.uniform(0.05, 0.15)
            self.symbolList.append(symbol)
    
    def thunder(self):
        symbols = ['█', '▓', '░' ]
        y = 0
        x = random.randint(0, self.width)
        self.thundertimer = 15



        for i in range(0, self.height):
            self.symbolList.append(Particle(random.randint(x-3,x+3 ),y, random.choice(symbols), particleType.Lightning, 10))
            y+=1

    def thunderclear(self):
         if self.thundertimer >0:
                self.thundertimer -=1
                if self.thundertimer == 0:
                    self.symbolList = [s for s in self.symbolList if s.particleType != particleType.Lightning]
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
                match s.particleType:
                    case particleType.Rain:
                        attr = curses.color_pair(1)
                    case particleType.Snow:      
                        attr = curses.color_pair(2)
                    case default:                                 
                        attr = curses.color_pair(3)

                try:
                    self.stdscr.addstr(y-1, x, s.symbol, attr)
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
                        self.symbolList.append(Particle(random.randint(x-2,x+2 ),y, random.choice(symbols), particleType.Lightning, 10))
                        
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
                self.physics.applyPhysics(s, self.fps)
            self.inbound()

            self.draw()

            curses.delay_output(int(max(0, (1 / self.fps) - (time.time() - t)) * 1000))
            self.debugstring = f"{str(round(1/(time.time()- t)))} wind: {str(round(self.physics.wind, 2))} gravitation: {str(round(self.physics.gravitation, 2))} Symbole: {len(self.symbolList)}"

def start_engine(stdscr):
    engine = MainLoop(stdscr, "config.toml")
    engine.loop()

if __name__ == '__main__':
    curses.wrapper(start_engine)