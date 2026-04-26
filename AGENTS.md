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
│   │   └── index.html   # SPA template; data-* attributes drive JS behavior
│   └── static/
│       ├── style.css    # Global styles
│       ├── scripts/     # ES modules (no build step)
│       │   ├── main.js              # Entry point; DOMContentLoaded bootstrap
│       │   ├── state.js             # Central AppState object (single source of truth)
│       │   ├── feedback.js          # Toast notification helper
│       │   ├── canvas-overlay.js    # Canvas drawing: slots, parts, labels
│       │   ├── stats.js             # Ship stat calculation and display
│       │   ├── validation.js        # Async backend part placement validation
│       │   ├── interaction.js       # Slot interaction, drag-drop, blueprint selection
│       │   ├── handlers.js          # Overlay canvas event listeners
│       │   ├── saved-ships.js       # localStorage CRUD, export/import
│       │   ├── dropdowns.js         # Dropdown open/close/reposition
│       │   └── tracking-min.js      # Analytics
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
| `/api/ship_types/<name>` | GET | JSON: detailed ship type info (part types, slot labels, OCR) |
| `/api/ship_type_mapping/<name>` | GET | JSON: detected slot index -> static slot index mapping |
| `/api/ship_type_grid/<name>` | GET | JSON: hardcoded slot pixel positions for overlay drawing |
| `/api/initial_stats/<name>` | GET | JSON: computed default stats for a ship type |
| `/api/validate_part_placement` | POST | JSON: validates where a part can be placed; returns invalid slots + reasons |

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

### Frontend Modules (`flaskr/static/scripts/`)

The frontend uses **native ES modules** (no build step). Entry point is `main.js` loaded via `<script type="module">` in `index.html`. All event binding uses `data-*` attributes -- no inline `onclick` handlers.

**Module dependency graph** (arrows = imports from):
```
state.js (no deps)          feedback.js (no deps)       dropdowns.js (no deps)
    │                            │                           │
    ▼                            │                           │
canvas-overlay.js ──────────────┤                           │
    │                            │                           │
    ▼                            │                           │
stats.js ───────────────────────┤                           │
    │                            │                           │
    ▼                            │                           │
validation.js ──────────────────┤                           │
    │                            │                           │
    ▼                            │                           │
interaction.js ─────────────────┤                           │
    │                            │                           │
    ▼                            │                           │
handlers.js ────────────────────┘                           │
    │                                                       │
    ▼                                                       │
saved-ships.js ── dynamic import ───────────────────────────┘
    │
    ▼
main.js (imports all setup functions)
```

#### `main.js` -- Entry Point

- Imports setup functions from all modules
- `DOMContentLoaded`: calls `setupOverlayHandlers()`, `setupDropdownHandlers()`, `setupDataAttributeHandlers()`, `updateSavedShipsMenu()`
- `setupDataAttributeHandlers()`: wires `data-*` attribute elements to handler functions:
  - `.blueprint-thumb` click -> `selectBlueprint(data-blueprint)`
  - `.part-image` click -> `addPartToShip(data-part)`
  - `.part-image` dragstart -> `onDragStart(event, data-part)`
  - `[data-view]` click -> `showPrimaryDiv(data-view)`
  - `[data-action="save-ship"]` click -> `saveCurrentShip()`
  - `[data-action="export-ship"]` click -> `exportCurrentShip()`
  - `#importShipFile` change -> `importShipFromEvent(event)`

#### `state.js` -- Central State

- Exports `AppState` object: single source of truth for all frontend state
- Properties: `blueprintSlotBoxes`, `selectedPartName`, `hoveredSlotIndex`, `overlayImagesLoaded`, `currentBlueprintName`, `invalidSlotsForSelectedPart`, `lastValidationFeedback`, `shipPartsData`, `shipTypesData`, `currentShipStats`, `currentShipTypeInfo`, `currentSlotMapping`
- Exports constants: `WHITE_THRESHOLD`, `SAVED_SHIPS_KEY`

#### `feedback.js` -- Toast Notifications

- `showPlacementFeedback(message)` -- shows a brief red toast above the canvas; auto-fades after 3 seconds

#### `canvas-overlay.js` -- Canvas Drawing

- `drawOverlay()` -- renders slot borders, part images, invalid markers, and labels on the overlay canvas
- `drawPartImage()` -- draws a part icon in a slot; lazy-loads part images
- `drawSlotLabelText()` -- draws part type label on each slot
- `updateSlotLabels()` -- populates slot labels from ship type info
- `loadGridSlots()` -- fetches hardcoded slot positions from `/api/ship_type_grid/<name>`
- Bounding box detection functions (`verifyVerticalEdge`, `verifyHorizontalEdge`, `deduplicateSlots`) -- legacy pixel analysis, largely unused now

