from enum import IntEnum


class Ship_Part(IntEnum):
    """Ship part types from Eclipse: Second Dawn for the Galaxy."""
    # Standard/Researchable parts
    ION_CANNON = 1
    ELECTRON_COMPUTER = 2
    NUCLEAR_DRIVE = 3
    NUCLEAR_SOURCE = 4
    HULL = 5
    PLASMA_CANNON = 6
    PHASE_SHIELD = 7
    GAUSS_SHIELD = 8
    PLASMA_MISSILE = 9
    GLUON_COMPUTER = 10
    FUSION_DRIVE = 11
    FUSION_SOURCE = 12
    POSITRON_COMPUTER = 13
    IMPROVED_HULL = 14
    TACHYON_SOURCE = 15
    TACHYON_DRIVE = 16
    ANTIMATTER_CANNON = 17
    # Rare parts
    ABSORPTION_SHIELD = 18
    FLUX_MISSILE = 19
    SOLITON_CANNON = 20
    ZEROPOINT_SOURCE = 21
    TRANSITION_DRIVE = 22
    SENTIENT_HULL = 23
    CONIFOLD_FIELD = 24
    RIFT_CANNON = 43
    # Discovery tiles / Expansion parts
    ION_MISSILE = 25
    ANTIMATTER_MISSILE = 26
    SOLITON_MISSILE = 27
    AXION_COMPUTER = 28
    CONFORMAL_DRIVE = 29
    FLUX_SHIELD = 30
    INVERSION_SHIELD = 31
    MORPH_SHIELD = 32
    PLASMA_TURRET = 33
    # Guardian/Ancient/GCDS parts
    ION_TURRET = 34
    ION_DISRUPTOR = 35
    RIFT_CONDUCTOR = 36
    JUMP_DRIVE = 37
    SHARD_HULL = 38
    HYPERGRID_SOURCE = 39
    SOLITON_CHARGER = 40
    NONLINEAR_DRIVE = 41
    MUON_SOURCE = 42


# Path to the parts directory
PARTS_DIR = "flaskr/static/images/parts"


def _part_path(filename: str) -> str:
    """Return the full path to a part PNG file."""
    return f"{PARTS_DIR}/{filename}"


# Ship parts with stats and PNG paths.
# For parts whose stats are not yet determined, the value is an empty dict.
# Users should fill in the stats manually for those entries.
ship_parts: dict[Ship_Part, dict] = {
    # --- Standard/Researchable parts ---
    Ship_Part.ION_CANNON: {"type": "cannon", "damage": 1, "energy": -1},
    Ship_Part.ELECTRON_COMPUTER: {"type": "computer", "targeting": 1, "energy": 0},
    Ship_Part.NUCLEAR_DRIVE: {"type": "drive", "initiative": 1, "energy": -1},
    Ship_Part.NUCLEAR_SOURCE: {"type": "source", "energy": 3},
    Ship_Part.HULL: {"type": "hull", "armor": 1, "energy": 0},
    Ship_Part.PLASMA_CANNON: {"type": "cannon", "damage": 2, "energy": -2},
    Ship_Part.PHASE_SHIELD: {"type": "shield", "shielding": -2, "energy": -1},
    Ship_Part.GAUSS_SHIELD: {"type": "shield", "shielding": -1, "energy": 0},
    Ship_Part.PLASMA_MISSILE: {"type": "missile", "damage": 2, "times_fired": 2, "energy": -1},
    Ship_Part.GLUON_COMPUTER: {"type": "computer", "targeting": 3, "energy": -2},
    Ship_Part.FUSION_DRIVE: {"type": "drive", "initiative": 2, "energy": -2},
    Ship_Part.FUSION_SOURCE: {"type": "source", "energy": 6},
    Ship_Part.POSITRON_COMPUTER: {"type": "computer", "targeting": 2, "energy": -1},
    Ship_Part.IMPROVED_HULL: {"type": "hull", "armor": 2, "energy": 0},
    Ship_Part.TACHYON_SOURCE: {"type": "source", "energy": 9},
    Ship_Part.TACHYON_DRIVE: {"type": "drive", "initiative": 3, "energy": -3},
    Ship_Part.ANTIMATTER_CANNON: {"type": "cannon", "damage": 4, "energy": -4},
    # --- Rare parts ---
    Ship_Part.ABSORPTION_SHIELD: {"type": "shield", "shielding": -1, "energy": 4},
    Ship_Part.FLUX_MISSILE: {"type": "missile", "damage": 1, "times_fired": 2, "energy": 0},
    Ship_Part.SOLITON_CANNON: {"type": "cannon", "damage": 3, "energy": -3},
    Ship_Part.ZEROPOINT_SOURCE: {"type": "source", "energy": 12},
    Ship_Part.TRANSITION_DRIVE: {"type": "drive", "initiative": 0, "energy": 0},
    Ship_Part.SENTIENT_HULL: {"type": "hull", "armor": 1, "targeting": 1, "energy": 0},
    Ship_Part.CONIFOLD_FIELD: {"type": "hull", "armor": 3, "energy": -2},
    Ship_Part.RIFT_CANNON: {"type": "cannon", "damage": "RIFT_DAMAGE", "energy": -2},
    # --- Discovery tiles ---
    Ship_Part.ION_MISSILE: {"type": "missile", "damage": 1, "times_fired": 2, "initiative": 1, "energy": 0},
    Ship_Part.ANTIMATTER_MISSILE: {"type": "missile", "damage": 4, "times_fired": 1, "energy": 0},
    Ship_Part.SOLITON_MISSILE: {"type": "missile", "damage": 3, "times_fired": 1, "initiative": 1, "energy": 0},
    Ship_Part.AXION_COMPUTER: {},
    Ship_Part.CONFORMAL_DRIVE: {},
    Ship_Part.FLUX_SHIELD: {},
    Ship_Part.INVERSION_SHIELD: {},
    Ship_Part.MORPH_SHIELD: {},
    Ship_Part.PLASMA_TURRET: {},
    # --- Guardian/Ancient/GCDS parts ---
    Ship_Part.ION_TURRET: {},
    Ship_Part.ION_DISRUPTOR: {},
    Ship_Part.RIFT_CONDUCTOR: {},
    Ship_Part.JUMP_DRIVE: {},
    Ship_Part.SHARD_HULL: {},
    Ship_Part.HYPERGRID_SOURCE: {},
    Ship_Part.SOLITON_CHARGER: {},
    Ship_Part.NONLINEAR_DRIVE: {},
    Ship_Part.MUON_SOURCE: {},
}


