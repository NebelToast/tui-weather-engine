import time
import random
from enum import Enum
import curses
import toml

particleType = Enum("symbolType", ["Lightning", "Rain", "Snow", "Overlay"])


class Config:
    """Manages the configuration of the program, loaded from a TOML file."""

    def __init__(self, configFile: str):
        self.configFile = configFile

    def loadValues(self):
        """Loads the configuration values from the TOML file."""
        Values = toml.load(self.configFile)
        self.fps = Values["MainLoop"]["fps"]
        self.maxSpeed = Values["MainLoop"]["maxSpeed"]
        self.maxParticles = Values["MainLoop"]["maxParticles"]
        self.thundertimer = Values["MainLoop"]["thundertimer"]
        self.raindropCount = Values["MainLoop"]["raindropCount"]
        self.windStrength = Values["Wind"]["strength"]
        self.windVariation = Values["Wind"]["variation"]
        self.clouds = Values["MainLoop"]["clouds"]
        self.gravitation = Values["Physics"]["gravitation"]
        self.temperatur = Values["Physics"]["temperatur"]
        self.increaseGravity = Values["Keybinds"]["increasGravity"]
        self.increaseWind = Values["Keybinds"]["increasWind"]
        self.increaseTemperatur = Values["Keybinds"]["increasTemperatur"]
        self.increaseMaxSpeed = Values["Keybinds"]["increasMaxSpeed"]
        self.decreaseGravity = Values["Keybinds"]["decreasGravity"]
        self.decreasWind = Values["Keybinds"]["decreasWind"]
        self.decreasTemperatur = Values["Keybinds"]["decreasTemperatur"]
        self.decreasMaxSpeed = Values["Keybinds"]["decreasMaxSpeed"]
        self.reload = Values["Keybinds"]["reload"]
        self.saveToConfig = Values["Keybinds"]["saveToConfig"]
        self.displayKeybinds = Values["Keybinds"]["displayKeybinds"]

        return self

    def saveValues(self):
        """Saves the current configuration values to the TOML file."""
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
            },
            "Wind": {"strength": self.windStrength, "variation": self.windVariation},
        }

        with open(self.configFile, "w") as f:
            toml.dump(data_to_save, f)


class Particle:
    """Represents a single particle in the simulation."""

    def __init__(
        self, x: float, y: float, symbol: str, type: particleType, temperatur: int
    ):
        self.x = x
        self.y = y
        self.velocityX = 0.0
        self.windresistance = random.uniform(0.8, 1.2)
        self.velocityY = 0.0
        self.symbol = symbol
        self.particleType = type
        self.temperatur = temperatur


class Wind:
    """Represents the wind in the simulation."""

    def __init__(self, strength: float, Variation: float):
        self.strength = strength
        self.variation = Variation


class Physics:
    """Handles the physics of the simulation."""

    def __init__(self, wind: Wind, gravitation: float, temperatur: int, maxSpeed: float):
        self.wind = wind
        self.gravitation = gravitation
        self.temperatur = temperatur
        self.maxSpeed = maxSpeed

    def applyWind(self, symbol: Particle):
        windVariation = random.uniform(-self.wind.variation, self.wind.variation)
        current_wind_strength = self.wind.strength + windVariation

        symbol.velocityX += current_wind_strength * symbol.windresistance

    def applyGravitation(self, symbol: Particle):
        if symbol.particleType != particleType.Lightning and symbol.particleType != particleType.Overlay:
            symbol.velocityY += self.gravitation
            symbol.x += symbol.velocityX
            symbol.y += min(symbol.velocityY, self.maxSpeed / symbol.windresistance)

    def applyTemperatur(self, symbol: Particle):
        symbol.temperatur += self.temperatur
        if symbol.temperatur <= 0:
            symbol.symbol = "❉"
            symbol.windresistance = random.uniform(1.3, 2.6)
            symbol.particleType = particleType.Snow
        elif symbol.temperatur > 0:
            symbol.symbol = random.choices(["|", "¦", "╿"], [5, 5, 1])[0]
            symbol.particleType = particleType.Rain

    def applyPhysics(self, symbol: Particle):
        match symbol.particleType:
            case particleType.Lightning:
                pass
            case _:
                self.applyWind(symbol)
                self.applyTemperatur(symbol)
                self.applyGravitation(symbol)


