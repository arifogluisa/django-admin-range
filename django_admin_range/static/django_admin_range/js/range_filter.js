function toggleRangeFilterDropdown(fieldName) {
    const dropdown = document.getElementById('dropdown_' + fieldName);
    const allDropdowns = document.querySelectorAll('.range-filter-dropdown');

    allDropdowns.forEach(function (d) {
        if (d.id !== 'dropdown_' + fieldName) {
            d.classList.remove('open');
        }
    });

    if (dropdown) {
        dropdown.classList.toggle('open');
    }
}

function clearRangeFilter(fieldName) {
    const from = document.getElementById('field_gte_' + fieldName);
    const to = document.getElementById('field_lte_' + fieldName);
    if (from) from.value = '';
    if (to) to.value = '';

    [from, to].forEach(function (input) {
        if (!input) return;
        const hid = input.dataset.hiddenId && document.getElementById(input.dataset.hiddenId);
        if (hid) {
            hid.value = '';
            hid.disabled = true;
            // Remove disabled hidden input from form to prevent it from being submitted
            if (hid.parentNode) {
                hid.parentNode.removeChild(hid);
            }
        }
        // Trigger sync manually since we're clearing programmatically
        const event = new Event('change', { bubbles: true });
        input.dispatchEvent(event);
    });
}

document.addEventListener('click', function (e) {
    if (!e.target.closest('.range-filter-wrapper')) {
        document.querySelectorAll('.range-filter-dropdown').forEach(function (d) {
            d.classList.remove('open');
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const inputs = document.querySelectorAll('.range-filter-dropdown input');

    const normalize = function (val, inputType) {
        if (!val) return '';

        if (inputType === 'date') {
            const parts = val.split('.');
            if (parts.length === 3) {
                // DD.MM.YYYY -> YYYY-MM-DD
                return `${parts[2]}-${parts[1]}-${parts[0]}`;
            }
            return val;
        } else if (inputType === 'datetime-local') {
            const cleaned = val.trim().replace(' ', 'T');
            const match = cleaned.match(/^(\d{4}-\d{2}-\d{2})[T ]?(\d{2}:\d{2})(?::\d{2})?/);
            if (match) {
                return `${match[1]}T${match[2]}`;
            }
            return cleaned;
        } else if (inputType === 'number') {
            // No normalization needed for numbers
            return val;
        }

        return val;
    };

    inputs.forEach(function (input) {
        const val = input.dataset.value || input.value;
        if (val) {
            input.value = normalize(val, input.type);
        }
    });

    const searchForm =
        document.getElementById('changelist-search') ||
        document.querySelector('#changelist-form') ||
        document.querySelector('form[action][method="get"]');

    if (!searchForm) return;

    searchForm.action = window.location.pathname;

    const hiddenMap = new Map();

    inputs.forEach(function (input, idx) {
        // Extract field name from input ID (format: field_gte_fieldname or field_lte_fieldname)
        const idParts = input.id.split('_');
        if (idParts.length < 3 || idParts[0] !== 'field') return;

        const direction = idParts[1]; // 'gte' or 'lte'
        const fieldName = idParts.slice(2).join('_'); // field name
        const name = `${fieldName}__${direction}`;

        searchForm.querySelectorAll(`input[type="hidden"][name="${name}"]`).forEach(function (h) {
            if (!hiddenMap.has(h)) h.parentNode.removeChild(h);
        });

        const hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = name;
        hidden.value = input.value || '';
        hidden.id = `hidden_${idx}_${name}`;

        input.dataset.hiddenId = hidden.id;

        searchForm.appendChild(hidden);
        hiddenMap.set(input, hidden);

        const sync = () => {
            const v = (input.value || '').trim();
            if (v) {
                hidden.value = v;
                hidden.disabled = false;
                if (!hidden.parentNode) {
                    searchForm.appendChild(hidden);
                }
                hiddenMap.set(input, hidden);
            } else {
                hidden.value = '';
                hidden.disabled = true;
                if (hidden.parentNode === searchForm) searchForm.removeChild(hidden);
                hiddenMap.delete(input);
            }
        };

        input.addEventListener('change', sync);
        input.addEventListener('input', sync);
        sync();
    });
});
