# Boilerplate code from https://flask.palletsprojects.com/en/2.2.x/tutorial/factory/
import os

from flask import Flask, jsonify, render_template, request, flash

from sim.eclipse_sd_sim import Ship, Battle_sim, ship_types, Ship_type
from sim.ship_parts_constants import ship_parts, ship_part_png, Ship_Part

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
            invalid_reasons (dict[int, str]): Reason for each invalid slot
        """
        from sim.eclipse_sd_sim import Ship, Ship_type, PlacementFailureReason
        from sim.ship_parts_constants import Ship_Part
        import re

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
            # Convert enum name to uppercase string form (e.g. 'ION_CANNON')
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
            success, reason = test_ship.add_part(part_name, slot_idx)
            if not success:
                invalid_slots.append(slot_idx)
                reason_map = {
                    PlacementFailureReason.INSUFFICIENT_ENERGY: 'INSUFFICIENT_ENERGY',
                    PlacementFailureReason.REMOVES_ONLY_DRIVE: 'REMOVES_ONLY_DRIVE',
                }
                invalid_reasons[slot_idx] = reason_map.get(reason, 'UNKNOWN')

        return jsonify({
            'invalid_slots': invalid_slots,
            'invalid_reasons': invalid_reasons,
        })

    return app
