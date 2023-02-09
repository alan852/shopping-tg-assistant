import re
import os
from typing import TypedDict

from env import ENV, DEFAULT


class UnitCost(TypedDict):
    cost: float
    unit: str


regex: str = None

conversions = {
    'G': {'factor': 1.0 / 1000.0, 'to': 'KG'},
    'ML': {'factor': 1.0 / 1000.0, 'to': 'L'}
}


def config_env():
    global regex
    if regex is None:
        regex_str = os.environ.get(ENV.CAL_UNIT_COST_REGEX, DEFAULT.CAL_UNIT_COST_REGEX) \
            .replace("{units}", os.environ.get(ENV.UNITS, DEFAULT.UNITS))
        regex = rf'{regex_str}'


def cal_unit_cost_from_str(string: str) -> UnitCost | None:
    config_env()
    try:
        match = re.search(regex, string, re.IGNORECASE)
        print(match)
        return cal_unit_cost(float(match.group('cost')), float(match.group('size')), match.group('unit').upper())
    except Exception:
        return None


def cal_unit_cost(cost: float, size: float, unit: str) -> UnitCost:
    unit = unit.upper()
    return {
        'cost': cost / size if unit not in conversions else cost / (size * conversions[unit]['factor']),
        'unit': unit if unit not in conversions else conversions[unit]['to']
    }
