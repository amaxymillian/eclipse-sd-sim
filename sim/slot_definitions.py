"""Hardcoded slot definitions for all 16 Eclipse ship types.

Provides a deterministic grid-based layout system for ship blueprint slots,
replacing the fragile pixel-based detection and OCR approaches. Each ship
type has a defined grid (rows x columns) with slot positions, types, and
default part assignments.

Slot types correspond to the part categories the game uses for validation:
- weapon: cannons and missiles (ion, plasma, antimatter, soliton, rift)
- drive: nuclear, fusion, tachyon, transition drives
- power_source: nuclear, fusion, tachyon, zeropoint sources
- computer: electron, gluon, positron computers
- hull: enhanced, improved, sentient hulls
- shield: phase, gauss, absorption shields
- empty: unused or reserved slot position

Grid coordinates are (row, col) with (0, 0) at top-left. All slots use
1x1 grid cells. Empty grid cells represent unused positions on the blueprint.
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


def _make_slot(slot_type, default_part, grid_row=0, grid_col=0):
    """Create a slot definition dict.

    Args:
        slot_type: SlotType enum string value.
        default_part: Ship_Part enum value for the default part, or None.
        grid_row: Grid row position (0-indexed, top to bottom).
        grid_col: Grid column position (0-indexed, left to right).

    Returns:
        Slot definition dict.
    """
    return {
        "slot_type": slot_type,
        "default_part": default_part,
        "grid_row": grid_row,
        "grid_col": grid_col,
    }


def _make_layout(rows, cols, slots):
    """Create a ship layout config dict.

    Args:
        rows: Number of grid rows.
        cols: Number of grid columns.
        slots: List of slot definition dicts.

    Returns:
        Layout config dict.
    """
    return {"grid_rows": rows, "grid_cols": cols, "slots": slots}


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

# Hardcoded slot grid definitions for all 16 ship types.
# Key: Ship_type enum value (1-16).
# Value: dict with grid_rows, grid_cols, and slots list.
#
# Grid layout visualized as (row, col) with (0,0) at top-left:
#
#   Terran Interceptor (cross pattern, 2x3 grid):
#       [W]
#   [S][D][ ]
#
#   Terran Cruiser (3x2 grid):
#   [C][W][ ]
#   [S][H][D]
#
#   Terran Dreadnought (4x2 grid):
#   [C][W][W][ ]
#   [S][H][H][D]
#
#   Terran Starbase (3x2 grid):
#   [C][E][W]
#   [H][E][H]
#
#   Orion Cruiser (3x2 grid):
#   [C][W][G]
#   [S][H][D]
#
#   Planta Interceptor (cross pattern, 2x3 grid):
#       [W]
#   [S][ ][D]
SLOT_DEFINITIONS = {
    # === Terran ships ===
    # Terran Interceptor: cross pattern, 4 slots
    # Grid: [ ][W][ ] / [S][D][ ]
    1: _make_layout(2, 3, [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 1, 0),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 1, 1),
        _make_slot(SlotType.EMPTY, None, 1, 2),
    ]),
    # Terran Cruiser: 6 slots
    # Grid: [C][W][E] / [S][H][D]
    2: _make_layout(2, 3, [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 0, 0),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 1, 0),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 1, 2),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 1),
        _make_slot(SlotType.EMPTY, None, 0, 2),
    ]),
    # Terran Dreadnought: 8 slots
    # Grid: [C][W][W][E] / [S][H][H][D]
    3: _make_layout(2, 4, [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 2),
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 0, 0),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 1, 0),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 1),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 2),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 1, 3),
        _make_slot(SlotType.EMPTY, None, 0, 3),
    ]),
    # Terran Starbase: 5 slots
    # Grid: [C][E][W] / [H][E][H]
    4: _make_layout(2, 3, [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 0, 0),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 2),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 0),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 2),
        _make_slot(SlotType.EMPTY, None, 1, 1),
    ]),

    # === Eridani ships (same layouts as Terran, different defaults) ===
    # Eridani Interceptor: cross pattern, 4 slots
    5: _make_layout(2, 3, [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 1, 0),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 1, 1),
        _make_slot(SlotType.EMPTY, None, 1, 2),
    ]),
    # Eridani Cruiser: 6 slots
    6: _make_layout(2, 3, [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 0, 0),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 1, 0),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 1, 2),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 1),
        _make_slot(SlotType.EMPTY, None, 0, 2),
    ]),
    # Eridani Dreadnought: 8 slots
    7: _make_layout(2, 4, [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 2),
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 0, 0),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 1, 0),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 1),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 2),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 1, 3),
        _make_slot(SlotType.EMPTY, None, 0, 3),
    ]),
    # Eridani Starbase: 5 slots
    8: _make_layout(2, 3, [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 0, 0),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 2),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 0),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 2),
        _make_slot(SlotType.EMPTY, None, 1, 1),
    ]),

    # === Orion ships ===
    # Orion Interceptor: cross pattern with shield on right, 4 slots
    # Grid: [ ][W][ ] / [S][D][G]
    9: _make_layout(2, 3, [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 1, 0),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 1, 1),
        _make_slot(SlotType.SHIELD, Ship_Part.GAUSS_SHIELD, 1, 2),
    ]),
    # Orion Cruiser: 6 slots
    # Grid: [C][W][G] / [S][H][D]
    10: _make_layout(2, 3, [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 0, 0),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 1, 0),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 1, 2),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 1),
        _make_slot(SlotType.SHIELD, Ship_Part.GAUSS_SHIELD, 0, 2),
    ]),
    # Orion Dreadnought: 8 slots
    # Grid: [C][W][W][G] / [S][H][H][D]
    11: _make_layout(2, 4, [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 2),
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 0, 0),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 1, 0),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 1),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 2),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 1, 3),
        _make_slot(SlotType.SHIELD, Ship_Part.GAUSS_SHIELD, 0, 3),
    ]),
    # Orion Starbase: 5 slots (weapon center, shield top-right)
    # Grid: [C][W][G] / [H][E][H]
    12: _make_layout(2, 3, [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 0, 0),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.SHIELD, Ship_Part.GAUSS_SHIELD, 0, 2),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 0),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 2),
    ]),

    # === Planta ships ===
    # Planta Interceptor: cross pattern, 3 slots (no bottom-center slot)
    # Grid: [ ][W][ ] / [S][ ][D]
    13: _make_layout(2, 3, [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 1, 0),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 1, 2),
    ]),
    # Planta Cruiser: 5 slots
    # Grid: [ ][W][E] / [S][H][D]
    14: _make_layout(2, 3, [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 1, 0),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 1, 2),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 1),
        _make_slot(SlotType.EMPTY, None, 0, 2),
    ]),
    # Planta Dreadnought: 7 slots (no computer column)
    # Grid: [ ][W][W][E] / [S][H][H][D]
    15: _make_layout(2, 4, [
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 2),
        _make_slot(SlotType.SOURCE, Ship_Part.NUCLEAR_SOURCE, 1, 0),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 1),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 2),
        _make_slot(SlotType.DRIVE, Ship_Part.NUCLEAR_DRIVE, 1, 3),
        _make_slot(SlotType.EMPTY, None, 0, 3),
    ]),
    # Planta Starbase: 4 slots (weapon center, hulls right, computer left)
    # Grid: [C][W][H] / [E][H][H]
    16: _make_layout(2, 3, [
        _make_slot(SlotType.COMPUTER, Ship_Part.ELECTRON_COMPUTER, 0, 0),
        _make_slot(SlotType.CANNON, Ship_Part.ION_CANNON, 0, 1),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 0, 2),
        _make_slot(SlotType.HULL, Ship_Part.HULL, 1, 2),
    ]),
}


def get_slot_definitions(ship_type):
    """Get the slot grid definitions for a ship type.

    Args:
        ship_type: Ship_type enum value (1-16) or the integer ID.

    Returns:
        Dict with keys: grid_rows, grid_cols, slots.
        Each slot has: slot_type, default_part, grid_row, grid_col.
    """
    return SLOT_DEFINITIONS[int(ship_type)]


def get_slot_positions(ship_type, blueprint_width, blueprint_height):
    """Calculate pixel positions for slots based on grid layout.

    Computes the bounding rectangle for each slot by dividing the
    blueprint width and height into a uniform grid, then mapping
    each slot's grid position to pixel coordinates.

    Args:
        ship_type: Ship_type enum value (1-16) or the integer ID.
        blueprint_width: Width of the blueprint image in pixels.
        blueprint_height: Height of the blueprint image in pixels.

    Returns:
        List of dicts, one per slot, with keys:
        - slot_type: SlotType string
        - default_part: Ship_Part enum or None
        - x: left pixel coordinate
        - y: top pixel coordinate
        - width: slot width in pixels
        - height: slot height in pixels
    """
    layout = get_slot_definitions(ship_type)
    grid_rows = layout["grid_rows"]
    grid_cols = layout["grid_cols"]
    slots = layout["slots"]

    # Reserve margins for blueprint headers/borders
    margin_x = 50
    margin_y = 60
    avail_w = blueprint_width - margin_x * 2
    avail_h = blueprint_height - margin_y * 2

    cell_w = avail_w / grid_cols
    cell_h = avail_h / grid_rows

    positions = []
    for slot in slots:
        x = margin_x + slot["grid_col"] * cell_w
        y = margin_y + slot["grid_row"] * cell_h
        positions.append({
            "slot_type": slot["slot_type"],
            "default_part": slot["default_part"],
            "x": int(x),
            "y": int(y),
            "width": int(cell_w),
            "height": int(cell_h),
            "grid_row": slot["grid_row"],
            "grid_col": slot["grid_col"],
        })

    return positions
