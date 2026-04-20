"""Hardcoded absolute pixel positions for all 16 Eclipse ship blueprint slots.

Each slot has an exact (x, y, width, height) in pixels, measured from the
top-left corner of the blueprint image. These positions were obtained by
analyzing the outline colors in the blueprint PNG files.

Slot types correspond to the part categories the game uses for validation:
- cannon: ion, plasma, antimatter, soliton, rift cannons
- drive: nuclear, fusion, tachyon, transition drives
- power_source: nuclear, fusion, tachyon, zeropoint sources
- computer: electron, gluon, positron computers
- hull: enhanced, improved, sentient hulls
- shield: phase, gauss, absorption shields
- empty: unused or reserved slot position (no outline on blueprint)

The positions are stored per blueprint filename because each ship type has
a unique blueprint image. The BLUEPRINT_SHIP_TYPE_MAP maps blueprint names
to Ship_type enum values.
"""

from sim.ship_parts_constants import Ship_Part


class SlotType:
    """Slot type labels matching part categories from ship_parts_constants.py.

    These define what kind of part each slot accepts. The labels match the
    'type' field in ship_parts constants (cannon, missile, turret, drive,
    source, computer, hull, shield) for frontend validation display.
    """

    CANNON = "cannon"
    MISSILE = "missile"
    TURRET = "turret"
    DRIVE = "drive"
    SOURCE = "source"
    COMPUTER = "computer"
    HULL = "hull"
    SHIELD = "shield"
    EMPTY = "empty"


SLOT_TYPE_NAMES = {
    SlotType.CANNON: "Cannon",
    SlotType.MISSILE: "Missile",
    SlotType.TURRET: "Turret",
    SlotType.DRIVE: "Drive",
    SlotType.SOURCE: "Source",
    SlotType.COMPUTER: "Computer",
    SlotType.HULL: "Hull",
    SlotType.SHIELD: "Shield",
    SlotType.EMPTY: None,
}


def _make_slot(slot_type, default_part, x, y, width, height):
    """Create a slot definition dict with absolute pixel position.

    Args:
        slot_type: SlotType string value.
        default_part: Ship_Part enum value for the default part, or None.
        x: Left pixel coordinate on the blueprint image.
        y: Top pixel coordinate on the blueprint image.
        width: Slot width in pixels.
        height: Slot height in pixels.

    Returns:
        Slot definition dict with position, type, and default part info.
    """
    return {
        "slot_type": slot_type,
        "default_part": default_part,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
    }


# Blueprint name -> Ship_type enum mapping
BLUEPRINT_SHIP_TYPE_MAP = {
    "Terran_Interceptor": 1,
    "Terran_Cruiser": 2,
    "Terran_Dreadnought": 3,
    "Terran_Starbase": 4,
    "Eridani_Interceptor": 5,
    "Eridani_Cruiser": 6,
    "Eridani_Dreadnought": 7,
    "Eridani_Starbase": 8,
    "Orion_Interceptor": 9,
    "Orion_Cruiser": 10,
    "Orion_Dreadnought": 11,
    "Orion_Starbase": 12,
    "Planta_Interceptor": 13,
    "Planta_Cruiser": 14,
    "Planta_Dreadnought": 15,
    "Planta_Starbase": 16,
}

