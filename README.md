# tui-weather-engine

A simple Python script that displays beautiful, aesthetic weather simulations right in your terminal. This project focuses more on creating a visually pleasing experience than on an accurate meteorological depiction.


## Features

- **Real-time Simulation:** Watch weather patterns like rain and snow come to life in your terminal.
    
- **Dynamic Controls:** Adjust parameters like wind, gravity, and temperature on the fly.
    
- **Persistent Configuration:** Save your favorite settings directly to the `config.toml` file.
    
- **Customizable:** Easily tweak the simulation's behavior through a simple configuration file.
    


## Usage

To start the simulation, simply run the `main.py` script:

```
python main.py
```

## Controls

You can control the simulation in real-time using the following keybinds:

|Key|Action|
|---|---|
|`+`|Increase wind strength|
|`-`|Decrease wind strength|
|`q`|Decrease gravity|
|`e`|Increase gravity|
|`a`|Decrease temperature|
|`d`|Increase temperature|
|`r`|Reset settings to match `config.toml`|
|`s`|Save current settings to `config.toml`|
|`x`|Exit the program|

## Customization

You can customize the default values for the simulation by editing the `config.toml` file. This allows you to set your preferred starting conditions.

**Example `config.toml`:**

```
[MainLoop]

fps = 60

thundertimer = 0

raindropCount = 13

  

[Physics]

gravitation = 0.1

temperatur = 3

  

[Wind]

strength = 0
```
