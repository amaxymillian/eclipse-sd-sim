// Battle Simulator module: fleet builders, simulation run, results display.

import { AppState } from './state.js';
import { getSavedShips } from './saved-ships.js';
import { showPlacementFeedback } from './feedback.js';
import { selectBlueprint, showPrimaryDiv } from './interaction.js';
import { drawOverlay } from './canvas-overlay.js';
import { updateShipStats } from './stats.js';

function getBlueprintImagePath(blueprintName) {
    return '/static/images/blueprints/' + blueprintName + '.png';
}

function renderFleetList(fleetId) {
    var container = document.getElementById(fleetId);
    if (!container) return;

    var savedShips = getSavedShips();
    if (savedShips.length === 0) {
        container.innerHTML = '<div class="no-ships-msg">No saved ships. Design and save ships first.</div>';
        return;
    }

    var fleetState = fleetId === 'fleetAList' ? AppState.battle.fleetA : AppState.battle.fleetB;

    var html = '<ul class="fleet-list">';
    for (var i = 0; i < savedShips.length; i++) {
        var ship = savedShips[i];
        var count = fleetState[ship.name] || 0;
        var thumb = getBlueprintImagePath(ship.blueprint);

        html += '<li class="fleet-item" data-ship-index="' + i + '" data-ship-name="' + ship.name + '">';
        html += '<img class="thumb" src="' + thumb + '" alt="' + ship.name + '" onerror="this.src=\'/static/images/blueprints/Terran_Interceptor.png\'">';
        html += '<span class="ship-name">' + ship.name + '</span>';
        html += '<div class="count-controls">';
        html += '<button class="count-btn dec" data-fleet="' + fleetId + '" data-ship="' + ship.name + '">−</button>';
        html += '<span class="count-value">' + count + '</span>';
        html += '<button class="count-btn inc" data-fleet="' + fleetId + '" data-ship="' + ship.name + '">+</button>';
        html += '</div>';
        html += '</li>';
    }
    html += '</ul>';
    container.innerHTML = html;

    bindFleetEvents(fleetId);
}

function bindFleetEvents(fleetId) {
    var fleetState = fleetId === 'fleetAList' ? AppState.battle.fleetA : AppState.battle.fleetB;

    var incBtns = document.querySelectorAll('#' + fleetId + ' .count-btn.inc');
    for (var i = 0; i < incBtns.length; i++) {
        incBtns[i].addEventListener('click', function () {
            var shipName = this.getAttribute('data-ship');
            fleetState[shipName] = (fleetState[shipName] || 0) + 1;
            updateCountDisplay(fleetId);
            updateRunButtonState();
        });
    }

    var decBtns = document.querySelectorAll('#' + fleetId + ' .count-btn.dec');
    for (var j = 0; j < decBtns.length; j++) {
        decBtns[j].addEventListener('click', function () {
            var shipName = this.getAttribute('data-ship');
            fleetState[shipName] = Math.max(0, (fleetState[shipName] || 0) - 1);
            updateCountDisplay(fleetId);
            updateRunButtonState();
        });
    }

    var items = document.querySelectorAll('#' + fleetId + ' .fleet-item');
    for (var k = 0; k < items.length; k++) {
        items[k].addEventListener('contextmenu', function (e) {
            e.preventDefault();
            var shipName = this.getAttribute('data-ship-name');
            showContextMenu(e.clientX, e.clientY, shipName);
        });
    }
}

function updateCountDisplay(fleetId) {
    var fleetState = fleetId === 'fleetAList' ? AppState.battle.fleetA : AppState.battle.fleetB;
    var items = document.querySelectorAll('#' + fleetId + ' .fleet-item');
    for (var i = 0; i < items.length; i++) {
        var shipName = items[i].getAttribute('data-ship-name');
        var countSpan = items[i].querySelector('.count-value');
        if (countSpan) {
            countSpan.textContent = fleetState[shipName] || 0;
        }
    }
}

function showContextMenu(x, y, shipName) {
    removeContextMenu();

    var menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.id = 'battle-context-menu';
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';

    var editItem = document.createElement('div');
    editItem.className = 'context-menu-item';
    editItem.textContent = 'Edit Design';
    editItem.addEventListener('click', function () {
        editSavedShipByName(shipName);
        removeContextMenu();
    });

    menu.appendChild(editItem);
    document.body.appendChild(menu);

    setTimeout(function () {
        document.addEventListener('click', removeContextMenu, { once: true });
    }, 0);
}

function removeContextMenu() {
    var existing = document.getElementById('battle-context-menu');
    if (existing) {
        document.body.removeChild(existing);
    }
}

function editSavedShipByName(shipName) {
    var savedShips = getSavedShips();
    for (var i = 0; i < savedShips.length; i++) {
        if (savedShips[i].name === shipName) {
            loadSavedShipForEdit(i);
            return;
        }
    }
    showPlacementFeedback('Ship "' + shipName + '" not found.');
}

