// State: cached slot boxes per blueprint
var blueprintSlotBoxes = {};

// State: currently selected part for click-to-place
var selectedPartName = null;

// State: currently hovered slot index on overlay
var hoveredSlotIndex = -1;

// State: loaded part images for overlay drawing
var overlayImagesLoaded = {};

// State: current blueprint being displayed
var currentBlueprintName = null;

// State: invalid slots for the currently selected part (set of slot indices)
var invalidSlotsForSelectedPart = new Set();

// State: last validation result for user feedback
var lastValidationFeedback = null;

// Ship types served by the API - removed from frontend
// See /api/ship_types/<ship_type_name> for dynamic data

const WHITE_THRESHOLD = 150;

// ===== Bounding Box Detection =====

function verifyVerticalEdge(data, width, col, topRow, bottomRow, threshold) {
    var whiteCount = 0;
    var totalCount = 0;
    var height = data.length / 4 / width;
    for (var row = topRow; row <= bottomRow; row++) {
        if (row < 0 || row >= height) continue;
        var idx = (row * width + col) * 4;
        totalCount++;
        if (data[idx] > threshold && data[idx+1] > threshold && data[idx+2] > threshold) {
            whiteCount++;
        }
    }
    return totalCount > 0 && (whiteCount / totalCount) > 0.5;
}

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

function loadGridSlots(canvas, ctx, blueprintName, callback) {
    console.log('loadGridSlots starting for:', blueprintName, 'canvas:', canvas.width, 'x', canvas.height);
    var url = '/api/ship_type_grid/' + blueprintName;
    console.log('Fetching grid data from:', url);

    fetch(url)
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP ' + response.status + ' for ' + url);
            }
            return response.json();
        })
        .then(function(data) {
            console.log('Grid data received:', data);
            var slots = [];
            if (data.slots) {
                for (var i = 0; i < data.slots.length; i++) {
                    var s = data.slots[i];
                    slots.push({
                        x: s.x,
                        y: s.y,
                        w: s.width,
                        h: s.height,
                        occupied: false,
                        partName: null,
                        invalid: false,
                        invalidReason: null,
                        slotType: s.slot_type,
                        defaultPart: s.default_part,
                        gridRow: s.grid_row ?? null,
                        gridCol: s.grid_col ?? null,
                    });
                }
            }
            blueprintSlotBoxes[blueprintName] = slots;
            console.log('[DIAG] loadGridSlots found', slots.length, 'slots for', blueprintName);
            if (callback) callback(slots);
        })
        .catch(function(e) {
            console.error('loadGridSlots failed:', e);
            blueprintSlotBoxes[blueprintName] = [];
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
        if (data[idx] > threshold && data[idx+1] > threshold && data[idx+2] > threshold) {
            whiteCount++;
        }
    }
    return totalCount > 0 && (whiteCount / totalCount) > 0.5;
}

// ===== Overlay Drawing =====

