// Event handlers for overlay canvas.

import { AppState } from './state.js';
import { drawOverlay } from './canvas-overlay.js';
import { getSlotAtPosition, placePart, removePart } from './interaction.js';
import { showPlacementFeedback } from './feedback.js';

export function setupOverlayHandlers() {
    var overlay = document.getElementById('overlayCanvas');
    console.log('[DIAG] setupOverlayHandlers starting: overlay element found:', !!overlay);
    if (!overlay) return;

    console.log('[DIAG] setupOverlayHandlers: overlay internal dimensions - width:', overlay.width, 'height:', overlay.height);
    var overlayRect = overlay.getBoundingClientRect();
    console.log('[DIAG] setupOverlayHandlers: overlay display size -', overlayRect);
    console.log('[DIAG] setupOverlayHandlers: overlay style.width =', overlay.style.width, 'style.height =', overlay.style.height);
    console.log('[DIAG] setupOverlayHandlers: overlay computed pointer-events =', getComputedStyle(overlay).pointerEvents);
    console.log('[DIAG] setupOverlayHandlers: overlay computed cursor =', getComputedStyle(overlay).cursor);

    if (overlayRect.width === 0 || overlayRect.height === 0) {
        console.warn('[DIAG] setupOverlayHandlers: overlay canvas has 0 size at setup time - will check again after blueprint selection');
    }

    overlay.addEventListener('dragover', function (event) {
        console.log('[DIAG] dragover event fired on overlay');
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
    });

    overlay.addEventListener('drop', function (event) {
        console.log('[DIAG] DROP event fired on overlay', {
            clientX: event.clientX,
            clientY: event.clientY,
            partName: event.dataTransfer.getData('text/plain')
        });
        event.preventDefault();
        var rect = overlay.getBoundingClientRect();
        console.log('[DIAG] drop: overlay rect =', rect);
        var scaleX = overlay.width / rect.width;
        var scaleY = overlay.height / rect.height;
        console.log('[DIAG] drop: scale factors =', scaleX, scaleY);
        var x = (event.clientX - rect.left) * scaleX;
        var y = (event.clientY - rect.top) * scaleY;
        console.log('[DIAG] drop: calculated coords =', x, y);

        var partName = event.dataTransfer.getData('text/plain');
        var slotIndex = getSlotAtPosition(x, y);
        console.log('[DIAG] drop: slotIndex =', slotIndex, 'partName =', partName);
        if (slotIndex >= 0 && partName) {
            placePart(slotIndex, partName);
        } else {
            var slots = AppState.blueprintSlotBoxes[AppState.currentBlueprintName];
            console.log('[DIAG] drop: slots for current blueprint =', slots ? slots.length : 'none', 'currentBlueprintName =', AppState.currentBlueprintName);
        }
    });

    overlay.addEventListener('click', function (event) {
        console.log('[DIAG] CLICK event fired on overlay', {
            clientX: event.clientX,
            clientY: event.clientY,
            selectedPartName: AppState.selectedPartName
        });
        var rect = overlay.getBoundingClientRect();
        var scaleX = overlay.width / rect.width;
        var scaleY = overlay.height / rect.height;
        var x = (event.clientX - rect.left) * scaleX;
        var y = (event.clientY - rect.top) * scaleY;
        console.log('[DIAG] click: calculated coords =', x, y);

        var slotIndex = getSlotAtPosition(x, y);
        console.log('[DIAG] click: slotIndex =', slotIndex);
        if (slotIndex >= 0) {
            var slots = AppState.blueprintSlotBoxes[AppState.currentBlueprintName];
            console.log('[DIAG] click: slots[', slotIndex, '].occupied =', slots && slots[slotIndex] ? slots[slotIndex].occupied : 'N/A');
            if (AppState.selectedPartName) {
                if (slots && slots[slotIndex] && slots[slotIndex].invalid) {
                    console.log('[DIAG] click: slot', slotIndex, 'is invalid - showing feedback');
                    showPlacementFeedback(slots[slotIndex].invalidReason);
                    return;
                }
                placePart(slotIndex, AppState.selectedPartName);
            } else if (slots && slots[slotIndex] && slots[slotIndex].occupied) {
                removePart(slotIndex);
            }
        }
    });

    overlay.addEventListener('contextmenu', function (event) {
        event.preventDefault();
        var rect = overlay.getBoundingClientRect();
        var scaleX = overlay.width / rect.width;
        var scaleY = overlay.height / rect.height;
        var x = (event.clientX - rect.left) * scaleX;
        var y = (event.clientY - rect.top) * scaleY;

        var slotIndex = getSlotAtPosition(x, y);
        if (slotIndex >= 0) {
            removePart(slotIndex);
        }
    });

    overlay.addEventListener('mousemove', function (event) {
        var rect = overlay.getBoundingClientRect();
        var scaleX = overlay.width / rect.width;
        var scaleY = overlay.height / rect.height;
        var x = (event.clientX - rect.left) * scaleX;
        var y = (event.clientY - rect.top) * scaleY;

        var newHoveredIndex = getSlotAtPosition(x, y);
        if (newHoveredIndex !== AppState.hoveredSlotIndex) {
            AppState.hoveredSlotIndex = newHoveredIndex;
            drawOverlay();
        }
    });

    overlay.addEventListener('mouseleave', function () {
        if (AppState.hoveredSlotIndex !== -1) {
            AppState.hoveredSlotIndex = -1;
            drawOverlay();
        }
    });

    console.log('[DIAG] setupOverlayHandlers: all event listeners attached to overlay');
    console.log('[DIAG] setupOverlayHandlers: overlay style.pointerEvents =', getComputedStyle(overlay).pointerEvents);
    console.log('[DIAG] setupOverlayHandlers: overlay computed position =', getComputedStyle(overlay).position);
}
