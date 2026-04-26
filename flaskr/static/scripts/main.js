// Main entry point for the Eclipse SD Sim frontend application.
// Imports all modules, wires up data-* attribute event listeners,
// and bootstraps the application on DOMContentLoaded.

import { setupOverlayHandlers } from './handlers.js';
import { setupDropdownHandlers } from './dropdowns.js';
import { updateSavedShipsMenu } from './saved-ships.js';
import { selectBlueprint, onDragStart, addPartToShip, showPrimaryDiv } from './interaction.js';
import { saveCurrentShip, exportCurrentShip, importShipFromEvent } from './saved-ships.js';

function setupDataAttributeHandlers() {
    // Blueprint thumbnail clicks
    document.querySelectorAll('.blueprint-thumb').forEach(function (img) {
        img.addEventListener('click', function () {
            var blueprintName = this.getAttribute('data-blueprint');
            if (blueprintName) {
                selectBlueprint(blueprintName);
            }
        });
    });

    // Part image clicks and drag starts
    document.querySelectorAll('.part-image').forEach(function (img) {
        var partName = img.getAttribute('data-part');
        if (!partName) return;

        img.addEventListener('click', function () {
            addPartToShip(partName);
        });

        img.addEventListener('dragstart', function (event) {
            onDragStart(event, partName);
        });
    });

    // View switching (data-view attributes)
    document.querySelectorAll('[data-view]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            e.preventDefault();
            var view = this.getAttribute('data-view');
            if (view) {
                showPrimaryDiv(view);
            }
        });
    });

    // Ship designer menu actions
    var saveShipBtn = document.querySelector('[data-action="save-ship"]');
    if (saveShipBtn) {
        saveShipBtn.addEventListener('click', function (e) {
            e.preventDefault();
            saveCurrentShip();
        });
    }

    var exportShipBtn = document.querySelector('[data-action="export-ship"]');
    if (exportShipBtn) {
        exportShipBtn.addEventListener('click', function (e) {
            e.preventDefault();
            exportCurrentShip();
        });
    }

    // Import ship file input
    var importInput = document.getElementById('importShipFile');
    if (importInput) {
        importInput.addEventListener('change', function (event) {
            importShipFromEvent(event);
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('[DIAG] DOMContentLoaded: initializing overlay handlers');
    setupOverlayHandlers();
    setupDropdownHandlers();
    setupDataAttributeHandlers();
    updateSavedShipsMenu();
});
