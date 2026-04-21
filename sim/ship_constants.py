"""Ship type definitions for Eclipse: Second Dawn for the Galaxy.

Contains the Ship_type enum and ship_types dictionary mapping each ship type
to its configuration: number of slots, base stats, and default part assignments.
"""

from enum import IntEnum
from sim.ship_parts_constants import Ship_Part


class Ship_type(IntEnum):
    """Enum of all 16 ship types across 4 races (Terran, Eridani, Orion, Planta),
    each with 4 classes (Interceptor, Cruiser, Dreadnought, Starbase).
    """
    TERRAN_INTERCEPTOR = 1
    TERRAN_CRUISER = 2
    TERRAN_DREADNOUGHT = 3
    TERRAN_STARBASE = 4
    ERIDANI_INTERCEPTOR = 5
    ERIDANI_CRUISER = 6
    ERIDANI_DREADNOUGHT = 7
    ERIDANI_STARBASE = 8
    ORION_INTERCEPTOR = 9
    ORION_CRUISER = 10
    ORION_DREADNOUGHT = 11
    ORION_STARBASE = 12
    PLANTA_INTERCEPTOR = 13
    PLANTA_CRUISER = 14
    PLANTA_DREADNOUGHT = 15
    PLANTA_STARBASE = 16


# Ship type configurations keyed by Ship_type enum.
# Each entry has:
#   - slots: total number of part slots on the ship
#   - base_initiative: base initiative value before part bonuses
#   - bonus_energy: energy pool bonus (added to part energy sources)
#   - bonus_targeting: base targeting bonus
#   - installed_parts: default parts in each slot (or None for empty slots)
ship_types = {
    Ship_type.TERRAN_INTERCEPTOR: {
        "slots": 4,
        "base_initiative": 2,
        "bonus_energy": 0,
        "bonus_targeting": 0,
        "installed_parts": [
            Ship_Part.ION_CANNON, Ship_Part.NUCLEAR_SOURCE,
            Ship_Part.NUCLEAR_DRIVE, None
        ],
    },
    Ship_type.TERRAN_CRUISER: {
        "slots": 6,
        "base_initiative": 1,
        "bonus_energy": 0,
        "bonus_targeting": 0,
        "installed_parts": [
            Ship_Part.ELECTRON_COMPUTER, Ship_Part.ION_CANNON,
            None, Ship_Part.NUCLEAR_SOURCE, Ship_Part.HULL,
            Ship_Part.NUCLEAR_DRIVE
        ],
    },
    Ship_type.TERRAN_DREADNOUGHT: {
        "slots": 8,
        "base_initiative": 0,
        "bonus_energy": 0,
        "bonus_targeting": 0,
        "installed_parts": [
            Ship_Part.ELECTRON_COMPUTER, Ship_Part.ION_CANNON,
            Ship_Part.ION_CANNON, None, Ship_Part.NUCLEAR_SOURCE,
            Ship_Part.HULL, Ship_Part.HULL, Ship_Part.NUCLEAR_DRIVE
        ],
    },
    Ship_type.TERRAN_STARBASE: {
        "slots": 5,
        "base_initiative": 4,
        "bonus_energy": 3,
        "bonus_targeting": 0,
        "installed_parts": [
            Ship_Part.ELECTRON_COMPUTER, Ship_Part.ION_CANNON,
            None, Ship_Part.HULL, Ship_Part.HULL
        ],
    },
    Ship_type.ERIDANI_INTERCEPTOR: {
        "slots": 4,
        "base_initiative": 2,
        "bonus_energy": 1,
        "bonus_targeting": 0,
        "installed_parts": [
            Ship_Part.ION_CANNON, Ship_Part.NUCLEAR_SOURCE,
            Ship_Part.NUCLEAR_DRIVE, None
        ],
    },
    Ship_type.ERIDANI_CRUISER: {
        "slots": 6,
        "base_initiative": 1,
        "bonus_energy": 1,
        "bonus_targeting": 0,
        "installed_parts": [
            Ship_Part.ELECTRON_COMPUTER, Ship_Part.ION_CANNON,
            None, Ship_Part.NUCLEAR_SOURCE, Ship_Part.HULL,
            Ship_Part.NUCLEAR_DRIVE
        ],
    },
    Ship_type.ERIDANI_DREADNOUGHT: {
        "slots": 8,
        "base_initiative": 0,
        "bonus_energy": 1,
        "bonus_targeting": 0,
        "installed_parts": [
            Ship_Part.ELECTRON_COMPUTER, Ship_Part.ION_CANNON,
            Ship_Part.ION_CANNON, None, Ship_Part.NUCLEAR_SOURCE,
            Ship_Part.HULL, Ship_Part.HULL, Ship_Part.NUCLEAR_DRIVE
        ],
    },
    Ship_type.ERIDANI_STARBASE: {
        "slots": 5,
        "base_initiative": 4,
        "bonus_energy": 3,
        "bonus_targeting": 0,
        "installed_parts": [
            Ship_Part.ELECTRON_COMPUTER, Ship_Part.ION_CANNON,
            None, Ship_Part.HULL, Ship_Part.HULL
        ],
    },
    Ship_type.ORION_INTERCEPTOR: {
        "slots": 4,
        "base_initiative": 3,
        "bonus_energy": 1,
        "bonus_targeting": 0,
        "installed_parts": [
            Ship_Part.ION_CANNON, Ship_Part.NUCLEAR_SOURCE,
            Ship_Part.NUCLEAR_DRIVE, Ship_Part.GAUSS_SHIELD
        ],
    },
    Ship_type.ORION_CRUISER: {
        "slots": 6,
        "base_initiative": 2,
        "bonus_energy": 2,
        "bonus_targeting": 0,
        "installed_parts": [
            Ship_Part.ELECTRON_COMPUTER, Ship_Part.ION_CANNON,
            Ship_Part.GAUSS_SHIELD, Ship_Part.NUCLEAR_SOURCE,
            Ship_Part.HULL, Ship_Part.NUCLEAR_DRIVE
        ],
    },
    Ship_type.ORION_DREADNOUGHT: {
        "slots": 8,
        "base_initiative": 1,
        "bonus_energy": 3,
        "bonus_targeting": 0,
        "installed_parts": [
            Ship_Part.ELECTRON_COMPUTER, Ship_Part.ION_CANNON,
            Ship_Part.ION_CANNON, Ship_Part.GAUSS_SHIELD,
            Ship_Part.NUCLEAR_SOURCE, Ship_Part.HULL,
            Ship_Part.HULL, Ship_Part.NUCLEAR_DRIVE
        ],
    },
    Ship_type.ORION_STARBASE: {
        "slots": 5,
        "base_initiative": 5,
        "bonus_energy": 3,
        "bonus_targeting": 0,
        "installed_parts": [
            Ship_Part.ELECTRON_COMPUTER, Ship_Part.ION_CANNON,
            Ship_Part.HULL, Ship_Part.HULL, Ship_Part.GAUSS_SHIELD
        ],
    },
    Ship_type.PLANTA_INTERCEPTOR: {
        "slots": 3,
        "base_initiative": 2,
        "bonus_energy": 2,
        "bonus_targeting": 1,
        "installed_parts": [
            Ship_Part.ION_CANNON, Ship_Part.NUCLEAR_SOURCE,
            Ship_Part.NUCLEAR_DRIVE
        ],
    },
    Ship_type.PLANTA_CRUISER: {
        "slots": 5,
        "base_initiative": 0,
        "bonus_energy": 2,
        "bonus_targeting": 1,
        "installed_parts": [
            Ship_Part.ION_CANNON, None, Ship_Part.NUCLEAR_SOURCE,
            Ship_Part.HULL, Ship_Part.NUCLEAR_DRIVE
        ],
    },
    Ship_type.PLANTA_DREADNOUGHT: {
        "slots": 7,
        "base_initiative": 0,
        "bonus_energy": 2,
        "bonus_targeting": 1,
        "installed_parts": [
            Ship_Part.ION_CANNON, Ship_Part.ION_CANNON,
            None, Ship_Part.NUCLEAR_SOURCE, Ship_Part.HULL,
            Ship_Part.HULL, Ship_Part.NUCLEAR_DRIVE
        ],
    },
    Ship_type.PLANTA_STARBASE: {
        "slots": 4,
        "base_initiative": 2,
        "bonus_energy": 5,
        "bonus_targeting": 1,
        "installed_parts": [
            Ship_Part.ELECTRON_COMPUTER, Ship_Part.ION_CANNON,
            Ship_Part.HULL, Ship_Part.HULL
        ],
    },
}
