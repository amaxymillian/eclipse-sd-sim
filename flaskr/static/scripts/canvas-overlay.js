// Canvas overlay drawing: slot borders, part images, labels.
// Also includes bounding box detection and grid slot loading.

import { AppState, WHITE_THRESHOLD } from './state.js';

// ===== Bounding Box Detection =====

function verifyVerticalEdge(data, width, col, topRow, bottomRow, threshold) {
    var whiteCount = 0;
    var totalCount = 0;
    var height = data.length / 4 / width;
    for (var row = topRow; row <= bottomRow; row++) {
        if (row < 0 || row >= height) continue;
        var idx = (row * width + col) * 4;
        totalCount++;
        if (data[idx] > threshold && data[idx + 1] > threshold && data[idx + 2] > threshold) {
            whiteCount++;
        }
    }
    return totalCount > 0 && (whiteCount / totalCount) > 0.5;
}

export { verifyVerticalEdge };

function deduplicateSlots(slots) {
    var result = [];
    for (var i = 0; i < slots.length; i++) {
        var dominated = false;
        for (var j = 0; j < slots.length; j++) {
            if (i === j) continue;
            if (slots[j].x <= slots[i].x && slots[j].y <= slots[i].y &&
                slots[j].x + slots[j].w >= slots[i].x + slots[i].w &&
                slots[j].y + slots[j].h >= slots[i].y + slots[i].h) {
                var areaI = slots[i].w * slots[i].h;
                var areaJ = slots[j].w * slots[j].h;
                if (areaJ > areaI * 1.5) { dominated = true; break; }
            }
        }
        if (!dominated) result.push(slots[i]);
    }
    return result;
}

export { deduplicateSlots };

export function loadGridSlots(canvas, ctx, blueprintName, callback) {
    console.log('loadGridSlots starting for:', blueprintName, 'canvas:', canvas.width, 'x', canvas.height);
    var url = '/api/ship_type_grid/' + blueprintName;
    console.log('Fetching grid data from:', url);

    fetch(url)
        .then(function (response) {
            if (!response.ok) {
                throw new Error('HTTP ' + response.status + ' for ' + url);
            }
            return response.json();
        })
        .then(function (data) {
            console.log('Grid data received:', data);
            var slots = [];
            if (data.slots) {
                for (var i = 0; i < data.slots.length; i++) {
                    var s = data.slots[i];
                    var hasDefault = s.default_part !== null && s.default_part !== undefined;
                    slots.push({
                        x: s.x,
                        y: s.y,
                        w: s.width,
                        h: s.height,
                        occupied: hasDefault,
                        partName: hasDefault ? s.default_part : null,
                        invalid: false,
                        invalidReason: null,
                        slotType: s.slot_type,
                        defaultPart: s.default_part,
                        gridRow: s.grid_row ?? null,
                        gridCol: s.grid_col ?? null,
                    });
                }
            }
            AppState.blueprintSlotBoxes[blueprintName] = slots;
            console.log('[DIAG] loadGridSlots found', slots.length, 'slots for', blueprintName);
            if (callback) callback(slots);
        })
        .catch(function (e) {
            console.error('loadGridSlots failed:', e);
            AppState.blueprintSlotBoxes[blueprintName] = [];
            if (callback) callback([]);
        });
}

function verifyHorizontalEdge(data, width, row, startX, endX, threshold) {
    var whiteCount = 0;
    var totalCount = 0;
    for (var col = startX; col <= endX; col++) {
        if (col < 0 || col >= width) continue;
        var idx = (row * width + col) * 4;
        totalCount++;
        if (data[idx] > threshold && data[idx + 1] > threshold && data[idx + 2] > threshold) {
            whiteCount++;
        }
    }
    return totalCount > 0 && (whiteCount / totalCount) > 0.5;
}

export { verifyHorizontalEdge };

// ===== Overlay Drawing =====

