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


# Mapping from enum value to PNG filename filename for each ship part
ship_part_png: dict[Ship_Part, str] = {
    # Standard/Researchable parts
    Ship_Part.ION_CANNON: _part_path("Ion_Cannon.png"),
    Ship_Part.ELECTRON_COMPUTER: _part_path("Electron_Computer.png"),
    Ship_Part.NUCLEAR_DRIVE: _part_path("Nuclear_Drive.png"),
    Ship_Part.NUCLEAR_SOURCE: _part_path("Nuclear_Source.png"),
    Ship_Part.HULL: _part_path("Hull.png"),
    Ship_Part.PLASMA_CANNON: _part_path("Plasma_Cannon.png"),
    Ship_Part.PHASE_SHIELD: _part_path("Phase_Shield.png"),
    Ship_Part.GAUSS_SHIELD: _part_path("Gauss_Shield.png"),
    Ship_Part.PLASMA_MISSILE: _part_path("Plasma_Missile.png"),
    Ship_Part.GLUON_COMPUTER: _part_path("Gluon_Computer.png"),
    Ship_Part.FUSION_DRIVE: _part_path("Fusion_Drive.png"),
    Ship_Part.FUSION_SOURCE: _part_path("Fusion_Source.png"),
    Ship_Part.POSITRON_COMPUTER: _part_path("Positron_Computer.png"),
    Ship_Part.IMPROVED_HULL: _part_path("Improved_Hull.png"),
    Ship_Part.TACHYON_SOURCE: _part_path("Tachyon_Source.png"),
    Ship_Part.TACHYON_DRIVE: _part_path("Tachyon_Drive.png"),
    Ship_Part.ANTIMATTER_CANNON: _part_path("Antimatter_Cannon.png"),
    # Rare parts
    Ship_Part.ABSORPTION_SHIELD: _part_path("Absorption_Shield.png"),
    Ship_Part.FLUX_MISSILE: _part_path("Flux_Missile.png"),
    Ship_Part.SOLITON_CANNON: _part_path("Soliton_Cannon.png"),
    Ship_Part.ZEROPOINT_SOURCE: _part_path("Zero-Point_Source.png"),
    Ship_Part.TRANSITION_DRIVE: _part_path("Transition_Drive.png"),
    Ship_Part.SENTIENT_HULL: _part_path("Sentient_Hull.png"),
    Ship_Part.CONIFOLD_FIELD: _part_path("Conifold_Field.png"),
    Ship_Part.RIFT_CANNON: _part_path("Rift_Cannon.png"),
    # Discovery tiles
    Ship_Part.ION_MISSILE: _part_path("Ion_Missile.png"),
    Ship_Part.ANTIMATTER_MISSILE: _part_path("Antimatter_Missile.png"),
    Ship_Part.SOLITON_MISSILE: _part_path("Soliton_Missile.png"),
    Ship_Part.AXION_COMPUTER: _part_path("Axion_Computer.png"),
    Ship_Part.CONFORMAL_DRIVE: _part_path("Conformal_Drive.png"),
    Ship_Part.FLUX_SHIELD: _part_path("Flux_Shield.png"),
    Ship_Part.INVERSION_SHIELD: _part_path("Inversion_Shield.png"),
    Ship_Part.MORPH_SHIELD: _part_path("Morph_Shield.png"),
    Ship_Part.PLASMA_TURRET: _part_path("Plasma_Turret.png"),
    # Guardian/Ancient/GCDS parts
    Ship_Part.ION_TURRET: _part_path("Ion_Turret.png"),
    Ship_Part.ION_DISRUPTOR: _part_path("Ion_Disruptor.png"),
    Ship_Part.RIFT_CONDUCTOR: _part_path("Rift_Conductor.png"),
    Ship_Part.JUMP_DRIVE: _part_path("Jump_Drive.png"),
    Ship_Part.SHARD_HULL: _part_path("Shard_Hull.png"),
    Ship_Part.HYPERGRID_SOURCE: _part_path("Hypergrid_Source.png"),
    Ship_Part.SOLITON_CHARGER: _part_path("Soliton_Charger.png"),
    Ship_Part.NONLINEAR_DRIVE: _part_path("Nonlinear_Drive.png"),
    Ship_Part.MUON_SOURCE: _part_path("Muon_Source.png"),
}
