function toggleDatetimeDropdown(fieldName) {
    const dropdown = document.getElementById('dt_dropdown_' + fieldName);
    const allDropdowns = document.querySelectorAll('.datetime-range-dropdown');

    allDropdowns.forEach(function (d) {
        if (d.id !== 'dt_dropdown_' + fieldName) {
            d.classList.remove('open');
        }
    });

    if (dropdown) {
        dropdown.classList.toggle('open');
    }
}

function clearDatetimeFilter(fieldName) {
    const from = document.getElementById('datetime_gte_' + fieldName);
    const to = document.getElementById('datetime_lte_' + fieldName);
    if (from) from.value = '';
    if (to) to.value = '';

    [from, to].forEach(function (input) {
        if (!input) return;
        const hid = input.dataset.hiddenId && document.getElementById(input.dataset.hiddenId);
        if (hid) {
            hid.value = '';
            hid.disabled = true;
        }
    });
}

document.addEventListener('click', function (e) {
    if (!e.target.closest('.datetime-range-wrapper')) {
        document.querySelectorAll('.datetime-range-dropdown').forEach(function (d) {
            d.classList.remove('open');
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const dtInputs = document.querySelectorAll('.datetime-range-dropdown input[type="datetime-local"]');

    const normalize = function (val) {
        if (!val) return '';
        const cleaned = val.trim().replace(' ', 'T');
        const match = cleaned.match(/^(\d{4}-\d{2}-\d{2})[T ]?(\d{2}:\d{2})(?::\d{2})?/);
        if (match) {
            return `${match[1]}T${match[2]}`;
        }
        return cleaned;
    };

    dtInputs.forEach(function (input) {
        const val = input.dataset.value || input.value;
        if (val) {
            input.value = normalize(val);
        }
    });

    const searchForm =
        document.getElementById('changelist-search') ||
        document.querySelector('#changelist-form') ||
        document.querySelector('form[action][method="get"]');

    if (!searchForm) return;

    searchForm.action = window.location.pathname;

    const hiddenMap = new Map();

    dtInputs.forEach(function (input, idx) {
        const name = input.getAttribute('name');
        if (!name) return;

        searchForm.querySelectorAll(`input[type="hidden"][name="${name}"]`).forEach(function (h) {
            if (!hiddenMap.has(h)) h.parentNode.removeChild(h);
        });

        const hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = name;
        hidden.value = input.value || '';
        hidden.id = `hidden_dt_${idx}_${name}`;

        input.removeAttribute('name');
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


