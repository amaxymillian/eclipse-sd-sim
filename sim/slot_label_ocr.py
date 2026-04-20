"""OCR-based slot label extraction for Eclipse blueprint images.

Uses pytesseract/Tesseract OCR to extract text labels from within each
slot bounding box on a blueprint PNG, then maps those labels to the
corresponding static slot indices from ship_types.

Falls back to positional ordering if OCR is unavailable or unreliable.
"""

import os
from typing import Optional

from sim.ship_constants import Ship_type, ship_types
from sim.ship_parts_constants import Ship_Part, ship_parts, ship_part_png


# Known part name strings that may appear as slot labels on blueprints.
# Maps normalized OCR output to Ship_Part enum values.
KNOWN_PART_NAMES: dict[str, Ship_Part] = {
    "ION CANNON": Ship_Part.ION_CANNON,
    "ION_CANNON": Ship_Part.ION_CANNON,
    "PLASMA CANNON": Ship_Part.PLASMA_CANNON,
    "PLASMA_CANNON": Ship_Part.PLASMA_CANNON,
    "ANTI Matter Cannon": Ship_Part.ANTIMATTER_CANNON,
    "ANTIMATTER CANNON": Ship_Part.ANTIMATTER_CANNON,
    "ANTIMATTER_CANNON": Ship_Part.ANTIMATTER_CANNON,
    "SOLITON CANNON": Ship_Part.SOLITON_CANNON,
    "SOLITON_CANNON": Ship_Part.SOLITON_CANNON,
    "RIFT CANNON": Ship_Part.RIFT_CANNON,
    "RIFT_CANNON": Ship_Part.RIFT_CANNON,
    "ION MISSILE": Ship_Part.ION_MISSILE,
    "ION_MISSILE": Ship_Part.ION_MISSILE,
    "PLASMA MISSILE": Ship_Part.PLASMA_MISSILE,
    "PLASMA_MISSILE": Ship_Part.PLASMA_MISSILE,
    "FLUX MISSILE": Ship_Part.FLUX_MISSILE,
    "FLUX_MISSILE": Ship_Part.FLUX_MISSILE,
    "ANTIMATTER MISSILE": Ship_Part.ANTIMATTER_MISSILE,
    "ANTIMATTER_MISSILE": Ship_Part.ANTIMATTER_MISSILE,
    "SOLITON MISSILE": Ship_Part.SOLITON_MISSILE,
    "SOLITON_MISSILE": Ship_Part.SOLITON_MISSILE,
    "PLASMA TURRET": Ship_Part.PLASMA_TURRET,
    "PLASMA_TURRET": Ship_Part.PLASMA_TURRET,
    "ION TURRET": Ship_Part.ION_TURRET,
    "ION_TURRET": Ship_Part.ION_TURRET,
    "NUCLEAR DRIVE": Ship_Part.NUCLEAR_DRIVE,
    "NUCLEAR_DRIVE": Ship_Part.NUCLEAR_DRIVE,
    "FUSION DRIVE": Ship_Part.FUSION_DRIVE,
    "FUSION_DRIVE": Ship_Part.FUSION_DRIVE,
    "TACHYON DRIVE": Ship_Part.TACHYON_DRIVE,
    "TACHYON_DRIVE": Ship_Part.TACHYON_DRIVE,
    "TRANSITION DRIVE": Ship_Part.TRANSITION_DRIVE,
    "TRANSITION_DRIVE": Ship_Part.TRANSITION_DRIVE,
    "ELECTRON COMPUTER": Ship_Part.ELECTRON_COMPUTER,
    "ELECTRON_COMPUTER": Ship_Part.ELECTRON_COMPUTER,
    "GLUON COMPUTER": Ship_Part.GLUON_COMPUTER,
    "GLUON_COMPUTER": Ship_Part.GLUON_COMPUTER,
    "POSITRON COMPUTER": Ship_Part.POSITRON_COMPUTER,
    "POSITRON_COMPUTER": Ship_Part.POSITRON_COMPUTER,
    "NUCLEAR SOURCE": Ship_Part.NUCLEAR_SOURCE,
    "NUCLEAR_SOURCE": Ship_Part.NUCLEAR_SOURCE,
    "FUSION SOURCE": Ship_Part.FUSION_SOURCE,
    "FUSION_SOURCE": Ship_Part.FUSION_SOURCE,
    "TACHYON SOURCE": Ship_Part.TACHYON_SOURCE,
    "TACHYON_SOURCE": Ship_Part.TACHYON_SOURCE,
    "ZEROPOINT SOURCE": Ship_Part.ZEROPOINT_SOURCE,
    "ZEROPOINT_SOURCE": Ship_Part.ZEROPOINT_SOURCE,
    "HULL": Ship_Part.HULL,
    "IMPROVED HULL": Ship_Part.IMPROVED_HULL,
    "IMPROVED_HULL": Ship_Part.IMPROVED_HULL,
    "SENTIENT HULL": Ship_Part.SENTIENT_HULL,
    "SENTIENT_HULL": Ship_Part.SENTIENT_HULL,
    "PHASE SHIELD": Ship_Part.PHASE_SHIELD,
    "PHASE_SHIELD": Ship_Part.PHASE_SHIELD,
    "GAUSS SHIELD": Ship_Part.GAUSS_SHIELD,
    "GAUSS_SHIELD": Ship_Part.GAUSS_SHIELD,
    "ABSORPTION SHIELD": Ship_Part.ABSORPTION_SHIELD,
    "ABSORPTION_SHIELD": Ship_Part.ABSORPTION_SHIELD,
    "PHASE SHIELD": Ship_Part.PHASE_SHIELD,
    "PHASE_SHIELD": Ship_Part.PHASE_SHIELD,
    "PHASE SHIELD": Ship_Part.PHASE_SHIELD,
    "RIFT CONDUCTOR": Ship_Part.RIFT_CONDUCTOR,
    "RIFT_CONDUCTOR": Ship_Part.RIFT_CONDUCTOR,
    "ION DISRUPTOR": Ship_Part.ION_DISRUPTOR,
    "ION_DISRUPTOR": Ship_Part.ION_DISRUPTOR,
}


