# Eclipse SD Sim - Agent Guidelines

## Project Overview

**Eclipse Second Dawn for the Galaxy Battle Simulator** -- a Monte Carlo probability simulator for the Eclipse board game. Users configure ship fleets via a drag-and-drop designer, then simulate battles to get win probabilities.

- **Python**: 3.12+
- **Package manager**: uv (see `pyproject.toml`, `uv.lock`)
- **Run**: `./run.sh` or `uv run flask run`

---

## Architecture

```
eclipse-sd-sim/
├── flaskr/              # Flask web application
│   ├── __init__.py      # App factory, routes, API endpoints
│   ├── frontend.py      # (empty placeholder)
│   ├── templates/
│   │   └── index.html   # Single-page app with embedded CSS/JS
│   └── static/
│       ├── style.css    # Global styles
│       ├── scripts/
│       │   ├── eclipse-sd-sim.js   # Frontend logic (drag-drop, canvas, stats)
│       │   └── tracking-min.js     # Analytics
│       └── images/      # Blueprints, parts, technology assets
├── sim/                 # Simulation engine
│   ├── eclipse_sd_sim.py        # Core battle simulation (Ship, Battle_sim)
│   └── ship_parts_constants.py  # Ship part definitions (Ship_Part enum, stats)
└── instance/            # SQLite DB (flaskr.sqlite) -- gitignored
```

---

## Code Modules

### `flaskr/__init__.py` -- Flask App Factory & Routes

Uses the **application factory pattern** (`create_app()`). Routes:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/`, `/index` | GET/POST | Main page renderer |
| `/api/ship_parts` | GET | JSON: all ship parts with stats and PNG filenames |
| `/api/ship_types` | GET | JSON: 16 ship types with slots, initiative, energy, default parts |

### `sim/eclipse_sd_sim.py` -- Simulation Engine

**Enums:**
- `PlacementFailureReason` -- result codes for part placement (SUCCESS, INSUFFICIENT_ENERGY, REMOVES_ONLY_DRIVE)
- `Ship_type` -- 16 ship types across 4 races (Terran, Eridani, Orion, Planta), each with 4 classes

**Core classes:**
- `Ship` -- Represents a single ship. Manages slot-based part installation, derived stat recalculation (HP, initiative, targeting, shielding), and weapon fire resolution. Parts are added/removed via `add_part()` / `remove_part()`.
- `Battle_sim` -- Manages a battle between two fleets. Key methods:
  - `do_battle(sim_count)` -- Main Monte Carlo loop; runs N battles, returns pandas DataFrame of outcome distributions
  - `create_ship_init_dict()` -- Groups ships by initiative for turn ordering
  - `process_one_init_group()` -- Resolves combat for ships acting in the same turn
  - `assign_dmg()` -- Assigns damage using "Ancients strategy" (destroy largest targetable ship possible)
  - `save_fleet()` / `load_fleet()` -- Persist/restore fleets via jsonpickle JSON serialization

### `sim/ship_parts_constants.py` -- Part Definitions

- `Ship_Part` (IntEnum) -- 43 part types across categories: standard, rare, discovery tiles, guardian/ancient/GCDS
- `ship_parts` (dict) -- Maps each part to stats: type, damage, energy, initiative, armor, targeting, shielding, times_fired
- `ship_part_png` (dict) -- Maps parts to their PNG filenames for the frontend

### `flaskr/static/scripts/eclipse-sd-sim.js` -- Frontend

Two-layer HTML5 canvas approach for the ship designer:
1. `shipBlueprintCanvas` -- renders the ship blueprint image
2. `overlayCanvas` -- interactive layer for slot borders and placed parts

Key flows:
- `detectBlueprintSlots()` -- pixel analysis of blueprint images to find draggable slot regions
- Drag-and-drop and click-to-place for installing parts
- `calculateShipStats()` -- aggregates stats from placed parts and updates UI
- Fetches part/type data from Flask API endpoints

### `flaskr/templates/index.html` + `static/style.css`

Single-page application with embedded CSS. Two main sections toggled via `showPrimaryDiv()`:
- Ship Designer (fully implemented)
- Battle Simulator (placeholder, awaiting implementation)

---

## Best Practices

### Documentation

- **Docstrings**: Every function, method, and class must have a docstring describing purpose, parameters, and return value. Use Google style.
- **Inline comments**: Explain *why*, not *what*. Code should be self-explanatory for straightforward logic.
- **Module-level docstrings**: Each Python file should start with a one-line description of its purpose.
- **TODO comments**: Mark incomplete features with `# TODO:` including what needs to be done.

### Code Design

- **Single responsibility**: Each class should have one clear purpose. `Ship` manages one ship's state; `Battle_sim` manages fleet-level simulation.
- **Enums over magic numbers**: All domain constants (ship types, part types, placement results) use `IntEnum`.
- **Static configuration in dicts**: Ship type defaults live in `ship_types` dict; parts data in `ship_parts` dict. Keep these in sync when adding new content.
- **Derived stats recalculation**: When ship state changes (parts added/removed), stats (HP, initiative, targeting, shielding) must be recalculated. Don't cache stale values.
- **Deep copy for simulation**: Always `deepcopy` ships before running simulation iterations to preserve original fleet state.

### API Design

- API endpoints (`/api/*`) return JSON. Keep responses minimal -- only the fields the frontend needs.
- Use GET for data retrieval, POST for mutations. Currently all APIs are GET.
- Error handling: return appropriate HTTP status codes with descriptive JSON error messages.

### Frontend

- Canvas slot detection via pixel analysis is a fragile approach. When blueprints change format, `detectBlueprintSlots()` may break. Consider hardcoding slot positions per blueprint as a more robust alternative.
- State management is implicit (stored in JS variables). As the app grows, consider introducing a clear state object.
- The Battle Simulator frontend section is still a placeholder in `index.html`.

### Testing

- No automated tests exist yet. The `Battle_sim.main()` function is a manual smoke test.
- Add pytest tests for:
  - Part placement validation (energy constraints, slot bounds)
  - Stat calculations (initiative, targeting, shielding)
  - Battle simulation outcomes (deterministic scenarios with known results)
  - API endpoint responses

### Simulation Engine

- `fire_missiles()` and `process_rift_stacks()` are marked `NotImplementedError` -- prioritize these before production use.
- The Monte Carlo loop in `do_battle()` uses pandas DataFrames for aggregation. For large sim counts, consider the planned Dask integration for parallelism.
- `get_flattened_df()` is also `NotImplementedError` -- needed for detailed per-iteration output.

### Git & Deployment

- `.gitignore` excludes `.venv/`, `instance/`, `__pycache__/`, `*.pyc`, `.vscode/`.
- Dependencies managed by uv -- install with `uv sync`, not `pip install`.
- The hardcoded `SECRET_KEY='dev'` in `flaskr/__init__.py` must be changed for any production deployment.