function loadSavedShipForEdit(index) {
    var savedShips = getSavedShips();
    if (index < 0 || index >= savedShips.length) {
        showPlacementFeedback('Saved ship not found.');
        return;
    }

    var ship = savedShips[index];

    showPrimaryDiv('shipDesigner');
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
            showPlacementFeedback('Loaded ship "' + ship.name + '" for editing.');
        } else if (waitCount > maxWait) {
            clearInterval(waitInterval);
            showPlacementFeedback('Timeout loading blueprint. Try again.');
        }
    }, 100);
}

function getFleetPayload(fleetState) {
    var savedShips = getSavedShips();
    var fleet = [];

    for (var shipName in fleetState) {
        if (fleetState.hasOwnProperty(shipName) && fleetState[shipName] > 0) {
            for (var i = 0; i < savedShips.length; i++) {
                if (savedShips[i].name === shipName) {
                    for (var j = 0; j < fleetState[shipName]; j++) {
                        fleet.push({
                            name: savedShips[i].name,
                            blueprint: savedShips[i].blueprint,
                            slots: savedShips[i].slots
                        });
                    }
                    break;
                }
            }
        }
    }
    return fleet;
}

function updateRunButtonState() {
    var runBtn = document.getElementById('runBattleBtn');
    if (!runBtn) return;

    var hasA = Object.values(AppState.battle.fleetA).some(function (v) { return v > 0; });
    var hasB = Object.values(AppState.battle.fleetB).some(function (v) { return v > 0; });
    runBtn.disabled = !(hasA && hasB);
}

async function runBattle() {
    var simCountInput = document.getElementById('simCountInput');
    var simCount = parseInt(simCountInput.value, 10);
    if (isNaN(simCount) || simCount < 1) {
        showPlacementFeedback('Enter a valid number of simulations.');
        return;
    }

    AppState.battle.simCount = simCount;

    var fleetA = getFleetPayload(AppState.battle.fleetA);
    var fleetB = getFleetPayload(AppState.battle.fleetB);

    if (fleetA.length === 0 || fleetB.length === 0) {
        showPlacementFeedback('Both fleets must have at least one ship.');
        return;
    }

    var spinner = document.getElementById('battleSpinner');
    var resultsPanel = document.getElementById('battleResults');
    var runBtn = document.getElementById('runBattleBtn');

    if (spinner) spinner.classList.add('active');
    if (resultsPanel) resultsPanel.innerHTML = '';
    if (runBtn) runBtn.disabled = true;

    try {
        var response = await fetch('/api/run_battle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                fleet_a: fleetA,
                fleet_b: fleetB,
                simulations: simCount
            })
        });

        var data = await response.json();

        if (!response.ok) {
            showPlacementFeedback('Battle error: ' + (data.error || 'Unknown error'));
            return;
        }

        AppState.battle.results = data;
        renderResults(data);
    } catch (err) {
        console.error('Battle request failed:', err);
        showPlacementFeedback('Failed to run battle simulation.');
    } finally {
        if (spinner) spinner.classList.remove('active');
        updateRunButtonState();
    }
}

function renderResults(data) {
    var panel = document.getElementById('battleResults');
    if (!panel) return;

    var html = '<h3>Battle Results</h3>';
    html += '<div class="result-row winner-a"><span>Fleet A wins</span><span class="result-value">' + data.a_win_pct + '%</span></div>';
    html += '<div class="result-row winner-b"><span>Fleet B wins</span><span class="result-value">' + data.b_win_pct + '%</span></div>';
    html += '<div class="result-row"><span>Draw</span><span class="result-value">' + data.draw_pct + '%</span></div>';
    html += '<div class="result-row"><span>Simulations</span><span class="result-value">' + data.simulations + '</span></div>';
    html += '<div class="result-row"><span>Avg surviving (A)</span><span class="result-value">' + data.avg_surviving_a + '</span></div>';
    html += '<div class="result-row"><span>Avg surviving (B)</span><span class="result-value">' + data.avg_surviving_b + '</span></div>';

    panel.innerHTML = html;
}

function resetBattle() {
    AppState.battle.fleetA = {};
    AppState.battle.fleetB = {};
    AppState.battle.results = null;

    var simInput = document.getElementById('simCountInput');
    if (simInput) simInput.value = '5000';

    renderFleetList('fleetAList');
    renderFleetList('fleetBList');

    var resultsPanel = document.getElementById('battleResults');
    if (resultsPanel) resultsPanel.innerHTML = '';

    updateRunButtonState();
    showPlacementFeedback('Battle simulator reset.');
}

export function setupBattleSimulator() {
    renderFleetList('fleetAList');
    renderFleetList('fleetBList');

    var runBtn = document.getElementById('runBattleBtn');
    if (runBtn) {
        runBtn.addEventListener('click', runBattle);
    }

    var resetBtn = document.getElementById('resetBattleBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetBattle);
    }

    var simInput = document.getElementById('simCountInput');
    if (simInput) {
        simInput.addEventListener('change', function () {
            var val = parseInt(this.value, 10);
            if (!isNaN(val) && val > 0) {
                AppState.battle.simCount = val;
            }
        });
    }

    updateRunButtonState();
}