def _normalize_text(text: str) -> str:
    """Normalize OCR-extracted text for matching against known part names.

    Args:
        text: Raw text extracted by OCR from a slot bounding box.

    Returns:
        Normalized uppercase string with underscores replacing spaces.
    """
    return text.upper().strip().replace(" ", "_")


def _match_part_name(normalized: str) -> Optional[Ship_Part]:
    """Try to match normalized text to a known part name.

    Exact matches are tried first, then partial matches against known parts.

    Args:
        normalized: Normalized uppercase text from OCR.

    Returns:
        Ship_Part enum value if matched, or None.
    """
    if normalized in KNOWN_PART_NAMES:
        return KNOWN_PART_NAMES[normalized]

    for key, part_enum in KNOWN_PART_NAMES.items():
        if normalized in key or key in normalized:
            return part_enum

    return None


def _get_blueprint_image_path(blueprint_name: str) -> Optional[str]:
    """Construct the filesystem path to a blueprint image.

    Args:
        blueprint_name: Blueprint name, e.g. 'Terran_Interceptor'.

    Returns:
        Absolute path to the PNG file, or None if not found.
    """
    flask_static = os.path.join(
        os.path.dirname(__file__), "..", "flaskr", "static", "images", "blueprints"
    )
    path = os.path.normpath(os.path.join(os.getcwd(), flask_static, blueprint_name + ".png"))
    if os.path.isfile(path):
        return path
    # Try relative to project root
    project_static = os.path.join(
        os.path.dirname(__file__), "..", "flaskr", "static", "images", "blueprints"
    )
    path = os.path.normpath(os.path.join(os.getcwd(), project_static, blueprint_name + ".png"))
    return None if not os.path.isfile(path) else path