#### `stats.js` -- Ship Statistics

- `loadShipData()` -- fetches `/api/ship_parts` and `/api/ship_types`
- `loadShipTypeInfo()` -- fetches type info, slot mapping, and initial stats for a blueprint
- `calculateShipStats()` -- aggregates stats from placed parts (shielding, energy, initiative, armor, targeting, HP)
- `updateStatsDisplay()` -- updates `#shipStatsPanel` DOM elements
- `updateInstalledPartsList()` -- updates `#installedPartsList` with current parts
- `updateShipStats()` -- orchestrates recalculation + display update

#### `validation.js` -- Backend Validation

- `buildSlotMapping()` -- maps detected frontend slot indices to backend static slot indices
- `validatePartPlacement()` -- POSTs to `/api/validate_part_placement`; updates slot invalid states and redraws overlay

#### `interaction.js` -- Core Interaction

- `getSlotAtPosition()` -- hit detection: returns slot index at canvas coordinates
- `placePart()` -- places a part in a slot with sync validation; updates overlay and stats
- `removePart()` -- removes a part from a slot; updates overlay and stats
- `onDragStart()` -- sets drag data and triggers validation for dragged part
- `addPartToShip()` -- selects a part for click-to-place; highlights part image; triggers validation
- `showPrimaryDiv()` -- toggles between Ship Designer and Battle Simulator views
- `selectBlueprint()` -- loads a blueprint image, sets up canvases, loads grid slots and ship data

#### `handlers.js` -- Canvas Event Listeners

- `setupOverlayHandlers()` -- attaches dragover/drop/click/contextmenu/mousemove/mouseleave to `#overlayCanvas`
- Handles coordinate scaling between display size and internal canvas dimensions

#### `saved-ships.js` -- Persistence

- `saveCurrentShip()` / `loadSavedShip()` -- localStorage CRUD with serialization
- `renameSavedShip()` / `deleteSavedShip()` -- mutation operations
- `exportCurrentShip()` -- downloads ship as JSON file
- `importShipFromEvent()` -- reads JSON file, adds to saved ships
- `updateSavedShipsMenu()` -- renders saved ships list in dropdown
- `serializeCurrentSlots()` -- converts slot state to serializable format

#### `dropdowns.js` -- Dropdown Management

- `openDropdown()` / `closeDropdown()` / `closeAllDropdowns()` -- dropdown lifecycle
- `repositionDropdownContent()` -- adjusts position on scroll/resize
- `setupDropdownHandlers()` -- attaches click/scroll/resize listeners; manages blueprint dropdown overlay pointer-events toggle

### `flaskr/templates/index.html` + `static/style.css`

Single-page application with embedded CSS. Two main sections toggled via `showPrimaryDiv()`:
- Ship Designer (fully implemented)
- Battle Simulator (placeholder, awaiting implementation)

**data-* attribute convention:** All interactive elements use `data-*` attributes instead of inline `onclick` handlers. The `main.js` module wires these up programmatically:
- `data-blueprint="Name"` on `.blueprint-thumb` images triggers blueprint selection
- `data-part="PART_NAME"` on `.part-image` images triggers click-to-place and drag-and-drop
- `data-view="shipDesigner|battleSimulator"` on links toggles primary views
- `data-action="save-ship|export-ship"` on links triggers ship designer menu actions

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

- Canvas slot detection via pixel analysis is a fragile approach. When blueprints change format, `detectBlueprintSlots()` may break. Slot positions are now hardcoded per blueprint (served via `/api/ship_type_grid/<name>`).
- State is centralized in the `AppState` object exported from `state.js`. All modules import from this single source of truth -- do not introduce new global variables.
- ES modules use relative imports (e.g., `import { ... } from './state.js'`). Flask serves these as static files; no build step needed.
- All event binding uses `data-*` attributes wired in `main.js`. Never add inline `onclick` handlers to `index.html`.
- Avoid circular dependencies between modules. If a circular dependency arises, extract the shared function to a separate module (e.g., `feedback.js`).
- The Battle Simulator frontend section is still a placeholder in `index.html`.

**Adding new frontend functionality:**
1. Determine which module the new code belongs to based on the dependency graph above
2. Add new exports to that module
3. If the new code needs to respond to DOM events, either:
   - Add a `data-*` attribute to `index.html` and wire it in `main.js`'s `setupDataAttributeHandlers()`
   - Or create a new `setup*()` function and call it from `main.js` on `DOMContentLoaded`
4. If the new code needs state, add properties to `AppState` in `state.js`

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
