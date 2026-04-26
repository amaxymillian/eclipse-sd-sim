// Toast feedback messages for user actions.

export function showPlacementFeedback(message) {
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

    setTimeout(function () {
        feedbackEl.style.opacity = '0';
    }, 3000);
}
