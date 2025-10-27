import time
import random
from enum import Enum
import curses
import toml
import os

particleType = Enum("symbolType", ["Lightning", "Rain", "Snow", "Overlay"])


class Config:
    def __init__(self,configFile:str):
        self.configFile = configFile

    def loadValues(self):
        Values = toml.load(self.configFile)
        self.fps = Values["MainLoop"]["fps"]
        self.maxSpeed = Values["MainLoop"]["maxSpeed"]
        self.maxParticles = Values["MainLoop"]["maxParticles"]
        self.thundertimer = Values["MainLoop"]["thundertimer"]
        self.raindropCount = Values["MainLoop"]["raindropCount"]
        self.windStrength = Values["Wind"]["strength"]
        self.windVariation = Values["Wind"]["variation"]

        self.gravitation = Values["Physics"]["gravitation"]
        self.temperatur = Values["Physics"]["temperatur"]


        
        return self
    
    def saveValues(self):
        data_to_save = {
            "MainLoop": {
                "fps": self.fps,
                "thundertimer": self.thundertimer,
                "raindropCount": self.raindropCount,
                "maxSpeed": self.maxSpeed,
                "maxParticles": self.maxParticles,
            },
            "Physics": {
                "gravitation": self.gravitation,
                "temperatur": self.temperatur,
            },"Wind": {
                "strength": self.windStrength,
                "variation": self.windVariation
            }
        }
        
        with open(self.configFile, "w") as f:
            toml.dump(data_to_save, f)



class Particle:

    def __init__(self, x:float, y:float, symbol:str, type:particleType, temperatur:int):
        self.x = x
        self.y = y
        self.velocityX = 0.0
        self.windresistance = random.uniform(0.8, 1.2)
        self.velocityY = 0.0
        self.symbol = symbol
        self.particleType = type
        self.temperatur = temperatur



class Wind:
    def __init__(self,strength:float, Variation:float):
        self.strength = strength
        self.variation = Variation



class Physics:
    def __init__(self, wind:Wind, gravitation:float, temperatur:int, maxSpeed:float):
        self.wind = wind
        self.gravitation = gravitation
        self.temperatur = temperatur
        self.maxSpeed = maxSpeed

    def applyWind(self, symbol:Particle):
            windVariation = random.uniform(-self.wind.variation, self.wind.variation) 
            current_wind_strength = self.wind.strength + windVariation
                
            symbol.velocityX += current_wind_strength * symbol.windresistance
    
    def applyGravitation(self, symbol:Particle):
        if(symbol.particleType != particleType.Lightning and symbol.particleType != particleType.Overlay):
            symbol.velocityY += self.gravitation
            symbol.x += symbol.velocityX
            symbol.y += min(symbol.velocityY , self.maxSpeed/symbol.windresistance)

                    


    def applyTemperatur(self, symbol: Particle):
        symbol.temperatur += self.temperatur
        if symbol.temperatur <=0:
            symbol.symbol ='❉'
            symbol.windresistance = random.uniform(1.3 ,2.6)
            symbol.particleType = particleType.Snow
        elif symbol.temperatur > 0:
            symbol.symbol=random.choices(['|', '¦','╿'], [5,5,1])[0]
            symbol.particleType = particleType.Rain
            

    def applyPhysics(self, symbol:Particle):
        match symbol.particleType:
            case particleType.Lightning:
                pass
            case default:
                self.applyWind(symbol)
                self.applyTemperatur(symbol)
                self.applyGravitation(symbol)
                



class MainLoop:
    def __init__(self,stdscr,configFile:str):
        
        self.debug = True
        self.config = Config(configFile).loadValues()
        self.stdscr = stdscr
        curses.curs_set(0)
        stdscr.nodelay(True)
        self.fps = self.config.fps
        self.maxParticles = self.config.maxParticles
        self.symbolList = []
        curses.start_color()
        curses.use_default_colors()
        
        self.height, self.width = stdscr.getmaxyx()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLUE,   -1) 
        curses.init_pair(2, curses.COLOR_WHITE,  -1)  
        curses.init_pair(3, curses.COLOR_YELLOW, -1) 
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.wind = Wind(self.config.windStrength, self.config.windVariation)

        self.physics = Physics(self.wind, self.config.gravitation, self.config.temperatur, self.config.maxSpeed)
        self.thundertimer = 0
        self.raindropCount = int(self.config.raindropCount)
        self.debugstring = f" "

    def inbound(self):
        new_symbol_list = []
        for element in self.symbolList:
            if element.y < self.height:
                element.x %= self.width
                new_symbol_list.append(element)        
        self.symbolList = new_symbol_list
    
    def spawnDrops(self,):
        for i in range(self.raindropCount):
            if len(self.symbolList) < self.maxParticles:
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
                    
    def parse_art_file(self,filepath: str) -> list:
        parsed_art = []
        with open("Overlay/"+filepath, 'r') as f:
            for y_offset, line in enumerate(f):
                for x_offset, symbol in enumerate(line.rstrip('\n')):
                            if symbol != ' ' and symbol != '⠀':
                                parsed_art.append((x_offset, y_offset, symbol))

        return parsed_art
    def special(self, fileName, y, x):
        piece = self.parse_art_file(fileName)
        for elements in piece:
            try:
                final_y = elements[1] + x 
                final_x = elements[0] + y
                self.stdscr.addstr(final_y, final_x, elements[2])
            except curses.error:

                pass

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
                    self.thundertimer = 18



                    for i in range(0, self.height):
                        self.symbolList.append(Particle(random.randint(x-2,x+2 ),y, random.choice(symbols), particleType.Lightning, 10))
                        
                        y+=1
                case '+':
                    self.physics.gravitation += 0.01
                case '-':
                    self.physics.gravitation -= 0.01
                case 'e':
                    self.physics.wind.strength += 0.0025
                case 'q':
                    self.physics.wind.strength -= 0.0025
                case 'a':
                    self.physics.temperatur +=1
                case'd':
                    self.physics.temperatur -=1
                case 'f':
                    self.physics.maxSpeed +=0.1
                case'g':
                    self.physics.maxSpeed -=0.1
                case 'r':
                    self.physics.gravitation = self.config.gravitation
                    self.physics.wind.strength = self.config.windStrength
                case 's':
                    self.config.gravitation = self.physics.gravitation
                    self.config.windStrength = self.physics.wind.strength
                    self.config.temperatur = self.physics.temperatur
                    self.config.maxSpeed = self.physics.maxSpeed
                    self.config.saveValues()
                case 'x':
                    exit(0)
            


    def loop(self):
        while(True):
            self.height, self.width = self.stdscr.getmaxyx()

            t = time.time()
            self.handle_input()
                 
            self.thunderclear()
            self.spawnDrops()




            for symbols in self.symbolList:
                self.physics.applyPhysics(symbols)

            self.inbound()

            self.draw()
            self.stdscr.refresh()
            curses.delay_output(int(max(0, (1 / self.fps) - (time.time() - t)) * 1000))
            self.debugstring = f"{str(round(1/(time.time()- t)))} frametime: {str(round(time.time()- t, 3))} wind: {str(round(self.physics.wind.strength, 1))} gravitation: {str(round(self.physics.gravitation, 2))} Symbole: {len(self.symbolList)} Temperatur: {self.physics.temperatur} MaxSpeed: {round(self.physics.maxSpeed, 3)}"
            
def start_engine(stdscr):
    engine = MainLoop(stdscr, "config.toml")
    engine.loop()

if __name__ == '__main__':
    curses.wrapper(start_engine)