# Hardcoded slot positions for each blueprint image.
# Key: Blueprint filename (e.g., "Terran_Cruiser.png")
# Value: List of slot dicts with absolute pixel positions measured from
#         the top-left corner of the blueprint image.
#
# Slot layouts are based on analysis of the actual blueprint PNG files.
# Each ship type has a unique arrangement that does NOT conform to a uniform
# grid -- slots have different y-offsets and the columns are not vertically
# aligned. The positions below were measured directly from the blueprint images.
#
# Example Terran Cruiser layout (2 rows, 3 columns, with offsets):
#   Top row:    [Computer]  [Cannon]     (Empty)
#               y=231      y=136        (no slot)
#   Bottom row: [Source]    [Hull]    [Drive]
#               y=465      y=369      y=464
# Note: Computer is LOWER than Cannon (different y), and Hull is HIGHER than
# Source/Drive -- slots are NOT in a rectangular grid.
SLOT_POSITIONS = {
    # === Terran ships ===
    # Terran Interceptor: cross pattern, 4 slots (1 empty at bottom-right)
    "Terran_Interceptor.png": [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 280, 132, 231, 231),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 47, 318, 231, 231),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 280, 365, 232, 231),
        _make_slot(SlotType.EMPTY, None, 513, 318, 231, 231),
    ],
    # Terran Cruiser: 6 slots (1 empty at top-right)
    "Terran_Cruiser.png": [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 30, 231, 232, 231),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 264, 136, 232, 230),
        _make_slot(SlotType.EMPTY, None, 498, 230, 232, 231),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 30, 465, 232, 230),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 265, 369, 232, 230),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 499, 464, 232, 230),
    ],
    # Terran Dreadnought: 8 slots (1 empty at top-right)
    # Right col (Empty/Drive) offset down to align with left col (Computer/Source)
    "Terran_Dreadnought.png": [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 71, 257, 234, 233),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 308, 160, 233, 234),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 544, 161, 234, 233),
        _make_slot(SlotType.EMPTY, None, 780, 257, 234, 233),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 72, 493, 233, 233),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 308, 396, 233, 234),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 544, 397, 234, 233),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 781, 493, 234, 233),
    ],
    # Terran Starbase: 5 slots (2 empty)
    # Center Empty slots properly centered between Computer and Cannon columns
    "Terran_Starbase.png": [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 74, 152, 235, 233),
        _make_slot(SlotType.EMPTY, None, 308, 152, 240, 233),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 548, 153, 234, 233),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 74, 388, 235, 229),
        _make_slot(SlotType.EMPTY, None, 308, 388, 240, 229),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 548, 389, 234, 228),
    ],

    # === Eridani ships (same layouts as Terran, different defaults) ===
    # Eridani Interceptor: cross pattern, 4 slots (1 empty at bottom-right)
    "Eridani_Interceptor.png": [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 267, 140, 231, 231),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 33, 326, 232, 231),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 267, 374, 233, 230),
        _make_slot(SlotType.EMPTY, None, 500, 326, 232, 231),
    ],
    # Eridani Cruiser: 6 slots (1 empty at top-right)
    "Eridani_Cruiser.png": [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 29, 230, 232, 231),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 264, 135, 232, 230),
        _make_slot(SlotType.EMPTY, None, 498, 230, 232, 231),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 29, 463, 232, 230),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 264, 368, 232, 231),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 499, 464, 232, 230),
    ],
    # Eridani Dreadnought: 8 slots (1 empty at top-right)
    # Right col (Empty/Drive) offset down to align with left col (Computer/Source)
    "Eridani_Dreadnought.png": [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 29, 234, 231, 231),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 263, 139, 232, 231),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 498, 140, 232, 231),
        _make_slot(SlotType.EMPTY, None, 732, 234, 232, 231),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 29, 467, 231, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 263, 372, 232, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 498, 373, 232, 231),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 733, 467, 231, 231),
    ],
    # Eridani Starbase: 5 slots (2 empty)
    # Center Empty slots properly centered between Computer and Cannon columns
    "Eridani_Starbase.png": [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 21, 135, 232, 232),
        _make_slot(SlotType.EMPTY, None, 253, 135, 239, 232),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 492, 137, 231, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 21, 369, 233, 231),
        _make_slot(SlotType.EMPTY, None, 253, 369, 239, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 491, 370, 232, 231),
    ],

    # === Orion ships ===
    # Orion Interceptor: cross pattern with shield on right, 4 slots
    "Orion_Interceptor.png": [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 273, 133, 232, 231),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 40, 319, 232, 231),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 274, 366, 232, 231),
        _make_slot(SlotType.SHIELD, Ship_Part.GAUSS_SHIELD, 508, 318, 234, 231),
    ],
    # Orion Cruiser: 6 slots (Gauss shield replaces empty)
    "Orion_Cruiser.png": [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 33, 236, 232, 231),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 267, 141, 233, 231),
        _make_slot(SlotType.SHIELD, Ship_Part.GAUSS_SHIELD, 503, 237, 232, 230),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 34, 470, 232, 230),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 268, 374, 233, 231),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 503, 470, 232, 230),
    ],
    # Orion Dreadnought: 8 slots (Gauss shield replaces empty)
    # Right col (Shield/Drive) offset down to align with left col (Computer/Source)
    "Orion_Dreadnought.png": [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 43, 245, 232, 231),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 277, 150, 232, 231),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 512, 150, 232, 231),
        _make_slot(SlotType.SHIELD, Ship_Part.GAUSS_SHIELD, 747, 245, 232, 231),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 44, 478, 231, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 278, 383, 231, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 512, 384, 232, 231),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 747, 478, 232, 230),
    ],
    # Orion Starbase: 5 slots (Gauss shield replaces empty center)
    # Center Empty slots properly centered between Computer and Cannon columns
    "Orion_Starbase.png": [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 39, 149, 232, 231),
        _make_slot(SlotType.EMPTY, None, 271, 149, 238, 231),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 509, 150, 231, 231),
        _make_slot(SlotType.SHIELD, Ship_Part.GAUSS_SHIELD, 271, 266, 238, 231),
        _make_slot(SlotType.EMPTY, None, 271, 382, 238, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 39, 382, 232, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 509, 384, 231, 231),
    ],

    # === Planta ships ===
    # Planta Interceptor: cross pattern, 3 slots (no bottom-center, no right)
    "Planta_Interceptor.png": [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 269, 128, 232, 230),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 36, 313, 232, 227),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 503, 313, 233, 227),
    ],
    # Planta Cruiser: 5 slots (no computer, empty top-right)
    # X-coordinates scaled proportionally from Terran Cruiser (764px vs 1058px)
    "Planta_Cruiser.png": [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 190, 152, 167, 231),
        _make_slot(SlotType.EMPTY, None, 359, 152, 167, 231),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 21, 247, 167, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 190, 385, 167, 231),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 359, 481, 167, 230),
    ],
    # Planta Dreadnought: 7 slots (no computer, empty top-right)
    # Right col (Empty/Drive) offset down to align with left col (Source)
    "Planta_Dreadnought.png": [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 266, 141, 232, 231),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 500, 142, 232, 231),
        _make_slot(SlotType.EMPTY, None, 735, 236, 232, 231),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 31, 236, 232, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 266, 374, 232, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 500, 375, 232, 231),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 735, 469, 232, 230),
    ],
    # Planta Starbase: 4 slots (no computer on left... actually has computer)
    "Planta_Starbase.png": [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 51, 142, 233, 232),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 521, 144, 231, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 286, 260, 232, 231),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 521, 377, 231, 231),
    ],
}


