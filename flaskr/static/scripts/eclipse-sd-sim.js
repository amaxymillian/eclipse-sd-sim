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

// Ship types enum (unused but kept for reference)
const ShipType = {
    TERRAN_INTERCEPTOR: "Terran_Interceptor",
    TERRAN_CRUISER: "Terran_Cruiser",
    TERRAN_DREADNOUGHT: "Terran_Dreadnought",
    TERRAN_STARBASE: "Terran_Starbase",
    ERIDANI_INTERCEPTOR: "Eridani_Interceptor",
    ERIDANI_CRUISER: "Eridani_Cruiser",
    ERIDANI_DREADNOUGHT: "Eridani_Dreadnought",
    ERIDANI_STARBASE: "Eridani_Starbase",
    ORION_INTERCEPTOR: "Orion_Interceptor",
    ORION_CRUISER: "Orion_Cruiser",
    ORION_DREADNOUGHT: "Orion_Dreadnought",
    ORION_STARBASE: "Orion_Starbase",
    PLANTA_INTERCEPTOR: "Planta_Interceptor",
    PLANTA_CRUISER: "Planta_Cruiser",
    PLANTA_DREADNOUGHT: "Planta_Dreadnought",
    PLANTA_STARBASE: "Planta_Starbase"
};

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

function detectBlueprintSlots(canvas, ctx, blueprintName) {
    console.log('detectBlueprintSlots starting for:', blueprintName, 'canvas:', canvas.width, 'x', canvas.height);
    try {
        var imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    } catch(e) {
        console.error('getImageData failed:', e);
        blueprintSlotBoxes[blueprintName] = [];
        return [];
    }
    var data = imageData.data;
    var width = canvas.width;
    var height = canvas.height;
    var minDim = Math.min(width, height);
    var minRunLen = Math.max(10, minDim * 0.03);
    var minSlotW = Math.max(15, minDim * 0.05);
    var minSlotH = Math.max(15, minDim * 0.05);
    var maxSlotW = width * 0.5;
    var maxSlotH = height * 0.5;

    // Step 1: Find all horizontal white pixel runs per row
    var hRuns = [];
    for (var row = 0; row < height; row++) {
        var runStart = -1;
        for (var col = 0; col < width; col++) {
            var idx = (row * width + col) * 4;
            var isWhite = data[idx] > WHITE_THRESHOLD &&
                          data[idx+1] > WHITE_THRESHOLD &&
                          data[idx+2] > WHITE_THRESHOLD;
            if (isWhite && runStart === -1) {
                runStart = col;
            } else if (!isWhite && runStart !== -1) {
                if (col - runStart >= minRunLen) {
                    hRuns.push({row: row, startX: runStart, endX: col - 1});
                }
                runStart = -1;
            }
        }
        if (runStart !== -1 && width - runStart >= minRunLen) {
            hRuns.push({row: row, startX: runStart, endX: width - 1});
        }
    }

    // Step 2: Group horizontal runs into line segments (adjacent rows with overlapping x-range)
    var hLines = [];
    var used = new Array(hRuns.length).fill(false);
    for (var i = 0; i < hRuns.length; i++) {
        if (used[i]) continue;
        var line = {topRow: hRuns[i].row, bottomRow: hRuns[i].row,
                    leftX: hRuns[i].startX, rightX: hRuns[i].endX};
        used[i] = true;
        for (var j = i + 1; j < hRuns.length; j++) {
            if (used[j]) continue;
            if (Math.abs(hRuns[j].row - line.bottomRow) <= 2) {
                var overlap = Math.min(line.rightX, hRuns[j].endX) - Math.max(line.leftX, hRuns[j].startX);
                if (overlap >= minRunLen * 0.5) {
                    line.leftX = Math.min(line.leftX, hRuns[j].startX);
                    line.rightX = Math.max(line.rightX, hRuns[j].endX);
                    line.bottomRow = hRuns[j].row;
                    used[j] = true;
                }
            }
        }
        hLines.push(line);
    }

    // Step 3: Find rectangles by pairing horizontal lines with matching edges
    var slots = [];
    for (var i = 0; i < hLines.length; i++) {
        for (var j = i + 1; j < hLines.length; j++) {
            var top = hLines[i], bottom = hLines[j];
            if (bottom.topRow - top.bottomRow < minSlotH * 0.5) continue;

            var leftX = Math.max(top.leftX, bottom.leftX);
            var rightX = Math.min(top.rightX, bottom.rightX);
            var slotW = rightX - leftX;
            var slotH = bottom.bottomRow - top.topRow;

            if (slotW < minSlotW || slotW > maxSlotW) continue;
            if (slotH < minSlotH || slotH > maxSlotH) continue;

            // Check if top and bottom edges have enough white pixels
            var topEdgeOK = verifyHorizontalEdge(data, width, top.topRow, leftX, rightX, WHITE_THRESHOLD);
            var bottomEdgeOK = verifyHorizontalEdge(data, width, bottom.bottomRow, leftX, rightX, WHITE_THRESHOLD);
            if (!topEdgeOK || !bottomEdgeOK) continue;

            // Verify left and right edges have white pixels connecting top and bottom
            var leftEdgeOK = verifyVerticalEdge(data, width, leftX, top.topRow, bottom.bottomRow, WHITE_THRESHOLD);
            var rightEdgeOK = verifyVerticalEdge(data, width, rightX, top.topRow, bottom.bottomRow, WHITE_THRESHOLD);
            if (!leftEdgeOK || !rightEdgeOK) continue;

            slots.push({x: leftX, y: top.topRow, w: slotW, h: slotH, occupied: false, partName: null});
        }
    }

    // Deduplicate overlapping detections
    slots = deduplicateSlots(slots);

    // Filter: keep slots in reasonable positions (skip the very top where the ship name/header might be)
    var filteredSlots = [];
    for (var k = 0; k < slots.length; k++) {
        if (slots[k].y > height * 0.08) {
            filteredSlots.push(slots[k]);
        }
    }

    // If too many slots detected, keep only the largest ones
    if (filteredSlots.length > 12) {
        filteredSlots.sort(function(a, b) { return (b.w * b.h) - (a.w * a.h); });
        filteredSlots = filteredSlots.slice(0, 10);
    }

    blueprintSlotBoxes[blueprintName] = filteredSlots;
    console.log('detectBlueprintSlots found', filteredSlots.length, 'slots for', blueprintName);
    return filteredSlots;
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

        if (s.occupied) {
            ctx.fillStyle = 'rgba(55, 123, 168, 0.12)';
            ctx.fillRect(s.x, s.y, s.w, s.h);
        }

        if (s.occupied) {
            ctx.strokeStyle = '#2e7d32';
            ctx.lineWidth = 3;
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
    var slots = blueprintSlotBoxes[currentBlueprintName];
    if (!slots) return -1;
    for (var i = 0; i < slots.length; i++) {
        var s = slots[i];
        if (x >= s.x && x <= s.x + s.w && y >= s.y && y <= s.y + s.h) {
            return i;
        }
    }
    return -1;
}

function placePart(slotIndex, partName) {
    var slots = blueprintSlotBoxes[currentBlueprintName];
    if (!slots || !slots[slotIndex]) return;
    slots[slotIndex].occupied = true;
    slots[slotIndex].partName = partName;
    drawOverlay();
}

function removePart(slotIndex) {
    var slots = blueprintSlotBoxes[currentBlueprintName];
    if (!slots || !slots[slotIndex]) return;
    slots[slotIndex].occupied = false;
    slots[slotIndex].partName = null;
    drawOverlay();
}

// ===== Drag and Drop =====

function onDragStart(event, partName) {
    event.dataTransfer.setData('text/plain', partName);
    event.dataTransfer.effectAllowed = 'copy';
    selectedPartName = partName;

    var img = event.target;
    img.style.opacity = '0.5';
    setTimeout(function() { img.style.opacity = '1'; }, 100);
}

// ===== UI Functions =====

function setupOverlayHandlers() {
    var overlay = document.getElementById('overlayCanvas');
    if (!overlay) return;

    overlay.addEventListener('dragover', function(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
    });

    overlay.addEventListener('drop', function(event) {
        event.preventDefault();
        var rect = overlay.getBoundingClientRect();
        var scaleX = overlay.width / rect.width;
        var scaleY = overlay.height / rect.height;
        var x = (event.clientX - rect.left) * scaleX;
        var y = (event.clientY - rect.top) * scaleY;

        var partName = event.dataTransfer.getData('text/plain');
        var slotIndex = getSlotAtPosition(x, y);
        if (slotIndex >= 0 && partName) {
            placePart(slotIndex, partName);
        }
    });

    overlay.addEventListener('click', function(event) {
        var rect = overlay.getBoundingClientRect();
        var scaleX = overlay.width / rect.width;
        var scaleY = overlay.height / rect.height;
        var x = (event.clientX - rect.left) * scaleX;
        var y = (event.clientY - rect.top) * scaleY;

        var slotIndex = getSlotAtPosition(x, y);
        if (slotIndex >= 0) {
            var slots = blueprintSlotBoxes[currentBlueprintName];
            if (selectedPartName) {
                placePart(slotIndex, selectedPartName);
            } else if (slots[slotIndex].occupied) {
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

            var ctx = shipBlueprintCanvas.getContext('2d');
            ctx.clearRect(0, 0, shipBlueprintCanvas.width, shipBlueprintCanvas.height);
            ctx.drawImage(image, 0, 0);

            currentBlueprintName = blueprintName;
            detectBlueprintSlots(shipBlueprintCanvas, ctx, blueprintName);

            drawOverlay();

            loadingDiv.style.display = "none";
            console.log('Blueprint displayed successfully');
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
    selectedPartName = partName;

    document.querySelectorAll('.part-image').forEach(function(img) {
        img.classList.remove('selected');
        if (img.src.indexOf(partName) !== -1) {
            img.classList.add('selected');
        }
    });
}

// Initialize overlay handlers when the page loads
document.addEventListener('DOMContentLoaded', function() {
    setupOverlayHandlers();
});