export function drawOverlay() {
    var overlay = document.getElementById('overlayCanvas');
    var blueprintCanvas = document.getElementById('shipBlueprintCanvas');
    if (!overlay || !blueprintCanvas) return;

    try {
        overlay.width = blueprintCanvas.width;
        overlay.height = blueprintCanvas.height;
        var ctx = overlay.getContext('2d');
        ctx.clearRect(0, 0, overlay.width, overlay.height);

        var slots = AppState.blueprintSlotBoxes[AppState.currentBlueprintName];
        if (!slots) return;

        for (var i = 0; i < slots.length; i++) {
            var s = slots[i];

            if (s.invalid) {
                ctx.fillStyle = 'rgba(255, 0, 0, 0.25)';
                ctx.fillRect(s.x, s.y, s.w, s.h);
            } else if (s.occupied) {
                ctx.fillStyle = 'rgba(55, 123, 168, 0.12)';
                ctx.fillRect(s.x, s.y, s.w, s.h);
            }

            if (s.occupied) {
                ctx.strokeStyle = '#2e7d32';
                ctx.lineWidth = 3;
            } else if (s.invalid) {
                ctx.strokeStyle = '#d32f2f';
                ctx.lineWidth = 2;
                var margin = 4;
                ctx.beginPath();
                ctx.moveTo(s.x + margin, s.y + margin);
                ctx.lineTo(s.x + s.w - margin, s.y + s.h - margin);
                ctx.moveTo(s.x + s.w - margin, s.y + margin);
                ctx.lineTo(s.x + margin, s.y + s.h - margin);
                ctx.stroke();
            } else if (i === AppState.hoveredSlotIndex) {
                ctx.strokeStyle = '#64b5f6';
                ctx.lineWidth = 3;
            } else {
                ctx.strokeStyle = '#1565c0';
                ctx.lineWidth = 2;
            }
            ctx.strokeRect(s.x, s.y, s.w, s.h);

            if (s.occupied && s.partName) {
                drawPartImage(ctx, s.partName, s.x + 2, s.y + 2, s.w - 4, s.h - 4);
            }

            drawSlotLabelText(ctx, s, i);
        }
    } catch (e) {
        console.error('drawOverlay error:', e);
    }
}

export function drawPartImage(ctx, partName, x, y, w, h) {
    if (!AppState.overlayImagesLoaded[partName]) {
        var img = new Image();
        img.src = '/static/images/parts/' + partName + '.png';
        AppState.overlayImagesLoaded[partName] = img;
    }
    var img = AppState.overlayImagesLoaded[partName];
    if (img && img.complete && img.naturalWidth > 0) {
        ctx.drawImage(img, x, y, w, h);
    }
}

// ===== Slot Label Display =====

export function updateSlotLabels() {
    if (!AppState.currentBlueprintName || !AppState.currentShipTypeInfo) return;

    var slots = AppState.blueprintSlotBoxes[AppState.currentBlueprintName];
    if (!slots) return;

    var partTypes = AppState.currentShipTypeInfo.part_types || [];
    var slotLabels = AppState.currentShipTypeInfo.slot_labels || [];

    for (var i = 0; i < slots.length; i++) {
        if (slots[i].slotType) {
            slots[i].partType = slots[i].slotType;
        } else if (i < partTypes.length) {
            slots[i].partType = partTypes[i];
        }
        if (slotLabels[i] !== undefined) {
            slots[i].slotLabel = slotLabels[i] || null;
        }
    }

    drawOverlay();
}

export function drawSlotLabelText(ctx, slot, index) {
    if (!slot.partType) return;

    var label = slot.partType.charAt(0).toUpperCase() + slot.partType.slice(1);
    ctx.font = 'bold ' + Math.max(8, slot.w / 6) + 'px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';

    var textX = slot.x + slot.w / 2;
    var textY = slot.y + slot.h - 4;
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.lineWidth = 2;
    ctx.strokeText(label, textX, textY);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
    ctx.fillText(label, textX, textY);
}