def extract_slot_labels_ocr(blueprint_name: str) -> list[list[str]]:
    """Extract slot label text from a blueprint image using OCR.

    Crops each detected slot region from the blueprint image and runs
    Tesseract OCR to identify the part name label inside each slot.

    Args:
        blueprint_name: Blueprint name, e.g. 'Terran_Interceptor'.

    Returns:
        List of lists of extracted text per slot. Each inner list contains
        the OCR results (strings) for that slot. May be empty if OCR is
        unavailable or the image is not found.
    """
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
    except ImportError:
        return []

    image_path = _get_blueprint_image_path(blueprint_name)
    if not image_path or not os.path.isfile(image_path):
        return []

    try:
        img = Image.open(image_path)
        img_array = np.array(img)
    except Exception:
        return []

    # Use the slot detection to find bounding boxes
    slot_boxes = _detect_slot_boxes(img, img_array)
    if not slot_boxes:
        return []

    # Try to extract text from each slot
    results = []
    for box in slot_boxes:
        x1, y1, x2, y2 = box
        # Crop the slot region with some padding removed
        padding = max(2, min(x2 - x1, y2 - y1) // 8)
        cropped = img.crop((x1 + padding, y1 + padding, x2 - padding, y2 - padding))

        try:
            # Use --psm 7 (treat as a single text line) for slot labels
            text = pytesseract.image_to_string(
                cropped, config="--psm 7"
            ).strip()
            if text:
                results.append(text.splitlines())
            else:
                results.append([])
        except Exception:
            results.append([])

    return results


def _detect_slot_boxes(img, img_array) -> list[tuple[int, int, int, int]]:
    """Detect slot bounding boxes from blueprint image using pixel analysis.

    This is a simplified version of the frontend detectBlueprintSlots logic,
    adapted for Python/OpenCV-style processing. Finds rectangular regions
    by looking for white-pixel outlined areas.

    Args:
        img: PIL Image of the blueprint.
        img_array: numpy array of the blueprint image.

    Returns:
        List of (x1, y1, x2, y2) bounding box tuples.
    """
    WHITE_THRESHOLD = 150

    if len(img_array.shape) == 2:
        gray = img_array
    else:
        gray = img_array[:, :, 0] if img_array.shape[2] >= 3 else img_array

    height, width = gray.shape
    min_dim = min(width, height)
    min_run_len = max(10, min_dim * 0.03)
    min_slot_w = max(15, min_dim * 0.05)
    min_slot_h = max(15, min_dim * 0.05)

    # Find horizontal white pixel runs
    h_runs = []
    for row in range(height):
        run_start = -1
        for col in range(width):
            is_white = gray[row, col] > WHITE_THRESHOLD
            if is_white and run_start == -1:
                run_start = col
            elif not is_white and run_start != -1:
                if col - run_start >= min_run_len:
                    h_runs.append((row, run_start, col - 1))
                run_start = -1
        if run_start != -1 and width - run_start >= min_run_len:
            h_runs.append((row, run_start, width - 1))

    # Group into horizontal lines
    h_lines = []
    used = [False] * len(h_runs)
    for i in range(len(h_runs)):
        if used[i]:
            continue
        row_i, left_i, right_i = h_runs[i]
        line = {"top_row": row_i, "bottom_row": row_i, "left_x": left_i, "right_x": right_i}
        used[i] = True
        for j in range(i + 1, len(h_runs)):
            if used[j]:
                continue
            row_j, left_j, right_j = h_runs[j]
            if abs(row_j - line["bottom_row"]) <= 2:
                overlap = min(line["right_x"], right_j) - max(line["left_x"], left_j)
                if overlap >= min_run_len * 0.5:
                    line["left_x"] = min(line["left_x"], left_j)
                    line["right_x"] = max(line["right_x"], right_j)
                    line["bottom_row"] = row_j
                    used[j] = True
        h_lines.append(line)

    # Find rectangular slot regions
    slots = []
    for i in range(len(h_lines)):
        for j in range(i + 1, len(h_lines)):
            top = h_lines[i]
            bottom = h_lines[j]
            slot_h = bottom["bottom_row"] - top["top_row"]
            if slot_h < min_slot_h * 0.5:
                continue

            left_x = max(top["left_x"], bottom["left_x"])
            right_x = min(top["right_x"], bottom["right_x"])
            slot_w = right_x - left_x

            if slot_w < min_slot_w or slot_w > width * 0.5:
                continue
            if slot_h < min_slot_h or slot_h > height * 0.5:
                continue

            slots.append((left_x, top["top_row"], right_x, bottom["bottom_row"]))

    # Deduplicate: keep the largest encompassing box
    slots = _deduplicate_rects(slots)

    # Filter: skip slots in the very top (~8%) where ship name/header might be
    filtered = [(x1, y1, x2, y2) for x1, y1, x2, y2 in slots if y1 > height * 0.08]

    # If too many slots detected, keep largest ones
    if len(filtered) > 12:
        filtered.sort(key=lambda b: (b[2] - b[0]) * (b[3] - b[1]), reverse=True)
        filtered = filtered[:10]

    return filtered


def _deduplicate_rects(rects: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    """Remove duplicate/overlapping rectangles by clustering on center position.

    Step 1: Filter out very small rectangles (false detections).
    Step 2: Cluster rectangles by center proximity using pairwise distance.
    Step 3: From each cluster keep the largest-area rectangle.

    Args:
        rects: List of (x1, y1, x2, y2) tuples.

    Returns:
        Deduplicated list of rectangles.
    """
    if not rects:
        return []

    # Step 1: Filter out small rectangles (less than 30% of median area)
    areas = [(x2 - x1) * (y2 - y1) for x1, y1, x2, y2 in rects]
    median_area = sorted(areas)[len(areas) // 2]
    min_area = median_area * 0.3
    rects = [r for r in rects if (r[2] - r[0]) * (r[3] - r[1]) >= min_area]

    if not rects:
        return []

    # Step 2: Cluster by center proximity (non-transitive pairwise)
    centers = [(
        (r[0] + r[2]) / 2,
        (r[1] + r[3]) / 2
    ) for r in rects]

    cluster_threshold = 60  # pixels
    assigned = [False] * len(rects)
    clusters = []

    for i in range(len(rects)):
        if assigned[i]:
            continue
        cluster = [i]
        assigned[i] = True
        for j in range(len(rects)):
            if assigned[j] or i == j:
                continue
            dx = centers[i][0] - centers[j][0]
            dy = centers[i][1] - centers[j][1]
            if (dx * dx + dy * dy) < cluster_threshold * cluster_threshold:
                cluster.append(j)
                assigned[j] = True
        clusters.append(cluster)

    # Step 3: From each cluster keep the largest-area rectangle
    result = []
    for cluster in clusters:
        best_idx = max(cluster, key=lambda idx: (rects[idx][2] - rects[idx][0]) * (rects[idx][3] - rects[idx][1]))
        result.append(rects[best_idx])

    return result


def map_slots_to_ship_type(
    blueprint_name: str,
    ship_type: Ship_type
) -> dict[int, int]:
    """Map detected slot indices to static slot indices from ship_types.

    Uses hardcoded grid-based slot definitions from slot_definitions.py to
    compute deterministic slot positions, then sorts them by grid position
    (top-to-bottom, left-to-right) to establish a consistent index ordering.
    Each detected slot index is mapped sequentially to the corresponding
    static slot index.

    This replaces the previous OCR-based and positional fallback approaches
    with a reliable, deterministic mapping.

    Args:
        blueprint_name: Blueprint name, e.g. 'Terran_Interceptor'.
        ship_type: The Ship_type enum for the blueprint.

    Returns:
        Dict mapping detected slot index (position in the sorted slots list)
        to static slot index (from ship_types[ship_type]['installed_parts']).
    """
    from sim.slot_definitions import get_slot_definitions, get_slot_positions, BLUEPRINT_SHIP_TYPE_MAP

    ship_config = ship_types[ship_type]
    num_slots = ship_config["slots"]

    # Get hardcoded slot positions for this ship type
    try:
        blueprint_width = 800  # default fallback
        blueprint_height = 600  # default fallback

        # Try to get actual blueprint dimensions from the image file
        image_path = _get_blueprint_image_path(blueprint_name)
        if image_path and os.path.isfile(image_path):
            try:
                from PIL import Image
                img = Image.open(image_path)
                blueprint_width, blueprint_height = img.size
            except Exception:
                pass

        positions = get_slot_positions(int(ship_type), blueprint_width, blueprint_height)
    except Exception:
        # Total fallback: 0:0, 1:1, etc.
        return {i: i for i in range(num_slots)}

    # Sort slots by grid position (top-to-bottom, left-to-right)
    # This establishes the detected index ordering
    sorted_indices = sorted(
        range(len(positions)),
        key=lambda i: (positions[i]["x"] + positions[i]["y"] * 10000)
    )

    # Map detected index to static index sequentially
    mapping = {}
    for static_idx, detected_idx in enumerate(sorted_indices):
        if static_idx < num_slots:
            mapping[detected_idx] = static_idx

    return mapping


def _map_via_ocr(
    ocr_labels: list[list[str]],
    default_parts: list,
    num_slots: int
) -> dict[int, int]:
    """Map slots using OCR-extracted labels matched against default parts.

    For each detected slot, normalizes the OCR text and tries to match it
    to one of the default parts for this ship type. If a match is found,
    the slot index is mapped to the corresponding static index.

    Args:
        ocr_labels: List of OCR text results per slot.
        default_parts: Default parts array from ship_types.
        num_slots: Total number of slots.

    Returns:
        Dict mapping detected slot index to static slot index, or empty
        dict if no OCR matches succeeded.
    """
    mapping = {}
    for detected_idx, label_list in enumerate(ocr_labels):
        for label in label_list:
            normalized = _normalize_text(label)
            part_enum = _match_part_name(normalized)
            if part_enum is None:
                continue

            # Find this part in the default parts array
            for static_idx, default_part in enumerate(default_parts):
                if default_part == part_enum:
                    mapping[detected_idx] = static_idx
                    break
            if detected_idx in mapping:
                break

    return mapping


def _map_by_position(
    blueprint_name: str,
    num_slots: int
) -> dict[int, int]:
    """Fallback slot mapping using positional ordering.

    Sorts detected slots by y-coordinate (top-to-bottom) and maps them
    sequentially to static slot indices. This works because blueprint
    images typically arrange slots in the same order as the default
    parts array.

    Args:
        blueprint_name: Blueprint name (used to detect slots).
        num_slots: Total number of slots.

    Returns:
        Dict mapping detected slot index to static slot index based on
        vertical position ordering.
    """
    # Get slot bounding boxes to determine position
    image_path = _get_blueprint_image_path(blueprint_name)
    if not image_path or not os.path.isfile(image_path):
        # Total fallback: 0:0, 1:1, etc.
        return {i: i for i in range(num_slots)}

    try:
        from PIL import Image
        img = Image.open(image_path)
        img_array = __import__("numpy").array(img)
        slot_boxes = _detect_slot_boxes(img, img_array)
    except Exception:
        return {i: i for i in range(num_slots)}

    if not slot_boxes:
        return {i: i for i in range(num_slots)}

    # Sort slots by y-coordinate (top-to-bottom)
    sorted_indices = sorted(range(len(slot_boxes)), key=lambda i: slot_boxes[i][1])

    mapping = {}
    for mapped_idx, detected_idx in enumerate(sorted_indices):
        if mapped_idx < num_slots:
            mapping[detected_idx] = mapped_idx

    return mapping