def get_slot_definitions(ship_type):
    """Get the slot definitions for a ship type.

    Returns the hardcoded slot list for this ship type's blueprint.
    Each slot has absolute pixel position, type, and default part info.

    Args:
        ship_type: Ship_type enum value (1-16) or the integer ID.

    Returns:
        List of slot dicts with keys: slot_type, default_part, x, y,
        width, height.
    """
    blueprint_name = _ship_type_to_blueprint(int(ship_type))
    return SLOT_POSITIONS[blueprint_name]


def _ship_type_to_blueprint(ship_type):
    """Convert a Ship_type enum value to its blueprint filename.

    Args:
        ship_type: Ship_type enum value (1-16) or the integer ID.

    Returns:
        Blueprint filename string (e.g., "Terran_Cruiser.png").

    Raises:
        KeyError: If the ship type has no mapped blueprint.
    """
    blueprint_map = {
        1: "Terran_Interceptor.png",
        2: "Terran_Cruiser.png",
        3: "Terran_Dreadnought.png",
        4: "Terran_Starbase.png",
        5: "Eridani_Interceptor.png",
        6: "Eridani_Cruiser.png",
        7: "Eridani_Dreadnought.png",
        8: "Eridani_Starbase.png",
        9: "Orion_Interceptor.png",
        10: "Orion_Cruiser.png",
        11: "Orion_Dreadnought.png",
        12: "Orion_Starbase.png",
        13: "Planta_Interceptor.png",
        14: "Planta_Cruiser.png",
        15: "Planta_Dreadnought.png",
        16: "Planta_Starbase.png",
    }
    return blueprint_map[ship_type]


def get_slot_positions(ship_type, blueprint_width, blueprint_height):
    """Return the hardcoded pixel positions for slots on a ship blueprint.

    The positions are absolute pixel coordinates measured from the
    top-left corner of the blueprint image. They were obtained by
    analyzing the outline colors in the actual blueprint PNG files.

    Note: blueprint_width and blueprint_height are accepted for API
    compatibility but are not used -- the positions are absolute, not
    computed from image dimensions. Each ship type has a fixed blueprint
    size, so the positions are the same regardless of how the image is
    scaled in the UI.

    Args:
        ship_type: Ship_type enum value (1-16) or the integer ID.
        blueprint_width: Width of the blueprint image in pixels (unused).
        blueprint_height: Height of the blueprint image in pixels (unused).

    Returns:
        List of dicts, one per slot, with keys:
        - slot_type: SlotType string
        - default_part: Ship_Part enum or None
        - x: left pixel coordinate
        - y: top pixel coordinate
        - width: slot width in pixels
        - height: slot height in pixels
    """
    slots = get_slot_definitions(ship_type)
    positions = []
    for slot in slots:
        positions.append({
            "slot_type": slot["slot_type"],
            "default_part": slot["default_part"],
            "x": slot["x"],
            "y": slot["y"],
            "width": slot["width"],
            "height": slot["height"],
        })
    return positions
