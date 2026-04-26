// Core interaction: slot hit detection, part placement/removal, drag-and-drop,
// blueprint selection, and view switching.

import { AppState } from './state.js';
import { drawOverlay, loadGridSlots, updateSlotLabels } from './canvas-overlay.js';
import { updateShipStats, loadShipTypeInfo, loadShipData } from './stats.js';
import { validatePartPlacement } from './validation.js';
import { showPlacementFeedback } from './feedback.js';

// ===== Slot Interaction =====

export function getSlotAtPosition(x, y) {
    console.log('[DIAG] getSlotAtPosition: x=', x, 'y=', y, 'currentBlueprintName=', AppState.currentBlueprintName);
    var slots = AppState.blueprintSlotBoxes[AppState.currentBlueprintName];
    if (!slots) {
        console.log('[DIAG] getSlotAtPosition: no slots found for current blueprint');
        return -1;
    }
    console.log('[DIAG] getSlotAtPosition: checking', slots.length, 'slots');
    for (var i = 0; i < slots.length; i++) {
        var s = slots[i];
        console.log('[DIAG] getSlotAtPosition: slot', i, '=', { x: s.x, y: s.y, w: s.w, h: s.h }, 'occupied:', s.occupied, 'invalid:', s.invalid);
        if (x >= s.x && x <= s.x + s.w && y >= s.y && y <= s.y + s.h) {
            console.log('[DIAG] getSlotAtPosition: MATCH found at slot', i);
            return i;
        }
    }
    console.log('[DIAG] getSlotAtPosition: no match found');
    return -1;
}

function validatePartPlacementSync(slotIndex, partName) {
    var slots = AppState.blueprintSlotBoxes[AppState.currentBlueprintName];
    if (!slots || !AppState.currentBlueprintName) return null;

    var shipType = AppState.shipTypesData[AppState.currentBlueprintName];
    if (!shipType) return null;

    var partData = AppState.shipPartsData[partName];
    if (!partData) return null;

    var partEnergy = partData.energy || 0;
    var oldPartName = slots[slotIndex].partName;
    var oldEnergy = 0;
    if (oldPartName) {
        var oldPartData = AppState.shipPartsData[oldPartName];
        if (oldPartData) {
            oldEnergy = oldPartData.energy || 0;
        }
    }

    var energyPool = shipType.bonus_energy || 0;
    var totalEnergyCost = 0;
    var driveCount = 0;
    var oldIsDrive = false;

    for (var i = 0; i < slots.length; i++) {
        var currentPartName = slots[i].partName;
        if (!currentPartName) continue;

        var currentPartData = AppState.shipPartsData[currentPartName];
        if (!currentPartData) continue;

        var energy = currentPartData.energy || 0;
        if (energy > 0) {
            energyPool += energy;
        } else if (energy < 0) {
            totalEnergyCost += Math.abs(energy);
        }

        if (currentPartData.type === 'drive') {
            driveCount++;
            if (i === slotIndex) {
                oldIsDrive = true;
            }
        }
    }

    var currentAvailableEnergy = energyPool - totalEnergyCost;

    var newAvailableEnergy = currentAvailableEnergy - oldEnergy + partEnergy;
    if (newAvailableEnergy < 0) {
        return 'Insufficient energy. Placing ' + partName + ' would require ' + Math.abs(newAvailableEnergy) + ' more energy available.';
    }

    var newIsDrive = partData.type === 'drive';
    var effectiveDriveCount = driveCount;
    if (oldIsDrive) {
        effectiveDriveCount -= 1;
    }

    if (!newIsDrive && effectiveDriveCount < 1) {
        if (oldIsDrive) {
            return 'Cannot remove the last drive. Replacing ' + oldPartName + ' with ' + partName + ' would leave the ship with no drive.';
        } else {
            return 'Cannot place ' + partName + '. The ship would have no drive installed.';
        }
    }

    return null;
}

