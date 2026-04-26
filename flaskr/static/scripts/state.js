// Central state object for the Eclipse SD Sim frontend application.
// All modules import from here instead of using global variables.

export const AppState = {
    blueprintSlotBoxes: {},
    selectedPartName: null,
    hoveredSlotIndex: -1,
    overlayImagesLoaded: {},
    currentBlueprintName: null,
    invalidSlotsForSelectedPart: new Set(),
    lastValidationFeedback: null,
    shipPartsData: {},
    shipTypesData: {},
    currentShipStats: null,
    currentShipTypeInfo: null,
    currentSlotMapping: {},
};

export const WHITE_THRESHOLD = 150;
export const SAVED_SHIPS_KEY = 'eclipse-sd-sim-ships';

AppState.battle = {
    fleetA: {},
    fleetB: {},
    simCount: 5000,
    results: null,
};
