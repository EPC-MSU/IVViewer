import enum
from typing import Tuple


class Current(enum.IntEnum):
    CURRENT_250UA = 0
    CURRENT_2_5MA = 1
    CURRENT_25MA = 2


class Voltage(enum.IntEnum):
    VOLTAGE_3_3V = 0
    VOLTAGE_5V = 1
    VOLTAGE_12V = 2
    VOLTAGE_1_2V = 3


adjust_scale_table = {
    Voltage.VOLTAGE_1_2V: {
        Current.CURRENT_250UA: (1.5, 0.04),
        Current.CURRENT_2_5MA: (1.5, 0.4),
        Current.CURRENT_25MA: (1.5, 4.0),
    },
    Voltage.VOLTAGE_3_3V: {
        Current.CURRENT_250UA: (4.0, 0.15),
        Current.CURRENT_2_5MA: (4.0, 1.0),
        Current.CURRENT_25MA: (4.0, 10.0),
    },
    Voltage.VOLTAGE_5V: {
        Current.CURRENT_250UA: (6.0, 0.18),
        Current.CURRENT_2_5MA: (6.0, 1.5),
        Current.CURRENT_25MA: (6.0, 15.0),
    },
    Voltage.VOLTAGE_12V: {
        Current.CURRENT_250UA: (14.0, 0.35),
        Current.CURRENT_2_5MA: (14.0, 2.8),
        Current.CURRENT_25MA: (14.0, 28.0),
    }
}

voltage_to_min_border = {
    Voltage.VOLTAGE_1_2V: 0.4,
    Voltage.VOLTAGE_3_3V: 1.0,
    Voltage.VOLTAGE_5V: 1.5,
    Voltage.VOLTAGE_12V: 4.0
}


current_to_min_border = {
    Current.CURRENT_250UA: 0.05,
    Current.CURRENT_2_5MA: 0.5,
    Current.CURRENT_25MA: 5.0
}


def adjust_scale(voltage: Voltage, current: Current) -> Tuple[float, float]:
    return adjust_scale_table[voltage][current]
