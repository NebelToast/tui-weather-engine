import time
import random
from enum import Enum
import curses
import toml

particleType = Enum("symbolType", ["Lightning", "Rain", "Snow"])


class Config:
    def __init__(self,configFile:str):
        self.configFile = configFile
    def loadValues(self):
        Values = toml.load(self.configFile)
        self.fps = Values["MainLoop"]["fps"]
        self.thundertimer = Values["MainLoop"]["thundertimer"]
        self.raindropCount = Values["MainLoop"]["raindropCount"]

        self.wind = Values["Physics"]["wind"]
        self.gravitation = Values["Physics"]["gravitation"]
        self.temperatur = Values["Physics"]["temperatur"]
        return self
    def saveValues(self):
        data_to_save = {
            "MainLoop": {
                "fps": self.fps,
                "thundertimer": self.thundertimer,
                "raindropCount": self.raindropCount,
            },
            "Physics": {
                "wind": self.wind,
                "gravitation": self.gravitation,
                "temperatur": self.temperatur,
            }
        }
        
        with open(self.configFile, "w") as f:
            toml.dump(data_to_save, f)



class Particle:

    def __init__(self, x:float, y:float, symbol:str, type:particleType, temperatur:int):
        self.x = x
        self.y = y
        self.velocityX = 0.0
        self.windresistance = 1
        self.velocityY = 0.0
        self.symbol = symbol
        self.particleType = type
        self.temperatur = temperatur







class Physics:
    def __init__(self, wind:float, gravitation:float, temperatur:int):
        self.wind = wind
        self.gravitation = gravitation
        self.temperatur = temperatur
    
    
    def applyGravitation(self, symbol:Particle,fps):
        if(symbol.particleType != particleType.Lightning):
            symbol.velocityX += self.wind
            symbol.velocityY += self.gravitation
            symbol.x += min(symbol.velocityX, (30/fps)*symbol.windresistance)
            symbol.y += min(symbol.velocityY, (30/fps)/symbol.windresistance)
        
                    


    def applyTemperatur(self, symbol: Particle):
        symbol.temperatur += self.temperatur
        if symbol.temperatur <=0:
            symbol.symbol ='❉'
            symbol.windresistance = 2
            symbol.particleType = particleType.Snow
        elif symbol.temperatur > 0:
            symbol.symbol=random.choices(['|', '¦','╿'], [5,5,1])[0]
            symbol.windresistance = 1
            symbol.particleType = particleType.Rain
            

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
        self.config = Config(configFile).loadValues()
        self.stdscr = stdscr
        curses.curs_set(0)
        stdscr.nodelay(True)
        self.fps = self.config.fps
        self.symbolList = []
        curses.start_color()
        curses.use_default_colors()
        
        self.height, self.width = stdscr.getmaxyx()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLUE,   -1)  # rain
        curses.init_pair(2, curses.COLOR_WHITE,  -1)  # snow
        curses.init_pair(3, curses.COLOR_YELLOW, -1) 
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)

        self.physics = Physics(self.config.wind, self.config.gravitation, self.config.temperatur)
        self.thundertimer = 0
        self.raindropCount = max(1,self.config.raindropCount * (30/self.fps))
        self.debugstring = f" Drops: {len(self.symbolList)} | FPS: {self.fps}"

        self.height, self.width = stdscr.getmaxyx()
    def inbound(self):
        new_symbol_list = []
        for element in self.symbolList:
            if element.y < self.height:
                element.x %= self.width
                new_symbol_list.append(element)        
        self.symbolList = new_symbol_list
    
    def spawnDrops(self,):
        for i in range(int(self.raindropCount)):
            x = random.randint(0, self.width - 1)
            char = random.choices(['|', '¦','╿'], [5,5,1])[0]
            symbol = Particle(x, 0, char, particleType.Rain, 10)
            
            symbol.velocityY = random.uniform(0.05, 0.15)
            self.symbolList.append(symbol)
    

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
            try:
                key = self.stdscr.getkey()
            except:
                return None
            
            match key:
                case 't':
                    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
                    curses.init_pair(1, curses.COLOR_BLUE,   curses.COLOR_BLACK)  
                    curses.init_pair(2, curses.COLOR_WHITE,  curses.COLOR_BLACK)  
                    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
                    
                    self.stdscr.bkgd(' ', curses.color_pair(1))
                    
                    symbols = ['█', '▓', '░' ]
                    y = 0
                    x = random.randint(0, self.width)
                    self.thundertimer = 18* (self.fps/30)



                    for i in range(0, self.height):
                        self.symbolList.append(Particle(random.randint(x-2,x+2 ),y, random.choice(symbols), particleType.Lightning, 10))
                        
                        y+=1
                case '+':
                    self.physics.gravitation += 0.05
                case '-':
                    self.physics.gravitation -= 0.05
                case 'e':
                    self.physics.wind += 0.0005
                case 'q':
                    self.physics.wind -= 0.0005
                case 'a':
                    self.physics.temperatur +=1
                case'd':
                    self.physics.temperatur -=1
                case 'r':
                    self.physics.gravitation = self.config.gravitation
                    self.physics.wind = self.config.wind
                case 's':
                    self.config.gravitation = self.physics.gravitation
                    self.config.wind = self.physics.wind
                    self.config.temperatur = self.physics.temperatur
                    self.config.saveValues()

            


    def loop(self):
        while(True):

            t = time.time()
            self.handle_input()
                 
            self.thunderclear()
            self.spawnDrops()

            for s in self.symbolList:
                self.physics.applyPhysics(s, self.fps)
            self.inbound()

            self.draw()

            curses.delay_output(int(max(0, (1 / self.fps) - (time.time() - t)) * 1000))
            self.debugstring = f"{str(round(1/(time.time()- t)))} wind: {str(round(self.physics.wind, 5))} gravitation: {str(round(self.physics.gravitation, 2))} Symbole: {len(self.symbolList)} Temperatur: {self.physics.temperatur}"
            
def start_engine(stdscr):
    engine = MainLoop(stdscr, "config.toml")
    engine.loop()

if __name__ == '__main__':
    curses.wrapper(start_engine)