function drawOverlay() {
    var overlay = document.getElementById('overlayCanvas');
    var blueprintCanvas = document.getElementById('shipBlueprintCanvas');
    if (!overlay || !blueprintCanvas) return;

    try {
        overlay.width = blueprintCanvas.width;
        overlay.height = blueprintCanvas.height;
        var ctx = overlay.getContext('2d');
        ctx.clearRect(0, 0, overlay.width, overlay.height);

        var slots = blueprintSlotBoxes[currentBlueprintName];
        if (!slots) return;

        for (var i = 0; i < slots.length; i++) {
            var s = slots[i];

            // Draw translucent red tint for invalid slots
            if (s.invalid) {
                ctx.fillStyle = 'rgba(255, 0, 0, 0.25)';
                ctx.fillRect(s.x, s.y, s.w, s.h);
            } else if (s.occupied) {
                ctx.fillStyle = 'rgba(55, 123, 168, 0.12)';
                ctx.fillRect(s.x, s.y, s.w, s.h);
            }

            // Draw border based on slot state
            if (s.occupied) {
                ctx.strokeStyle = '#2e7d32';
                ctx.lineWidth = 3;
            } else if (s.invalid) {
                ctx.strokeStyle = '#d32f2f';
                ctx.lineWidth = 2;
                // Draw an X for invalid slots
                var margin = 4;
                ctx.beginPath();
                ctx.moveTo(s.x + margin, s.y + margin);
                ctx.lineTo(s.x + s.w - margin, s.y + s.h - margin);
                ctx.moveTo(s.x + s.w - margin, s.y + margin);
                ctx.lineTo(s.x + margin, s.y + s.h - margin);
                ctx.stroke();
            } else if (i === hoveredSlotIndex) {
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

            // Draw slot type label
            drawSlotLabelText(ctx, s, i);
        }
    } catch(e) {
        console.error('drawOverlay error:', e);
    }
}

function drawPartImage(ctx, partName, x, y, w, h) {
    if (!overlayImagesLoaded[partName]) {
        var img = new Image();
        img.src = '/static/images/parts/' + partName + '.png';
        overlayImagesLoaded[partName] = img;
    }
    var img = overlayImagesLoaded[partName];
    if (img && img.complete && img.naturalWidth > 0) {
        ctx.drawImage(img, x, y, w, h);
    }
}

// ===== Slot Interaction =====

function getSlotAtPosition(x, y) {
    console.log('[DIAG] getSlotAtPosition: x=', x, 'y=', y, 'currentBlueprintName=', currentBlueprintName);
    var slots = blueprintSlotBoxes[currentBlueprintName];
    if (!slots) {
        console.log('[DIAG] getSlotAtPosition: no slots found for current blueprint');
        return -1;
    }
    console.log('[DIAG] getSlotAtPosition: checking', slots.length, 'slots');
    for (var i = 0; i < slots.length; i++) {
        var s = slots[i];
        console.log('[DIAG] getSlotAtPosition: slot', i, '=', {x: s.x, y: s.y, w: s.w, h: s.h}, 'occupied:', s.occupied, 'invalid:', s.invalid);
        if (x >= s.x && x <= s.x + s.w && y >= s.y && y <= s.y + s.h) {
            console.log('[DIAG] getSlotAtPosition: MATCH found at slot', i);
            return i;
        }
    }
    console.log('[DIAG] getSlotAtPosition: no match found');
    return -1;
}

function placePart(slotIndex, partName) {
    console.log('[DIAG] placePart called: slotIndex=', slotIndex, 'partName=', partName);
    var slots = blueprintSlotBoxes[currentBlueprintName];
    if (!slots) {
        console.log('[DIAG] placePart: NO SLOTS for', currentBlueprintName);
        return;
    }
    if (!slots[slotIndex]) {
        console.log('[DIAG] placePart: slot', slotIndex, 'does not exist (total slots:', slots.length, ')');
        return;
    }

    // Check if slot is invalid for the selected part
    if (slots[slotIndex].invalid) {
        console.log('[DIAG] placePart: slot', slotIndex, 'is invalid - reason:', slots[slotIndex].invalidReason);
        showPlacementFeedback(slots[slotIndex].invalidReason);
        return;
    }

    // If placing the same part in an occupied slot, remove the existing part first
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

function removePart(slotIndex) {
    console.log('[DIAG] removePart called: slotIndex=', slotIndex);
    var slots = blueprintSlotBoxes[currentBlueprintName];
    if (!slots || !slots[slotIndex]) return;
    slots[slotIndex].occupied = false;
    slots[slotIndex].partName = null;
    drawOverlay();
    updateShipStats();
}

// ===== User Feedback =====

function showPlacementFeedback(message) {
    // Show a brief flash message near the canvas
    var feedbackEl = document.getElementById('placementFeedback');
    if (!feedbackEl) {
        feedbackEl = document.createElement('div');
        feedbackEl.id = 'placementFeedback';
        feedbackEl.style.cssText = 'position: absolute; top: 10px; left: 50%; transform: translateX(-50%); ' +
            'background-color: #d32f2f; color: white; padding: 8px 16px; border-radius: 4px; ' +
            'z-index: 100; font-size: 14px; font-weight: bold; pointer-events: none; ' +
            'opacity: 0; transition: opacity 0.3s ease-out;';
        var canvasContainer = document.getElementById('canvasContainer');
        if (canvasContainer) {
            canvasContainer.appendChild(feedbackEl);
        }
    }

    if (message) {
        feedbackEl.textContent = message;
    } else {
        feedbackEl.textContent = 'Cannot place part here: operation rejected by backend validation.';
    }

    feedbackEl.style.opacity = '1';

    // Fade out after 3 seconds
    setTimeout(function() {
        feedbackEl.style.opacity = '0';
    }, 3000);
}

// ===== Validation =====

function validatePartPlacement(partName) {
    if (!currentBlueprintName) {
        return;
    }

    var typeName = currentBlueprintName;
    var response = fetch('/api/validate_part_placement', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ship_type: typeName, part_name: partName})
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        var slots = blueprintSlotBoxes[currentBlueprintName];
        if (!slots) return;

        invalidSlotsForSelectedPart = new Set(data.invalid_slots || []);

        // Update slot invalid states using generic messages from backend
        for (var i = 0; i < slots.length; i++) {
            if (invalidSlotsForSelectedPart.has(i)) {
                slots[i].invalid = true;
                slots[i].invalidReason = data.invalid_reasons[i] || null;
            } else {
                slots[i].invalid = false;
                slots[i].invalidReason = null;
            }
        }

        drawOverlay();
    })
    .catch(function(err) {
        console.error('Failed to validate part placement:', err);
    });
}

