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
        """Return ship parts data as JSON for the frontend."""
        parts = {}
        for part_enum, stats in ship_parts.items():
            # Get the PNG filename from the path
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

    return app