class MainLoop:
    """The main loop of the program."""

    def __init__(self, stdscr, configFile: str):

        self.debug = True
        self.config = Config(configFile).loadValues()
        self.stdscr = stdscr
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        self.fps = self.config.fps
        self.maxParticles = self.config.maxParticles
        self.symbolList = []
        curses.start_color()
        curses.use_default_colors()

        self.height, self.width = self.stdscr.getmaxyx()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLUE, -1)
        curses.init_pair(2, curses.COLOR_WHITE, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.wind = Wind(self.config.windStrength, self.config.windVariation)

        self.physics = Physics(
            self.wind,
            self.config.gravitation,
            self.config.temperatur,
            self.config.maxSpeed,
        )
        self.thundertimer = 0
        self.raindropCount = int(self.config.raindropCount)
        self.debugstring = " "
        self.keybindsVisible = False
        self._init_keybinds()

    def _init_keybinds(self):
        self.keybinds = {
            self.config.increaseGravity: self.increase_gravity,
            self.config.decreaseGravity: self.decrease_gravity,
            self.config.increaseWind: self.increase_wind,
            self.config.decreasWind: self.decrease_wind,
            self.config.increaseTemperatur: self.increase_temperatur,
            self.config.decreasTemperatur: self.decrease_temperatur,
            self.config.increaseMaxSpeed: self.increase_max_speed,
            self.config.decreasMaxSpeed: self.decrease_max_speed,
            self.config.reload: self.reload_config,
            self.config.saveToConfig: self.save_config,
            self.config.displayKeybinds: self.toggle_keybinds,
            "t": self.thunder,
            "x": self.exit,
        }

    def increase_gravity(self):
        self.physics.gravitation += 0.01

    def decrease_gravity(self):
        self.physics.gravitation -= 0.01

    def increase_wind(self):
        self.physics.wind.strength += 0.0025

    def decrease_wind(self):
        self.physics.wind.strength -= 0.0025

    def increase_temperatur(self):
        self.physics.temperatur += 1

    def decrease_temperatur(self):
        self.physics.temperatur -= 1

    def increase_max_speed(self):
        self.physics.maxSpeed += 0.1

    def decrease_max_speed(self):
        self.physics.maxSpeed -= 0.1

    def reload_config(self):
        self.config.loadValues()
        self.physics.gravitation = self.config.gravitation
        self.physics.wind.strength = self.config.windStrength
        self.physics.temperatur = self.config.temperatur
        self.physics.maxSpeed = self.config.maxSpeed
        

    def save_config(self):
        self.config.gravitation = self.physics.gravitation
        self.config.windStrength = self.physics.wind.strength
        self.config.temperatur = self.physics.temperatur
        self.config.maxSpeed = self.physics.maxSpeed
        self.config.saveValues()

    def toggle_keybinds(self):
        self.keybindsVisible = not self.keybindsVisible

    def thunder(self):
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        self.stdscr.bkgd(" ", curses.color_pair(1))

        symbols = ["█", "▓", "░"]
        y = 0
        x = random.randint(0, self.width)
        self.thundertimer = 18

        for i in range(0, self.height):
            self.symbolList.append(
                Particle(
                    random.randint(x - 2, x + 2),
                    y,
                    random.choice(symbols),
                    particleType.Lightning,
                    10,
                )
            )

            y += 1
    
    def exit(self):
        exit(0)

    def inbound(self):
        """Removes particles that are out of bounds."""
        new_symbol_list = []
        for element in self.symbolList:
            if element.y < self.height:
                element.x %= self.width
                new_symbol_list.append(element)
        self.symbolList = new_symbol_list

    def spawnDrops(self):
        """Spawns new raindrops."""
        for i in range(self.raindropCount):
            if len(self.symbolList) < self.maxParticles:
                x = random.randint(0, self.width - 1)
                char = random.choices(["|", "¦", "╿"], [5, 5, 1])[0]
                symbol = Particle(x, 0, char, particleType.Rain, 10)

                symbol.velocityY = random.uniform(0.05, 0.15)
                self.symbolList.append(symbol)

    def thunderclear(self):
        """Clears the lightning and resets the colors after a thunder."""
        if self.thundertimer > 0:
            self.thundertimer -= 1
            if self.thundertimer == 0:
                self.symbolList = [
                    s for s in self.symbolList if s.particleType != particleType.Lightning
                ]
                self.stdscr.bkgd(" ", curses.color_pair(0))
                curses.init_pair(1, curses.COLOR_BLUE, -1)
                curses.init_pair(2, curses.COLOR_WHITE, -1)
                curses.init_pair(3, curses.COLOR_YELLOW, -1)
            elif self.thundertimer % 9 in range(3, 8):
                curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
                curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
                curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
                curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            else:
                curses.init_pair(1, curses.COLOR_BLUE, -1)
                curses.init_pair(1, curses.COLOR_BLUE, -1)
                curses.init_pair(2, curses.COLOR_WHITE, -1)
                curses.init_pair(3, curses.COLOR_YELLOW, -1)

    def parse_art_file(self, filepath: str, transparent: bool) -> list:
        """Parses an ASCII art file and returns a list of characters with their positions."""
        parsed_art = []
        with open("Overlay/" + filepath, "r") as f:
            for y_offset, line in enumerate(f):
                for x_offset, symbol in enumerate(line.removesuffix("\n")):
                    if symbol != " " and symbol != "⠀" or not transparent:
                        parsed_art.append((x_offset, y_offset, symbol))

        return parsed_art

    def special(self, fileName, y: int, x: int, transparent: bool):
        """Displays an ASCII art file on the screen."""
        piece = self.parse_art_file(fileName, transparent)
        for elements in piece:
            try:
                final_y = elements[1] + x
                final_x = elements[0] + y
                self.stdscr.addstr(final_y, final_x, elements[2])
            except curses.error:

                pass

    def draw(self):
        """Draws all the particles on the screen."""
        self.stdscr.erase()
        if self.debug:
            self.debugstring.join("test")
            self.stdscr.addstr(
                self.height - 1, 0, self.debugstring[: self.width - 1], curses.A_REVERSE
            )
        for symbol in self.symbolList:
            y, x = int(symbol.y), int(symbol.x)
            match symbol.particleType:
                case particleType.Rain:
                    attr = curses.color_pair(1)
                case particleType.Snow:
                    attr = curses.color_pair(2)
                case _:
                    attr = curses.color_pair(3)

            try:
                self.stdscr.addstr(y - 1, x, symbol.symbol, attr)
            except curses.error:
                pass

    def handle_input(self):
        """Handles user input."""
        try:
            key = self.stdscr.getkey()
            if key in self.keybinds:
                self.keybinds[key]()
        except curses.error:
            return None

    def clouds(self):
        """Displays the clouds overlay."""
        self.special("Cloud.txt", self.width - 18, -2, False)
        self.special("Cloud.txt", 10, -3, False)
        self.special("Cloud.txt", 45, -1, False)
        self.special("Cloud.txt", 80, -2, False)
        self.special("Cloud.txt", 120, -4, False)

    def keybinds_overlay(self):
        self.special("keybinds.txt", self.width // 2 - 25, self.height // 2 - 9, False)
    def loop(self):
        """The main loop of the program."""
        while True:
            self.height, self.width = self.stdscr.getmaxyx()

            t = time.time()
            self.handle_input()

            self.thunderclear()
            self.spawnDrops()

            for symbols in self.symbolList:
                self.physics.applyPhysics(symbols)

            self.inbound()

            self.draw()
            if self.config.clouds:
                self.clouds()
            if self.keybindsVisible:
                self.keybinds_overlay()
            self.stdscr.refresh()
            curses.delay_output(int(max(0, (1 / self.fps) - (time.time() - t)) * 1000))
            self.debugstring = f"{str(round(1/(time.time()- t)))} frametime: {str(round(time.time()- t, 3))} wind: {str(round(self.physics.wind.strength, 1))} gravitation: {str(round(self.physics.gravitation, 2))} Symbole: {len(self.symbolList)} Temperatur: {self.physics.temperatur} MaxSpeed: {round(self.physics.maxSpeed, 3)}"


def start_engine(stdscr):
    engine = MainLoop(stdscr, "config.toml")
    engine.loop()


if __name__ == "__main__":
    curses.wrapper(start_engine)
