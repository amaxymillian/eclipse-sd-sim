// Saved ships: localStorage CRUD, export/import, saved ships menu.

import { AppState } from './state.js';
import { drawOverlay } from './canvas-overlay.js';
import { updateShipStats } from './stats.js';
import { selectBlueprint } from './interaction.js';
import { showPlacementFeedback } from './feedback.js';

export function getSavedShips() {
    try {
        var data = localStorage.getItem(AppState.SAVED_SHIPS_KEY);
        return data ? JSON.parse(data) : [];
    } catch (e) {
        console.error('Failed to read saved ships:', e);
        return [];
    }
}

function persistSavedShips(ships) {
    try {
        localStorage.setItem(AppState.SAVED_SHIPS_KEY, JSON.stringify(ships));
    } catch (e) {
        console.error('Failed to persist saved ships:', e);
        showPlacementFeedback('Failed to save: storage full or unavailable.');
    }
}

export function serializeCurrentSlots() {
    var slots = AppState.blueprintSlotBoxes[AppState.currentBlueprintName];
    if (!slots) return [];
    var result = [];
    for (var i = 0; i < slots.length; i++) {
        result.push({
            partName: slots[i].partName,
            occupied: slots[i].occupied
        });
    }
    return result;
}

export function saveCurrentShip() {
    if (!AppState.currentBlueprintName) {
        showPlacementFeedback('No ship loaded. Select a blueprint first.');
        return;
    }

    var name = prompt('Enter a name for this ship:');
    if (!name || !name.trim()) return;
    name = name.trim();

    var ships = getSavedShips();
    for (var i = 0; i < ships.length; i++) {
        if (ships[i].name === name) {
            showPlacementFeedback('A ship named "' + name + '" already exists.');
            return;
        }
    }

    ships.push({
        name: name,
        blueprint: AppState.currentBlueprintName,
        slots: serializeCurrentSlots()
    });

    persistSavedShips(ships);
    updateSavedShipsMenu();
    showPlacementFeedback('Ship "' + name + '" saved.');
}

export function loadSavedShip(index) {
    var ships = getSavedShips();
    if (index < 0 || index >= ships.length) {
        showPlacementFeedback('Saved ship not found.');
        return;
    }

    var ship = ships[index];
    selectBlueprint(ship.blueprint);

    var maxWait = 50;
    var waitCount = 0;
    var waitInterval = setInterval(function () {
        waitCount++;
        var slots = AppState.blueprintSlotBoxes[ship.blueprint];
        if (slots && slots.length > 0) {
            clearInterval(waitInterval);
            for (var i = 0; i < ship.slots.length && i < slots.length; i++) {
                slots[i].partName = ship.slots[i].partName;
                slots[i].occupied = ship.slots[i].occupied;
            }
            drawOverlay();
            updateShipStats();
            showPlacementFeedback('Loaded ship "' + ship.name + '".');
        } else if (waitCount > maxWait) {
            clearInterval(waitInterval);
            showPlacementFeedback('Timeout loading blueprint. Try again.');
        }
    }, 100);
}

export function renameSavedShip(index) {
    var ships = getSavedShips();
    if (index < 0 || index >= ships.length) return;
    var oldName = ships[index].name;
    var newName = prompt('Rename ship:', oldName);
    if (!newName || !newName.trim()) return;
    newName = newName.trim();

    for (var i = 0; i < ships.length; i++) {
        if (i !== index && ships[i].name === newName) {
            showPlacementFeedback('A ship named "' + newName + '" already exists.');
            return;
        }
    }

    ships[index].name = newName;
    persistSavedShips(ships);
    updateSavedShipsMenu();
    showPlacementFeedback('Renamed to "' + newName + '".');
}

export function deleteSavedShip(index) {
    var ships = getSavedShips();
    if (index < 0 || index >= ships.length) return;
    var removed = ships.splice(index, 1)[0];
    persistSavedShips(ships);
    updateSavedShipsMenu();
    showPlacementFeedback('Deleted ship "' + removed.name + '".');
}

