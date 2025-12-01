# tui-weather-engine

https://github.com/user-attachments/assets/87f81af3-ba69-4f55-baeb-92f61413b4c0

A simple Python script that displays beautiful, aesthetic weather simulations right in your terminal. This project focuses more on creating a visually pleasing experience than on an accurate meteorological depiction.

## Features

- **Real-time Simulation:** Watch weather patterns like rain, snow (at low temperatures), and lightning come to life in your terminal.
- **Dynamic Controls:** Adjust parameters like wind, gravity, temperature, and speed on the fly.
- **Persistent Configuration:** Save your favorite settings directly to the `config.toml` file.
- **Overlays:** Toggle clouds and view keybinds directly on screen.
- **Nix Support:** Easily set up the development environment using `flake.nix` or `direnv`.

## Installation & Usage

### Using Python
Ensure you have Python installed. You will need the `toml` package.

```bash
pip install toml
python main.py
```
    

## Usage

To start the simulation, simply run the `main.py` script:

```
python main.py
```

## Controls

You can control the simulation in real-time using the following keybinds:

|Key|Action|
|---|---|
|`t`| Call thunder|
|`q`|Decrease wind (blows to left)
|`e`|Increase wind (blows to right)|
|`+`|Increase gravity|
|`-`|Decrease gravity|
|`a`|Increase temperature|
|`d`|Decrease temperature|
|`r`|Reset settings to match `config.toml`|
|`s`|Save current settings to `config.toml`|
|`g`|Decrease max speed|
|`f`|Increase max speed|
|`x`|Exit|
|`h`|Toggle keybinds display|


## Customization

You can customize the default values for the simulation by editing the `config.toml` file. This allows you to set your preferred starting conditions or change the Keybinds.

**Example `config.toml`:**

```
[MainLoop]
fps = 60
thundertimer = 0
raindropCount = 13
maxSpeed = 0.5
maxParticles = 1200
clouds = true
debug = true

[Physics]
gravitation = 0.1
temperatur = 0

[Wind]
strength = 0.0
variation = 0.03

[Keybinds]
increasGravity = '+'
decreasGravity = '-'
increasWind = 'e'
decreasWind = 'q'
increasTemperatur = 'a'
decreasTemperatur = 'd'
increasMaxSpeed = 'f'
decreasMaxSpeed = 'g'
reload = 'r'
saveToConfig = 's'
displayKeybinds = 'h'
```
