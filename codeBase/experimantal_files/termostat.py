from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class thermostat_data_points:
    current_temp: Any
    setpointTemp: Any
    plus: Any
    minus: Any
    fan_control_speed: Any
    fan_control_mode: Any
    # and so on

@dataclass
class tenPoleSwitch:
    switch1: Any
    switch2: Any
    # and so on

# button representation of thermostat switch:

class ThermostatSwitch(thermostat_data_points, tenPoleSwitch):
    def __init__(self) -> None:
        # to init all dataclasses variables
        super().__init__()


        