export function exportCurrentShip() {
    if (!AppState.currentBlueprintName) {
        showPlacementFeedback('No ship loaded. Select a blueprint first.');
        return;
    }

    var name = prompt('Enter a name for the exported ship:');
    if (!name || !name.trim()) return;
    name = name.trim();

    var shipData = {
        name: name,
        blueprint: AppState.currentBlueprintName,
        slots: serializeCurrentSlots()
    };

    var blob = new Blob([JSON.stringify(shipData, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = name.replace(/[^a-zA-Z0-9_-]/g, '_') + '.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showPlacementFeedback('Exported ship "' + name + '".');
}

export function importShipFromEvent(event) {
    var file = event.target.files[0];
    if (!file) return;

    var reader = new FileReader();
    reader.onload = function (e) {
        try {
            var data = JSON.parse(e.target.result);
            if (!data.name || !data.blueprint || !data.slots || !Array.isArray(data.slots)) {
                showPlacementFeedback('Invalid ship file: missing required fields.');
                return;
            }

            var ships = getSavedShips();
            for (var i = 0; i < ships.length; i++) {
                if (ships[i].name === data.name) {
                    data.name = data.name + ' (imported)';
                    break;
                }
            }

            ships.push({
                name: data.name,
                blueprint: data.blueprint,
                slots: data.slots
            });
            persistSavedShips(ships);
            updateSavedShipsMenu();
            showPlacementFeedback('Imported ship "' + data.name + '".');
        } catch (err) {
            console.error('Failed to import ship:', err);
            showPlacementFeedback('Invalid JSON file.');
        }
    };
    reader.readAsText(file);
    event.target.value = '';
}

export function updateSavedShipsMenu() {
    var container = document.getElementById('savedShipsList');
    if (!container) return;

    var ships = getSavedShips();
    container.innerHTML = '';

    if (ships.length === 0) {
        var emptyEl = document.createElement('a');
        emptyEl.href = '#';
        emptyEl.textContent = 'No saved ships';
        emptyEl.style.color = '#999';
        emptyEl.style.pointerEvents = 'none';
        container.appendChild(emptyEl);
        return;
    }

    for (var i = 0; i < ships.length; i++) {
        (function (index) {
            var row = document.createElement('div');
            row.style.cssText = 'display: flex; align-items: center; justify-content: space-between; padding: 6px 8px;';

            var link = document.createElement('a');
            link.href = '#';
            link.textContent = ships[index].name;
            link.style.cssText = 'flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;';
            link.onclick = function (e) {
                e.preventDefault();
                // Import closeAllDropdowns dynamically to avoid circular dep at load time
                loadDropdownsAndClose(index);
            };
            row.appendChild(link);

            var btns = document.createElement('span');
            btns.style.cssText = 'display: flex; gap: 4px; margin-left: 4px;';

            var renameBtn = document.createElement('a');
            renameBtn.href = '#';
            renameBtn.textContent = '\u{1F9AD}';
            renameBtn.title = 'Rename';
            renameBtn.style.cssText = 'font-size: 12px; padding: 2px 4px;';
            renameBtn.onclick = function (e) { e.preventDefault(); renameSavedShip(index); };
            btns.appendChild(renameBtn);

            var delBtn = document.createElement('a');
            delBtn.href = '#';
            delBtn.textContent = '\u{1F5D1}';
            delBtn.title = 'Delete';
            delBtn.style.cssText = 'font-size: 12px; padding: 2px 4px;';
            delBtn.onclick = function (e) { e.preventDefault(); deleteSavedShip(index); };
            btns.appendChild(delBtn);

            row.appendChild(btns);
            container.appendChild(row);
        })(i);
    }
}

function loadDropdownsAndClose(index) {
    import('./dropdowns.js').then(function (mod) {
        mod.closeAllDropdowns();
        loadSavedShip(index);
    });
}