# Mapping from enum value to PNG filename for each ship part
# PNG filenames use uppercase with underscores to match the enum names
ship_part_png: dict[Ship_Part, str] = {
    # Standard/Researchable parts
    Ship_Part.ION_CANNON: _part_path("ION_CANNON.png"),
    Ship_Part.ELECTRON_COMPUTER: _part_path("ELECTRON_COMPUTER.png"),
    Ship_Part.NUCLEAR_DRIVE: _part_path("NUCLEAR_DRIVE.png"),
    Ship_Part.NUCLEAR_SOURCE: _part_path("NUCLEAR_SOURCE.png"),
    Ship_Part.HULL: _part_path("HULL.png"),
    Ship_Part.PLASMA_CANNON: _part_path("PLASMA_CANNON.png"),
    Ship_Part.PHASE_SHIELD: _part_path("PHASE_SHIELD.png"),
    Ship_Part.GAUSS_SHIELD: _part_path("GAUSS_SHIELD.png"),
    Ship_Part.PLASMA_MISSILE: _part_path("PLASMA_MISSILE.png"),
    Ship_Part.GLUON_COMPUTER: _part_path("GLUON_COMPUTER.png"),
    Ship_Part.FUSION_DRIVE: _part_path("FUSION_DRIVE.png"),
    Ship_Part.FUSION_SOURCE: _part_path("FUSION_SOURCE.png"),
    Ship_Part.POSITRON_COMPUTER: _part_path("POSITRON_COMPUTER.png"),
    Ship_Part.IMPROVED_HULL: _part_path("IMPROVED_HULL.png"),
    Ship_Part.TACHYON_SOURCE: _part_path("TACHYON_SOURCE.png"),
    Ship_Part.TACHYON_DRIVE: _part_path("TACHYON_DRIVE.png"),
    Ship_Part.ANTIMATTER_CANNON: _part_path("ANTIMATTER_CANNON.png"),
    # Rare parts
    Ship_Part.ABSORPTION_SHIELD: _part_path("ABSORPTION_SHIELD.png"),
    Ship_Part.FLUX_MISSILE: _part_path("FLUX_MISSILE.png"),
    Ship_Part.SOLITON_CANNON: _part_path("SOLITON_CANNON.png"),
    Ship_Part.ZEROPOINT_SOURCE: _part_path("ZEROPOINT_SOURCE.png"),
    Ship_Part.TRANSITION_DRIVE: _part_path("TRANSITION_DRIVE.png"),
    Ship_Part.SENTIENT_HULL: _part_path("SENTIENT_HULL.png"),
    Ship_Part.CONIFOLD_FIELD: _part_path("CONIFOLD_FIELD.png"),
    Ship_Part.RIFT_CANNON: _part_path("RIFT_CANNON.png"),
    # Discovery tiles
    Ship_Part.ION_MISSILE: _part_path("ION_MISSILE.png"),
    Ship_Part.ANTIMATTER_MISSILE: _part_path("ANTIMATTER_MISSILE.png"),
    Ship_Part.SOLITON_MISSILE: _part_path("SOLITON_MISSILE.png"),
    Ship_Part.AXION_COMPUTER: _part_path("AXION_COMPUTER.png"),
    Ship_Part.CONFORMAL_DRIVE: _part_path("CONFORMAL_DRIVE.png"),
    Ship_Part.FLUX_SHIELD: _part_path("FLUX_SHIELD.png"),
    Ship_Part.INVERSION_SHIELD: _part_path("INVERSION_SHIELD.png"),
    Ship_Part.MORPH_SHIELD: _part_path("MORPH_SHIELD.png"),
    Ship_Part.PLASMA_TURRET: _part_path("PLASMA_TURRET.png"),
    # Guardian/Ancient/GCDS parts
    Ship_Part.ION_TURRET: _part_path("ION_TURRET.png"),
    Ship_Part.ION_DISRUPTOR: _part_path("ION_DISRUPTOR.png"),
    Ship_Part.RIFT_CONDUCTOR: _part_path("RIFT_CONDUCTOR.png"),
    Ship_Part.JUMP_DRIVE: _part_path("JUMP_DRIVE.png"),
    Ship_Part.SHARD_HULL: _part_path("SHARD_HULL.png"),
    Ship_Part.HYPERGRID_SOURCE: _part_path("HYPERGRID_SOURCE.png"),
    Ship_Part.SOLITON_CHARGER: _part_path("SOLITON_CHARGER.png"),
    Ship_Part.NONLINEAR_DRIVE: _part_path("NONLINEAR_DRIVE.png"),
    Ship_Part.MUON_SOURCE: _part_path("MUON_SOURCE.png"),
}
