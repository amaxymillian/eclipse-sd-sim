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
        """Return hardcoded slot pixel positions for drawing the slot overlay.

        Returns absolute pixel coordinates for each slot, measured from
        the top-left corner of the blueprint image. Positions were obtained
        by analyzing the outline colors in the actual blueprint PNG files.

        Args:
            ship_type_name: Ship type name, e.g. 'Terran_Interceptor'.

        Response JSON:
            slots (list[dict]): Each dict has slot_type, default_part,
                x, y, width, height
            slot_types (list[str]): Slot type for each slot index
            slot_labels (list[str|None]): Human-readable label for each slot
        """
        from sim.ship_constants import Ship_type
        from sim.slot_definitions import (
            get_slot_definitions,
            SLOT_TYPE_NAMES,
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

        positions = get_slot_definitions(blueprint_int)

        # Sort positions by pixel y-coordinate, then x-coordinate
        positions_sorted = sorted(positions, key=lambda p: (p["y"], p["x"]))

        # Build response in pixel-sorted order
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
            })
            slot_types.append(pos["slot_type"])
            slot_labels.append(SLOT_TYPE_NAMES.get(pos["slot_type"]))

        return jsonify({
            'slots': result_slots,
            'slot_types': slot_types,
            'slot_labels': slot_labels,
        })

    @app.route('/api/initial_stats/<path:ship_type_name>')
    def get_initial_stats(ship_type_name):
        """Return initial ship stats computed by the backend Ship class with default parts.

        Creates a temporary Ship instance with default parts for the given
        ship type and returns its computed stats. Also returns the installed
        part names so the frontend can populate slot data.

        Args:
            ship_type_name: Ship type name, e.g. 'Terran_Interceptor'.

        Response JSON:
            stats (dict): Computed ship stats (shielding, energy, available_energy,
                initiative, armor, targeting, hp)
            installed_parts (list[str|None]): Part PNG filenames for each slot index
        """
        from sim.eclipse_sd_sim import Ship

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

        test_ship = Ship(ship_type_enum, player_num=1, is_attacker=True)

        # Calculate total_energy as sum of positive energy values from default parts
        # This represents the ship's total energy pool (sources only, not costs)
        total_energy = 0
        for part in test_ship.ship_parts:
            if part is not None:
                part_energy = ship_parts[part].get('energy', 0)
                if part_energy > 0:
                    total_energy += part_energy

        return jsonify({
            'stats': {
                'shielding': test_ship.get_shielding(),
                'energy': total_energy,
                'available_energy': test_ship.get_avail_energy(),
                'initiative': test_ship.get_initiative(),
                'armor': 0,
                'targeting': test_ship.get_targeting(),
                'hp': test_ship.get_hp(),
            },
        })

    @app.route('/api/run_battle', methods=['POST'])
    def run_battle():
        """Run a Monte Carlo battle simulation between two fleets.

        Request JSON:
            fleet_a (list[dict]): Fleet A ships, each {name, blueprint, slots}
            fleet_b (list[dict]): Fleet B ships, each {name, blueprint, slots}
            simulations (int): Number of Monte Carlo iterations

        Response JSON:
            a_win_pct (float): Percentage of simulations fleet A won
            b_win_pct (float): Percentage of simulations fleet B won
            draw_pct (float): Percentage of draws
            avg_surviving_a (float): Average surviving ships for fleet A
            avg_surviving_b (float): Average surviving ships for fleet B
        """
        from sim.eclipse_sd_sim import Ship, Battle_sim
        from sim.ship_parts_constants import Ship_Part
        from sim.ship_constants import Ship_type

        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400

        fleet_a_data = data.get('fleet_a')
        fleet_b_data = data.get('fleet_b')
        sim_count = data.get('simulations', 1000)

        if not fleet_a_data or not fleet_b_data:
            return jsonify({'error': 'fleet_a and fleet_b are required'}), 400

        if not isinstance(sim_count, int) or sim_count < 1:
            return jsonify({'error': 'simulations must be a positive integer'}), 400

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

        def build_ships(fleet_data, player_num, is_attacker):
            ships = []
            for ship_info in fleet_data:
                blueprint = ship_info.get('blueprint')
                slots = ship_info.get('slots', [])

                ship_type_enum = ship_type_map.get(blueprint)
                if not ship_type_enum:
                    return None, f'Unknown ship type: {blueprint}'

                parts_list = []
                for slot in slots:
                    part_name = slot.get('partName')
                    occupied = slot.get('occupied', False)
                    if occupied and part_name:
                        for sp in Ship_Part:
                            if sp.name == part_name:
                                parts_list.append(sp)
                                break
                        else:
                            parts_list.append(None)
                    else:
                        parts_list.append(None)

                ships.append(Ship(ship_type_enum, player_num, is_attacker, parts_list))
            return ships, None

        fleet_a, err = build_ships(fleet_a_data, 1, True)
        if err:
            return jsonify({'error': err}), 400

        fleet_b, err = build_ships(fleet_b_data, 2, False)
        if err:
            return jsonify({'error': err}), 400

        if not fleet_a or not fleet_b:
            return jsonify({'error': 'Both fleets must have at least one ship'}), 400

        battle = Battle_sim(fleet_a, fleet_b)
        battle.do_battle(sim_count)

        a_wins = 0
        b_wins = 0
        draws = 0
        total_surviving_a = 0
        total_surviving_b = 0

        for _idx, row in battle._df.iterrows():
            winner = row['Winning Player']
            count = row['Raw Count']
            if winner == 1:
                a_wins += count
            elif winner == 2:
                b_wins += count
            else:
                draws += count

            surviving_a = len([s for s in row['Surviving Intr'] + row['Surviving Crus'] + row['Surviving Dred'] + row['Surviving Strb'] if s.player_num == 1])
            surviving_b = len([s for s in row['Surviving Intr'] + row['Surviving Crus'] + row['Surviving Dred'] + row['Surviving Strb'] if s.player_num == 2])
            total_surviving_a += surviving_a * count
            total_surviving_b += surviving_b * count

        total = a_wins + b_wins + draws
        return jsonify({
            'a_win_pct': round(a_wins / total * 100, 2) if total > 0 else 0,
            'b_win_pct': round(b_wins / total * 100, 2) if total > 0 else 0,
            'draw_pct': round(draws / total * 100, 2) if total > 0 else 0,
            'avg_surviving_a': round(total_surviving_a / total, 2) if total > 0 else 0,
            'avg_surviving_b': round(total_surviving_b / total, 2) if total > 0 else 0,
            'simulations': sim_count,
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
        current_parts_names = data.get('current_parts')

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

        # Convert current parts names to enums
        current_parts = None
        if current_parts_names:
            current_parts = []
            for pname in current_parts_names:
                if pname is None:
                    current_parts.append(None)
                else:
                    found = None
                    for sp in Ship_Part:
                        if sp.name == pname:
                            found = sp
                            break
                    current_parts.append(found)

        invalid_slots = []
        invalid_reasons = {}
        num_slots = ship_types[ship_type_enum]['slots']

        # Test placing the part in each slot (fresh ship for each to avoid state pollution)
        for slot_idx in range(num_slots):
            test_ship = Ship(ship_type_enum, player_num=1, is_attacker=True, ship_parts=current_parts)
            success, message = test_ship.add_part(part_name, slot_idx)
            if not success:
                invalid_slots.append(slot_idx)
                invalid_reasons[slot_idx] = message

        return jsonify({
            'invalid_slots': invalid_slots,
            'invalid_reasons': invalid_reasons,
        })

    return app
