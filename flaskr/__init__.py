# Boilerplate code from https://flask.palletsprojects.com/en/2.2.x/tutorial/factory/
import os

from flask import Flask, jsonify, render_template, request, flash

from sim.eclipse_sd_sim import Ship, Battle_sim
from sim.ship_parts_constants import ship_parts, ship_part_png, Ship_Part
from sim.ship_constants import ship_types, Ship_type

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/', methods=('GET','POST'))
    @app.route('/index', methods=('GET','POST'))
    def index():
        # Do Stuff
        if request.method == 'POST':
            flash('POST!')

        return render_template('index.html')

    @app.route('/api/ship_parts')
    def get_ship_parts():
        """Return ship parts data as JSON for the frontend.

        Returns parts keyed by their uppercase name (e.g. 'ION_CANNON')
        matching the Ship_Part enum values.
        """
        parts = {}
        for part_enum, stats in ship_parts.items():
            png_path = ship_part_png[part_enum]
            png_filename = png_path.split('/')[-1].replace('.png', '')
            parts[png_filename] = dict(stats)
        return jsonify(parts)

    @app.route('/api/ship_types')
    def get_ship_types():
        """Return ship types data as JSON for the frontend."""
        ship_type_data = {}
        for ship_enum, data in ship_types.items():
            # Convert Ship_type enum to string name (e.g. Terran_Interceptor)
            parts = ship_enum.name.split('_')
            name = parts[0].capitalize() + '_' + '_'.join(w.capitalize() for w in parts[1:])
            ship_type_data[name] = {
                'slots': data['slots'],
                'base_initiative': data['base_initiative'],
                'bonus_energy': data['bonus_energy'],
                'bonus_targeting': data['bonus_targeting'],
                'installed_parts': [
                    ship_part_png[p].split('/')[-1].replace('.png', '') if p is not None else None
                    for p in data['installed_parts']
                ]
            }
        return jsonify(ship_type_data)

    @app.route('/api/ship_types/<path:ship_type_name>')
    def get_ship_type_info(ship_type_name):
        """Return detailed ship type data for a specific ship type.

        Returns the ship configuration including slots, base stats, default parts,
        and part type labels extracted from the blueprint image using OCR.

        Args:
            ship_type_name: Ship type name, e.g. 'Terran_Interceptor'.

        Response JSON:
            slots (int): Number of slots on the ship
            base_initiative (int): Base initiative value
            bonus_energy (int): Energy pool bonus
            bonus_targeting (int): Targeting bonus
            installed_parts (list[str]): Default part PNG filenames for each slot
            part_types (list[str]): Human-readable part type labels for each slot
            slot_labels (list[str]|None): OCR-extracted labels from blueprint, if available
        """
        from sim.ship_parts_constants import ship_part_png

        # Convert ship type string to enum
        parts = ship_type_name.split('_')
        enum_name = '_'.join(p.upper() for p in parts)
        ship_type_enum = None
        for st in Ship_type:
            if st.name == enum_name:
                ship_type_enum = st
                break

        if not ship_type_enum:
            return jsonify({'error': f'Unknown ship type: {ship_type_name}'}), 400

        config = ship_types[ship_type_enum]
        default_parts = config['installed_parts']

        # Build installed parts list with PNG filenames
        installed_parts = []
        for p in default_parts:
            if p is not None:
                installed_parts.append(ship_part_png[p].split('/')[-1].replace('.png', ''))
            else:
                installed_parts.append(None)

        # Build part type labels (human-readable type for each slot)
        part_types = []
        for p in default_parts:
            if p is not None:
                part_type = ship_parts[p].get('type', 'unknown')
                part_types.append(part_type)
            else:
                part_types.append('empty')

        # Try OCR to extract slot labels from blueprint
        slot_labels = None
        try:
            from sim.slot_label_ocr import extract_slot_labels_ocr
            ocr_result = extract_slot_labels_ocr(ship_type_name)
            if ocr_result:
                slot_labels = []
                for slot_text_list in ocr_result:
                    if slot_text_list:
                        # Use first non-empty OCR result
                        slot_labels.append(slot_text_list[0])
                    else:
                        slot_labels.append(None)
        except ImportError:
            pass  # OCR not available, skip

        return jsonify({
            'slots': config['slots'],
            'base_initiative': config['base_initiative'],
            'bonus_energy': config['bonus_energy'],
            'bonus_targeting': config['bonus_targeting'],
            'installed_parts': installed_parts,
            'part_types': part_types,
            'slot_labels': slot_labels,
        })

    @app.route('/api/ship_type_mapping/<path:ship_type_name>')
    def get_ship_type_mapping(ship_type_name):
        """Return the mapping between detected blueprint slots and static slot indices.

        Uses OCR to extract labels from the blueprint image and matches them
        against the ship type's default parts to determine which detected slot
        corresponds to which static slot index.

        Args:
            ship_type_name: Ship type name, e.g. 'Terran_Interceptor'.

        Response JSON:
            mapping (dict[int, int]): Detected slot index -> static slot index
            fallback (bool): True if OCR failed and positional ordering was used
        """
        from sim.ship_constants import Ship_type

        # Convert ship type string to enum
        parts = ship_type_name.split('_')
        enum_name = '_'.join(p.upper() for p in parts)
        ship_type_enum = None
        for st in Ship_type:
            if st.name == enum_name:
                ship_type_enum = st
                break

        if not ship_type_enum:
            return jsonify({'error': f'Unknown ship type: {ship_type_name}'}), 400

        try:
            from sim.slot_label_ocr import map_slots_to_ship_type
            mapping = map_slots_to_ship_type(ship_type_name, ship_type_enum)
            fallback = len(mapping) < ship_types[ship_type_enum]['slots']
            return jsonify({
                'mapping': mapping,
                'fallback': False,
            })
        except ImportError:
            return jsonify({'error': 'Slot definitions module not available'}), 503

    @app.route('/api/ship_type_grid/<path:ship_type_name>')
    def get_ship_type_grid(ship_type_name):
        """Return hardcoded slot grid positions for drawing the slot overlay.

        Computes pixel coordinates for each slot based on the blueprint
        image dimensions and the hardcoded grid layout. Replaces the
        fragile pixel-based slot detection.

        Args:
            ship_type_name: Ship type name, e.g. 'Terran_Interceptor'.

        Response JSON:
            slots (list[dict]): Each dict has slot_type, default_part,
                x, y, width, height, grid_row, grid_col
            slot_types (list[str]): Slot type for each slot index
            slot_labels (list[str|None]): Human-readable label for each slot
        """
        from sim.ship_constants import Ship_type
        from sim.slot_definitions import (
            get_slot_positions,
            get_slot_definitions,
            SLOT_TYPE_NAMES,
            BLUEPRINT_SHIP_TYPE_MAP,
        )

        blueprint_name = ship_type_name
        ship_type_enum = None
        for st in Ship_type:
            if st.name == ship_type_name.upper().replace('-', '_'):
                ship_type_enum = st
                break

        if not ship_type_enum:
            return jsonify({'error': f'Unknown ship type: {ship_type_name}'}), 400

        blueprint_int = int(ship_type_enum)

        try:
            from PIL import Image
            import os
            image_path = os.path.join(
                os.path.dirname(__file__),
                "static", "images", "blueprints", blueprint_name + ".png"
            )
            if os.path.isfile(image_path):
                img = Image.open(image_path)
                bw, bh = img.size
            else:
                bw, bh = 800, 600
        except Exception:
            bw, bh = 800, 600

        positions = get_slot_positions(blueprint_int, bw, bh)

        # Sort positions by grid position (top-to-bottom, left-to-right)
        positions_sorted = sorted(positions, key=lambda p: (p["grid_row"], p["grid_col"]))

        # Build response in grid-sorted order
        result_slots = []
        slot_types = []
        slot_labels = []

        for pos in positions_sorted:

            result_slots.append({
                "slot_type": pos["slot_type"],
                "default_part": pos["default_part"].name if pos["default_part"] else None,
                "x": pos["x"],
                "y": pos["y"],
                "width": pos["width"],
                "height": pos["height"],
                "grid_row": pos["grid_row"],
                "grid_col": pos["grid_col"],
            })
            slot_types.append(pos["slot_type"])
            slot_labels.append(SLOT_TYPE_NAMES.get(pos["slot_type"]))

        return jsonify({
            'slots': result_slots,
            'slot_types': slot_types,
            'slot_labels': slot_labels,
        })

    @app.route('/api/validate_part_placement', methods=['POST'])
    def validate_part_placement():
        """Validate where a part can be placed on a ship.

        Creates a temporary Ship instance with default parts for the given
        ship type, then tests add_part() against every slot. Returns which
        slots are invalid and why.

        Request JSON:
            ship_type (str): Ship type name, e.g. 'Terran_Interceptor'
            part_name (str): Uppercase part name, e.g. 'ION_CANNON'

        Response JSON:
            invalid_slots (list[int]): Slot indices where placement fails
            invalid_reasons (dict[int, str]): Human-readable reason for each invalid slot
        """
        from sim.eclipse_sd_sim import Ship
        from sim.ship_parts_constants import Ship_Part

        data = request.get_json()
        ship_type_name = data.get('ship_type')
        part_name = data.get('part_name')

        if not ship_type_name or not part_name:
            return jsonify({'error': 'ship_type and part_name are required'}), 400

        # Convert ship type string (e.g. 'Terran_Interceptor') to Ship_type enum
        ship_type_map = {
            'Terran_Interceptor': Ship_type.TERRAN_INTERCEPTOR,
            'Terran_Cruiser': Ship_type.TERRAN_CRUISER,
            'Terran_Dreadnought': Ship_type.TERRAN_DREADNOUGHT,
            'Terran_Starbase': Ship_type.TERRAN_STARBASE,
            'Eridani_Interceptor': Ship_type.ERIDANI_INTERCEPTOR,
            'Eridani_Cruiser': Ship_type.ERIDANI_CRUISER,
            'Eridani_Dreadnought': Ship_type.ERIDANI_DREADNOUGHT,
            'Eridani_Starbase': Ship_type.ERIDANI_STARBASE,
            'Orion_Interceptor': Ship_type.ORION_INTERCEPTOR,
            'Orion_Cruiser': Ship_type.ORION_CRUISER,
            'Orion_Dreadnought': Ship_type.ORION_DREADNOUGHT,
            'Orion_Starbase': Ship_type.ORION_STARBASE,
            'Planta_Interceptor': Ship_type.PLANTA_INTERCEPTOR,
            'Planta_Cruiser': Ship_type.PLANTA_CRUISER,
            'Planta_Dreadnought': Ship_type.PLANTA_DREADNOUGHT,
            'Planta_Starbase': Ship_type.PLANTA_STARBASE,
        }
        ship_type_enum = ship_type_map.get(ship_type_name)
        if not ship_type_enum:
            return jsonify({'error': f'Unknown ship type: {ship_type_name}'}), 400

        # Convert part name string (e.g. 'ION_CANNON') to Ship_Part enum
        part_enum = None
        for sp_enum in Ship_Part:
            enum_str = sp_enum.name
            if part_name == enum_str:
                part_enum = sp_enum
                break
        if not part_enum:
            return jsonify({'error': f'Unknown part: {part_name}'}), 400

        invalid_slots = []
        invalid_reasons = {}
        num_slots = ship_types[ship_type_enum]['slots']

        # Test placing the part in each slot (fresh ship for each to avoid state pollution)
        for slot_idx in range(num_slots):
            test_ship = Ship(ship_type_enum, player_num=1, is_attacker=True, ship_parts=None)
            success, message = test_ship.add_part(part_name, slot_idx)
            if not success:
                invalid_slots.append(slot_idx)
                invalid_reasons[slot_idx] = message

        return jsonify({
            'invalid_slots': invalid_slots,
            'invalid_reasons': invalid_reasons,
        })

    return app