// ===== Drag and Drop =====

function onDragStart(event, partName) {
    console.log('[DIAG] onDragStart: partName =', partName);
    event.dataTransfer.setData('text/plain', partName);
    event.dataTransfer.effectAllowed = 'copy';
    selectedPartName = partName;
    validatePartPlacement(partName);

    var img = event.target;
    img.style.opacity = '0.5';
    setTimeout(function() { img.style.opacity = '1'; }, 100);
}

// ===== UI Functions =====

function setupOverlayHandlers() {
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

    overlay.addEventListener('dragover', function(event) {
        console.log('[DIAG] dragover event fired on overlay');
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
    });

    overlay.addEventListener('drop', function(event) {
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
            var slots = blueprintSlotBoxes[currentBlueprintName];
            console.log('[DIAG] drop: slots for current blueprint =', slots ? slots.length : 'none', 'currentBlueprintName =', currentBlueprintName);
        }
    });

    overlay.addEventListener('click', function(event) {
        console.log('[DIAG] CLICK event fired on overlay', {
            clientX: event.clientX,
            clientY: event.clientY,
            selectedPartName: selectedPartName
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
            var slots = blueprintSlotBoxes[currentBlueprintName];
            console.log('[DIAG] click: slots[', slotIndex, '].occupied =', slots && slots[slotIndex] ? slots[slotIndex].occupied : 'N/A');
            if (selectedPartName) {
                // Check if the clicked slot is invalid for the selected part
                if (slots && slots[slotIndex] && slots[slotIndex].invalid) {
                    console.log('[DIAG] click: slot', slotIndex, 'is invalid - showing feedback');
                    showPlacementFeedback(slots[slotIndex].invalidReason);
                    return;
                }
                placePart(slotIndex, selectedPartName);
            } else if (slots && slots[slotIndex] && slots[slotIndex].occupied) {
                removePart(slotIndex);
            }
        }
    });

    overlay.addEventListener('contextmenu', function(event) {
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

    overlay.addEventListener('mousemove', function(event) {
        var rect = overlay.getBoundingClientRect();
        var scaleX = overlay.width / rect.width;
        var scaleY = overlay.height / rect.height;
        var x = (event.clientX - rect.left) * scaleX;
        var y = (event.clientY - rect.top) * scaleY;

        var newHoveredIndex = getSlotAtPosition(x, y);
        if (newHoveredIndex !== hoveredSlotIndex) {
            hoveredSlotIndex = newHoveredIndex;
            drawOverlay();
        }
    });

    overlay.addEventListener('mouseleave', function() {
        if (hoveredSlotIndex !== -1) {
            hoveredSlotIndex = -1;
            drawOverlay();
        }
    });

    console.log('[DIAG] setupOverlayHandlers: all event listeners attached to overlay');
    console.log('[DIAG] setupOverlayHandlers: overlay style.pointerEvents =', getComputedStyle(overlay).pointerEvents);
    console.log('[DIAG] setupOverlayHandlers: overlay computed position =', getComputedStyle(overlay).position);
}

function selectBlueprint(blueprintName) {
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

    // Find the existing blueprint image element from the dropdown
    // The dropdown images are already loaded by the browser
    var blueprintImages = document.querySelectorAll('.dropdown-content img[src*="blueprints/"]');
    var existingImg = null;
    for (var i = 0; i < blueprintImages.length; i++) {
        var src = blueprintImages[i].src;
        if (src && src.indexOf(blueprintName + '.png') !== -1) {
            existingImg = blueprintImages[i];
            console.log('Found existing blueprint image:', src);
            break;
        }
    }

    // Use the existing image if found, otherwise create a new one
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

            // Cap canvas width to container width to prevent horizontal overflow
            var containerWidth = document.getElementById('shipBlueprintDiv').clientWidth;
            var scale = 1;
            if (image.naturalWidth > containerWidth) {
                scale = containerWidth / image.naturalWidth;
            }
            var displayWidth = Math.floor(image.naturalWidth * scale);
            var displayHeight = Math.floor(image.naturalHeight * scale);

            // Explicitly set the display size to match the internal dimensions
            // This ensures the overlay canvas is properly sized and receives pointer events
            shipBlueprintCanvas.style.width = displayWidth + 'px';
            shipBlueprintCanvas.style.height = displayHeight + 'px';
            overlayCanvas.style.width = displayWidth + 'px';
            overlayCanvas.style.height = displayHeight + 'px';

            // Ensure canvas container is sized correctly
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

            currentBlueprintName = blueprintName;
            blueprintSlotBoxes[blueprintName] = [];
            loadGridSlots(shipBlueprintCanvas, ctx, blueprintName, function(slots) {
                drawOverlay();
                loadShipTypeInfo(blueprintName, function() {
                    console.log('Ship type info loaded for', blueprintName);
                    updateSlotLabels();
                    loadShipData(function() {
                        console.log('[DIAG] Ship data loaded successfully');
                        updateShipStats();
                    });
                });
                loadingDiv.style.display = "none";
                console.log('Blueprint displayed successfully');
            });
        } catch(e) {
            console.error('Error drawing blueprint:', e);
            loadingDiv.style.display = "none";
            loadingDiv.textContent = 'Error: ' + e.message;
            loadingDiv.style.display = "block";
        }
    }

    if (existingImg) {
        // Image already loaded in the DOM
        console.log('Using existing DOM image');
        if (existingImg.naturalWidth > 0) {
            handleImageLoad();
        } else {
            // Image element exists but hasn't finished decoding yet
            console.log('Existing image not decoded yet, waiting...');
            var waitCount = 0;
            var waitInterval = setInterval(function() {
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
        // Create a new image element
        var imageUrl = '/static/images/blueprints/' + blueprintName + '.png';
        var newImage = new Image();
        var loadTriggered = false;

        newImage.onerror = function() {
            console.error('Failed to load image:', imageUrl);
            if (!loadTriggered) {
                loadTriggered = true;
                loadingDiv.style.display = "none";
                loadingDiv.textContent = 'Failed to load blueprint image';
                loadingDiv.style.display = "block";
            }
        };

        newImage.onload = function() {
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

function showPrimaryDiv(divToShow) {
    var shipDesigner = document.getElementById("shipDesigner");
    var battleSimulator = document.getElementById("battleSimulator");
    switch(divToShow) {
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

function addPartToShip(partName) {
    console.log('[DIAG] addPartToShip called: partName =', partName);
    selectedPartName = partName;

    document.querySelectorAll('.part-image').forEach(function(img) {
        img.classList.remove('selected');
        if (img.src.indexOf(partName) !== -1) {
            img.classList.add('selected');
        }
    });

    // Validate placement for the selected part against all slots
    validatePartPlacement(partName);
}

// ===== Ship Statistics =====

var shipPartsData = {};
var shipTypesData = {};
var currentShipStats = null;
var currentShipTypeInfo = null;
var currentSlotMapping = {};

function loadShipData(callback) {
    fetch('/api/ship_parts')
        .then(function(response) { return response.json(); })
        .then(function(data) {
            shipPartsData = data;
            return fetch('/api/ship_types');
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            shipTypesData = data;
            if (callback) callback();
        })
        .catch(function(err) {
            console.error('Failed to load ship data:', err);
        });
}

function loadShipTypeInfo(blueprintName, callback) {
    fetch('/api/ship_types/' + blueprintName)
        .then(function(response) { return response.json(); })
        .then(function(data) {
            currentShipTypeInfo = data;
            return fetch('/api/ship_type_mapping/' + blueprintName);
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            currentSlotMapping = data.mapping || {};
            if (callback) callback();
        })
        .catch(function(err) {
            console.error('Failed to load ship type info for ' + blueprintName + ':', err);
            currentShipTypeInfo = null;
            currentSlotMapping = {};
        });
}

function calculateShipStats(blueprintName) {
    var typeName = blueprintName;
    var shipType = shipTypesData[typeName];
    if (!shipType) {
        currentShipStats = null;
        return null;
    }

    var slots = blueprintSlotBoxes[blueprintName];
    if (!slots) {
        currentShipStats = null;
        return null;
    }

    var totalShielding = 0;
    var totalEnergy = shipType.bonus_energy;
    var initiative = shipType.base_initiative;
    var armor = 0;
    var targeting = shipType.bonus_targeting;

    for (var i = 0; i < slots.length; i++) {
        var partName = slots[i].partName;
        if (!partName) continue;

        var partData = shipPartsData[partName];
        if (!partData) continue;

        if ('shielding' in partData) {
            totalShielding += partData.shielding;
        }
        if ('energy' in partData) {
            totalEnergy += partData.energy;
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
    var availableEnergy = totalEnergy;

    currentShipStats = {
        shielding: totalShielding,
        energy: totalEnergy,
        availableEnergy: availableEnergy,
        initiative: initiative,
        armor: armor,
        targeting: targeting,
        hp: hitPoints,
        maxHp: hitPoints
    };

    return currentShipStats;
}

function updateStatsDisplay() {
    var stats = currentShipStats;
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

function updateInstalledPartsList() {
    var listEl = document.getElementById('installedPartsList');
    if (!currentBlueprintName) {
        listEl.textContent = 'None';
        return;
    }

    var slots = blueprintSlotBoxes[currentBlueprintName];
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

function updateShipStats() {
    if (!currentBlueprintName) return;
    calculateShipStats(currentBlueprintName);
    updateStatsDisplay();
}

// ===== End Ship Statistics =====

// ===== Slot Label Display =====

function updateSlotLabels() {
    if (!currentBlueprintName || !currentShipTypeInfo) return;

    var slots = blueprintSlotBoxes[currentBlueprintName];
    if (!slots) return;

    var partTypes = currentShipTypeInfo.part_types || [];
    var slotLabels = currentShipTypeInfo.slot_labels || [];

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

function drawSlotLabelText(ctx, slot, index) {
    if (!slot.partType) return;

    var label = slot.partType.charAt(0).toUpperCase() + slot.partType.slice(1);
    ctx.font = 'bold ' + Math.max(8, slot.w / 6) + 'px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';

    // Draw label with dark outline for readability
    var textX = slot.x + slot.w / 2;
    var textY = slot.y + slot.h - 4;
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.lineWidth = 2;
    ctx.strokeText(label, textX, textY);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
    ctx.fillText(label, textX, textY);
}

// ===== End Slot Label Display =====

// Initialize overlay handlers when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('[DIAG] DOMContentLoaded: initializing overlay handlers');
    setupOverlayHandlers();
    setupDropdownHandlers();
});

function openDropdown(dropdown) {
    closeAllDropdowns();
    dropdown.classList.add('open');

    var content = dropdown.querySelector('.dropdown-content');
    if (!content) return;

    var btn = dropdown.querySelector('.dropbtn');
    if (!btn) return;

    var portal = document.getElementById('dropdown-portal');
    if (!portal) return;

    var btnRect = btn.getBoundingClientRect();

    content.style.display = 'block';
    content.style.position = 'fixed';
    content.style.left = btnRect.left + 'px';
    content.style.top = (btnRect.top + btnRect.height) + 'px';
    content.style.transform = 'none';

    portal.appendChild(content);

    requestAnimationFrame(function() {
        var contentRect = content.getBoundingClientRect();
        var viewportHeight = window.innerHeight;

        if (contentRect.bottom > viewportHeight) {
            content.style.top = (btnRect.top - contentRect.height) + 'px';
        }
    });

    content._originalParent = btn.parentElement;
    content._parentDropdown = dropdown;
}

function closeDropdown(dropdown) {
    dropdown.classList.remove('open');

    var portal = document.getElementById('dropdown-portal');
    if (!portal) return;

    var content = portal.querySelector('.dropdown-content');
    if (!content) return;

    if (content._originalParent) {
        content.style.display = 'none';
        content.style.position = '';
        content.style.left = '';
        content.style.top = '';
        content.style.transform = '';
        content._parentDropdown = null;
        content._originalParent.appendChild(content);
    } else {
        if (content.parentNode === portal) {
            portal.removeChild(content);
        }
    }
}

function setupDropdownHandlers() {
    var dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(function(dropdown) {
        var btn = dropdown.querySelector('.dropbtn');
        if (btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                var isOpen = dropdown.classList.contains('open');
                if (!isOpen) {
                    openDropdown(dropdown);
                } else {
                    closeDropdown(dropdown);
                }
            });
        }
    });

    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            closeAllDropdowns();
        }
    });

    var blueprintDropdown = document.querySelector('#shipDesigner .dropdown');
    if (blueprintDropdown) {
        blueprintDropdown.addEventListener('mouseenter', function() {
            var overlay = document.getElementById('overlayCanvas');
            if (overlay) {
                overlay.style.pointerEvents = 'none';
            }
        });
        blueprintDropdown.addEventListener('mouseleave', function() {
            var overlay = document.getElementById('overlayCanvas');
            if (overlay) {
                overlay.style.pointerEvents = 'auto';
            }
        });
    }

    window.addEventListener('scroll', function() {
        var portal = document.getElementById('dropdown-portal');
        if (!portal) return;
        var content = portal.querySelector('.dropdown-content');
        if (!content) return;
        var dropdown = content._parentDropdown;
        if (!dropdown || !dropdown.classList.contains('open')) return;
        repositionDropdownContent(dropdown);
    }, true);

    var resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            var portal = document.getElementById('dropdown-portal');
            if (!portal) return;
            var content = portal.querySelector('.dropdown-content');
            if (!content) return;
            var dropdown = content._parentDropdown;
            if (!dropdown || !dropdown.classList.contains('open')) return;
            repositionDropdownContent(dropdown);
        }, 100);
    });
}

function repositionDropdownContent(dropdown) {
    var content = dropdown.querySelector('.dropdown-content');
    if (!content) return;

    var portal = document.getElementById('dropdown-portal');
    if (!portal || content.parentNode !== portal) return;

    var btn = dropdown.querySelector('.dropbtn');
    if (!btn) return;

    content.style.display = 'block';

    var btnRect = btn.getBoundingClientRect();

    content.style.left = btnRect.left + 'px';
    content.style.top = (btnRect.top + btnRect.height) + 'px';

    requestAnimationFrame(function() {
        var contentRect = content.getBoundingClientRect();
        var viewportHeight = window.innerHeight;

        if (contentRect.bottom > viewportHeight) {
            content.style.top = (btnRect.top - contentRect.height) + 'px';
        }
    });
}

function closeAllDropdowns() {
    document.querySelectorAll('.dropdown.open').forEach(function(d) {
        closeDropdown(d);
    });
}
