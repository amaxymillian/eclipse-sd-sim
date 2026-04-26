// Backend validation: slot mapping and async part placement validation.

import { AppState } from './state.js';
import { drawOverlay } from './canvas-overlay.js';

export function buildSlotMapping(slots, typeName) {
    var detectedToStatic = {};
    var staticToDetected = {};
    var installedParts = AppState.shipTypesData[typeName] ? AppState.shipTypesData[typeName].installed_parts : [];

    for (var i = 0; i < slots.length; i++) {
        var defaultPart = slots[i].defaultPart;
        if (defaultPart) {
            var staticIdx = -1;
            for (var j = 0; j < installedParts.length; j++) {
                if (installedParts[j] === defaultPart && !staticToDetected[j]) {
                    staticIdx = j;
                    break;
                }
            }
            if (staticIdx >= 0) {
                detectedToStatic[i] = staticIdx;
                staticToDetected[staticIdx] = i;
            }
        }
    }

    for (var i = 0; i < slots.length; i++) {
        if (detectedToStatic[i] === undefined) {
            for (var j = 0; j < installedParts.length; j++) {
                if (!staticToDetected[j]) {
                    detectedToStatic[i] = j;
                    staticToDetected[j] = i;
                    break;
                }
            }
        }
    }

    return { detectedToStatic: detectedToStatic, staticToDetected: staticToDetected };
}

export function validatePartPlacement(partName) {
    if (!AppState.currentBlueprintName) {
        return;
    }

    var typeName = AppState.currentBlueprintName;
    var slots = AppState.blueprintSlotBoxes[AppState.currentBlueprintName];
    if (!slots) return;

    var mapping = buildSlotMapping(slots, typeName);
    var detectedToStatic = mapping.detectedToStatic;
    var staticToDetected = mapping.staticToDetected;

    var shipType = AppState.shipTypesData[typeName];
    var numSlots = shipType ? shipType.slots : slots.length;
    var currentParts = new Array(numSlots).fill(null);
    for (var i = 0; i < slots.length; i++) {
        var staticIdx = detectedToStatic[i];
        if (staticIdx !== undefined && slots[i].partName) {
            currentParts[staticIdx] = slots[i].partName;
        }
    }

    fetch('/api/validate_part_placement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ship_type: typeName, part_name: partName, current_parts: currentParts })
    })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (!slots) return;

            AppState.invalidSlotsForSelectedPart = new Set();

            var invalidStaticSlots = data.invalid_slots || [];
            for (var j = 0; j < invalidStaticSlots.length; j++) {
                var staticIdx = invalidStaticSlots[j];
                if (staticToDetected[staticIdx] !== undefined) {
                    AppState.invalidSlotsForSelectedPart.add(staticToDetected[staticIdx]);
                }
            }

            var staticReasons = data.invalid_reasons || {};

            for (var i = 0; i < slots.length; i++) {
                var staticIdx = detectedToStatic[i] !== undefined ? detectedToStatic[i] : i;
                if (AppState.invalidSlotsForSelectedPart.has(i)) {
                    slots[i].invalid = true;
                    slots[i].invalidReason = staticReasons[String(staticIdx)] || null;
                } else {
                    slots[i].invalid = false;
                    slots[i].invalidReason = null;
                }
            }

            drawOverlay();
        })
        .catch(function (err) {
            console.error('Failed to validate part placement:', err);
        });
}