export function placePart(slotIndex, partName) {
    console.log('[DIAG] placePart called: slotIndex=', slotIndex, 'partName=', partName);
    var slots = AppState.blueprintSlotBoxes[AppState.currentBlueprintName];
    if (!slots) {
        console.log('[DIAG] placePart: NO SLOTS for', AppState.currentBlueprintName);
        return;
    }
    if (!slots[slotIndex]) {
        console.log('[DIAG] placePart: slot', slotIndex, 'does not exist (total slots:', slots.length, ')');
        return;
    }

    if (slots[slotIndex].invalid) {
        console.log('[DIAG] placePart: slot', slotIndex, 'is invalid - reason:', slots[slotIndex].invalidReason);
        showPlacementFeedback(slots[slotIndex].invalidReason);
        return;
    }

    var syncError = validatePartPlacementSync(slotIndex, partName);
    if (syncError) {
        console.log('[DIAG] placePart: synchronous validation failed -', syncError);
        slots[slotIndex].invalid = true;
        slots[slotIndex].invalidReason = syncError;
        showPlacementFeedback(syncError);
        drawOverlay();
        return;
    }

    if (slots[slotIndex].occupied && slots[slotIndex].partName === partName) {
        console.log('[DIAG] placePart: slot already has this part, skipping');
        return;
    }

    console.log('[DIAG] placePart: placing', partName, 'in slot', slotIndex);
    slots[slotIndex].occupied = true;
    slots[slotIndex].partName = partName;
    slots[slotIndex].invalid = false;
    slots[slotIndex].invalidReason = null;
    drawOverlay();
    updateShipStats();
    console.log('[DIAG] placePart: done, slot is now:', slots[slotIndex]);
}

export function removePart(slotIndex) {
    console.log('[DIAG] removePart called: slotIndex=', slotIndex);
    var slots = AppState.blueprintSlotBoxes[AppState.currentBlueprintName];
    if (!slots || !slots[slotIndex]) return;
    slots[slotIndex].occupied = false;
    slots[slotIndex].partName = null;
    drawOverlay();
    updateShipStats();
}

// ===== Drag and Drop =====

export function onDragStart(event, partName) {
    console.log('[DIAG] onDragStart: partName =', partName);
    event.dataTransfer.setData('text/plain', partName);
    event.dataTransfer.effectAllowed = 'copy';
    AppState.selectedPartName = partName;
    validatePartPlacement(partName);

    var img = event.target;
    img.style.opacity = '0.5';
    setTimeout(function () { img.style.opacity = '1'; }, 100);
}

// ===== UI Functions =====

export function showPrimaryDiv(divToShow) {
    var shipDesigner = document.getElementById("shipDesigner");
    var battleSimulator = document.getElementById("battleSimulator");
    switch (divToShow) {
        case "shipDesigner":
            shipDesigner.style.display = "block";
            battleSimulator.style.display = "none";
            break;
        case "battleSimulator":
            shipDesigner.style.display = "none";
            battleSimulator.style.display = "block";
            break;
    }
}

export function addPartToShip(partName) {
    console.log('[DIAG] addPartToShip called: partName =', partName);
    AppState.selectedPartName = partName;

    document.querySelectorAll('.part-image').forEach(function (img) {
        img.classList.remove('selected');
        if (img.src.indexOf(partName) !== -1) {
            img.classList.add('selected');
        }
    });

    validatePartPlacement(partName);
}

