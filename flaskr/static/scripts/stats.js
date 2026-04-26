// Ship statistics: API data loading, stat calculation, display updates.

import { AppState } from './state.js';

export function loadShipData(callback) {
    fetch('/api/ship_parts')
        .then(function (response) { return response.json(); })
        .then(function (data) {
            AppState.shipPartsData = data;
            return fetch('/api/ship_types');
        })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            AppState.shipTypesData = data;
            if (callback) callback();
        })
        .catch(function (err) {
            console.error('Failed to load ship data:', err);
        });
}

export function loadShipTypeInfo(blueprintName, callback) {
    fetch('/api/ship_types/' + blueprintName)
        .then(function (response) { return response.json(); })
        .then(function (data) {
            AppState.currentShipTypeInfo = data;
            return fetch('/api/ship_type_mapping/' + blueprintName);
        })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            AppState.currentSlotMapping = data.mapping || {};
            return fetch('/api/initial_stats/' + blueprintName);
        })
        .then(function (response) {
            if (!response.ok) {
                console.error('Failed to load initial stats for ' + blueprintName);
                AppState.currentShipStats = null;
                return;
            }
            return response.json();
        })
        .then(function (initialData) {
            if (initialData && initialData.stats) {
                var raw = initialData.stats;
                AppState.currentShipStats = {
                    shielding: raw.shielding,
                    energy: raw.energy,
                    availableEnergy: raw.available_energy,
                    initiative: raw.initiative,
                    armor: raw.armor,
                    targeting: raw.targeting,
                    hp: raw.hp,
                    maxHp: raw.hp
                };
            }
            if (callback) callback();
        })
        .catch(function (err) {
            console.error('Failed to load ship type info for ' + blueprintName + ':', err);
            AppState.currentShipTypeInfo = null;
            AppState.currentSlotMapping = {};
            AppState.currentShipStats = null;
        });
}

export function calculateShipStats(blueprintName) {
    var typeName = blueprintName;
    var shipType = AppState.shipTypesData[typeName];
    if (!shipType) {
        AppState.currentShipStats = null;
        return null;
    }

    var slots = AppState.blueprintSlotBoxes[blueprintName];
    if (!slots) {
        AppState.currentShipStats = null;
        return null;
    }

    var hasUserParts = false;
    for (var i = 0; i < slots.length; i++) {
        if (slots[i].partName) {
            hasUserParts = true;
            break;
        }
    }

    if (!hasUserParts && AppState.currentShipStats) {
        return AppState.currentShipStats;
    }

    var totalShielding = 0;
    var energyPool = shipType.bonus_energy;
    var totalEnergyCost = 0;
    var initiative = shipType.base_initiative;
    var armor = 0;
    var targeting = shipType.bonus_targeting;

    for (var i = 0; i < slots.length; i++) {
        var partName = slots[i].partName;
        if (!partName) continue;

        var partData = AppState.shipPartsData[partName];
        if (!partData) continue;

        if ('shielding' in partData) {
            totalShielding += partData.shielding;
        }
        if ('energy' in partData) {
            if (partData.energy > 0) {
                energyPool += partData.energy;
            } else if (partData.energy < 0) {
                totalEnergyCost += Math.abs(partData.energy);
            }
        }
        if ('initiative' in partData) {
            initiative += partData.initiative;
        }
        if ('armor' in partData) {
            armor += partData.armor;
        }
        if ('targeting' in partData) {
            targeting += partData.targeting;
        }
    }

    var hitPoints = 1 + armor;
    var availableEnergy = energyPool - totalEnergyCost;

    AppState.currentShipStats = {
        shielding: totalShielding,
        energy: energyPool,
        availableEnergy: availableEnergy,
        initiative: initiative,
        armor: armor,
        targeting: targeting,
        hp: hitPoints,
        maxHp: hitPoints
    };

    return AppState.currentShipStats;
}

export function updateStatsDisplay() {
    var stats = AppState.currentShipStats;
    if (!stats) {
        document.getElementById('statShielding').textContent = '-';
        document.getElementById('statEnergy').textContent = '-';
        document.getElementById('statAvailEnergy').textContent = '-';
        document.getElementById('statInitiative').textContent = '-';
        document.getElementById('statArmor').textContent = '-';
        document.getElementById('statTargeting').textContent = '-';
        document.getElementById('statHP').textContent = '-';
        return;
    }

    document.getElementById('statShielding').textContent = stats.shielding;
    document.getElementById('statEnergy').textContent = stats.energy;
    document.getElementById('statAvailEnergy').textContent = stats.availableEnergy;
    document.getElementById('statInitiative').textContent = stats.initiative;
    document.getElementById('statArmor').textContent = stats.armor;
    document.getElementById('statTargeting').textContent = stats.targeting;
    document.getElementById('statHP').textContent = stats.hp;

    updateInstalledPartsList();
}

export function updateInstalledPartsList() {
    var listEl = document.getElementById('installedPartsList');
    if (!AppState.currentBlueprintName) {
        listEl.textContent = 'None';
        return;
    }

    var slots = AppState.blueprintSlotBoxes[AppState.currentBlueprintName];
    if (!slots) {
        listEl.textContent = 'None';
        return;
    }

    var parts = [];
    for (var i = 0; i < slots.length; i++) {
        if (slots[i].partName) {
            var slotLabel = slots[i].partType ? ' (' + slots[i].partType + ')' : '';
            parts.push('Slot ' + (i + 1) + ': ' + slots[i].partName + slotLabel);
        }
    }

    if (parts.length === 0) {
        listEl.textContent = 'None';
    } else {
        listEl.innerHTML = parts.join('<br>');
    }
}

export function updateShipStats() {
    if (!AppState.currentBlueprintName) return;
    calculateShipStats(AppState.currentBlueprintName);
    updateStatsDisplay();
}
