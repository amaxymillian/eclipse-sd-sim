// Dropdown open/close/reposition logic.
// No dependencies on other modules -- only DOM manipulation.

export function openDropdown(dropdown) {
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

    if (!content.classList.contains('blueprint-dropdown')) {
        requestAnimationFrame(function () {
            var contentRect = content.getBoundingClientRect();
            var viewportHeight = window.innerHeight;

            if (contentRect.bottom > viewportHeight) {
                content.style.top = (btnRect.top - contentRect.height) + 'px';
            }
        });
    }

    content._originalParent = btn.parentElement;
    content._parentDropdown = dropdown;
}

export function closeDropdown(dropdown) {
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

export function closeAllDropdowns() {
    document.querySelectorAll('.dropdown.open').forEach(function (d) {
        closeDropdown(d);
    });
}

export function repositionDropdownContent(dropdown) {
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

    if (!content.classList.contains('blueprint-dropdown')) {
        requestAnimationFrame(function () {
            var contentRect = content.getBoundingClientRect();
            var viewportHeight = window.innerHeight;

            if (contentRect.bottom > viewportHeight) {
                content.style.top = (btnRect.top - contentRect.height) + 'px';
            }
        });
    }
}

export function setupDropdownHandlers() {
    var dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(function (dropdown) {
        var btn = dropdown.querySelector('.dropbtn');
        if (btn) {
            btn.addEventListener('click', function (e) {
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

    document.addEventListener('click', function (e) {
        if (!e.target.closest('.dropdown')) {
            closeAllDropdowns();
        }
    });

    var blueprintDropdown = document.querySelector('#shipDesigner .dropdown');
    if (blueprintDropdown) {
        blueprintDropdown.addEventListener('mouseenter', function () {
            var overlay = document.getElementById('overlayCanvas');
            if (overlay) {
                overlay.style.pointerEvents = 'none';
            }
        });
        blueprintDropdown.addEventListener('mouseleave', function () {
            var overlay = document.getElementById('overlayCanvas');
            if (overlay) {
                overlay.style.pointerEvents = 'auto';
            }
        });
    }

    window.addEventListener('scroll', function () {
        var portal = document.getElementById('dropdown-portal');
        if (!portal) return;
        var content = portal.querySelector('.dropdown-content');
        if (!content) return;
        var dropdown = content._parentDropdown;
        if (!dropdown || !dropdown.classList.contains('open')) return;
        repositionDropdownContent(dropdown);
    }, true);

    var resizeTimeout;
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function () {
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