export function selectBlueprint(blueprintName) {
    var shipBlueprintCanvas = document.getElementById('shipBlueprintCanvas');
    var overlayCanvas = document.getElementById('overlayCanvas');
    var loadingDiv = document.getElementById("shipBluePrintLoadingDiv");
    var shipDesigner = document.getElementById("shipDesigner");

    console.log('selectBlueprint called with:', blueprintName);

    if (!shipBlueprintCanvas || !overlayCanvas) {
        console.error('Canvas elements not found!');
        return;
    }

    shipDesigner.style.display = "block";
    loadingDiv.style.display = "block";

    var blueprintImages = document.querySelectorAll('.blueprint-thumb[src*="blueprints/"]');
    var existingImg = null;
    for (var i = 0; i < blueprintImages.length; i++) {
        var src = blueprintImages[i].src;
        if (src && src.indexOf(blueprintName + '.png') !== -1) {
            existingImg = blueprintImages[i];
            console.log('Found existing blueprint image:', src);
            break;
        }
    }

    var image = existingImg || new Image();

    function handleImageLoad() {
        console.log('handleImageLoad called, natural size:', image.naturalWidth, 'x', image.naturalHeight);
        try {
            if (image.naturalWidth === 0 || image.naturalHeight === 0) {
                throw new Error('Image has zero dimensions (' + image.naturalWidth + 'x' + image.naturalHeight + ')');
            }
            shipBlueprintCanvas.width = image.naturalWidth;
            shipBlueprintCanvas.height = image.naturalHeight;

            overlayCanvas.width = image.naturalWidth;
            overlayCanvas.height = image.naturalHeight;

            var containerWidth = document.getElementById('shipBlueprintDiv').clientWidth;
            var scale = 1;
            if (image.naturalWidth > containerWidth) {
                scale = containerWidth / image.naturalWidth;
            }
            var displayWidth = Math.floor(image.naturalWidth * scale);
            var displayHeight = Math.floor(image.naturalHeight * scale);

            shipBlueprintCanvas.style.width = displayWidth + 'px';
            shipBlueprintCanvas.style.height = displayHeight + 'px';
            overlayCanvas.style.width = displayWidth + 'px';
            overlayCanvas.style.height = displayHeight + 'px';

            var canvasContainer = document.getElementById('canvasContainer');
            if (canvasContainer) {
                canvasContainer.style.width = displayWidth + 'px';
                canvasContainer.style.height = displayHeight + 'px';
            }

            console.log('[DIAG] Canvas set: internal dimensions =', image.naturalWidth, 'x', image.naturalHeight);
            var overlayRect = overlayCanvas.getBoundingClientRect();
            console.log('[DIAG] Canvas set: overlay display size =', overlayRect);
            console.log('[DIAG] Canvas set: overlay style.width =', overlayCanvas.style.width, 'style.height =', overlayCanvas.style.height);
            console.log('[DIAG] Canvas set: overlay computed pointer-events =', getComputedStyle(overlayCanvas).pointerEvents);
            console.log('[DIAG] Canvas set: overlay computed cursor =', getComputedStyle(overlayCanvas).cursor);

            if (overlayRect.width === 0 || overlayRect.height === 0) {
                console.error('[DIAG] ERROR: Overlay canvas has 0 size! Pointer events will NOT work!');
            }

            var ctx = shipBlueprintCanvas.getContext('2d');
            ctx.clearRect(0, 0, shipBlueprintCanvas.width, shipBlueprintCanvas.height);
            ctx.drawImage(image, 0, 0);

            AppState.currentBlueprintName = blueprintName;
            AppState.blueprintSlotBoxes[blueprintName] = [];
            loadGridSlots(shipBlueprintCanvas, ctx, blueprintName, function (slots) {
                drawOverlay();
                loadShipTypeInfo(blueprintName, function () {
                    console.log('Ship type info loaded for', blueprintName);
                    updateSlotLabels();
                    loadShipData(function () {
                        console.log('[DIAG] Ship data loaded successfully');
                        updateShipStats();
                        loadingDiv.style.display = "none";
                        console.log('Blueprint displayed successfully');
                    });
                });
            });
        } catch (e) {
            console.error('Error drawing blueprint:', e);
            loadingDiv.style.display = "none";
            loadingDiv.textContent = 'Error: ' + e.message;
            loadingDiv.style.display = "block";
        }
    }

    if (existingImg) {
        console.log('Using existing DOM image');
        if (existingImg.naturalWidth > 0) {
            handleImageLoad();
        } else {
            console.log('Existing image not decoded yet, waiting...');
            var waitCount = 0;
            var waitInterval = setInterval(function () {
                waitCount++;
                if (existingImg.naturalWidth > 0) {
                    clearInterval(waitInterval);
                    handleImageLoad();
                } else if (waitCount > 50) {
                    clearInterval(waitInterval);
                    console.error('Existing image never decoded');
                    loadingDiv.style.display = "none";
                    loadingDiv.textContent = 'Failed to decode blueprint image';
                    loadingDiv.style.display = "block";
                }
            }, 100);
        }
    } else {
        var imageUrl = '/static/images/blueprints/' + blueprintName + '.png';
        var newImage = new Image();
        var loadTriggered = false;

        newImage.onerror = function () {
            console.error('Failed to load image:', imageUrl);
            if (!loadTriggered) {
                loadTriggered = true;
                loadingDiv.style.display = "none";
                loadingDiv.textContent = 'Failed to load blueprint image';
                loadingDiv.style.display = "block";
            }
        };

        newImage.onload = function () {
            console.log('New image loaded:', imageUrl);
            if (!loadTriggered) {
                loadTriggered = true;
                handleImageLoad();
            }
        };

        newImage.src = imageUrl;
        console.log('Loading new image from:', imageUrl);
    }
}
