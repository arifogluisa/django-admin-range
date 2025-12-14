function toggleDateDropdown(fieldName) {
    const dropdown = document.getElementById('dropdown_' + fieldName);
    const allDropdowns = document.querySelectorAll('.date-range-dropdown');
    
    allDropdowns.forEach(function(d) {
        if (d.id !== 'dropdown_' + fieldName) {
            d.classList.remove('open');
        }
    });
    
    dropdown.classList.toggle('open');
}

function clearDateFilter(fieldName) {
    const from = document.getElementById('date_gte_' + fieldName);
    const to = document.getElementById('date_lte_' + fieldName);
    if (from) from.value = '';
    if (to) to.value = '';

    [from, to].forEach(function(input) {
        if (!input) return;
        const hid = input.dataset.hiddenId && document.getElementById(input.dataset.hiddenId);
        if (hid) {
            hid.value = '';
            hid.disabled = true;
        }
    });
}

document.addEventListener('click', function(e) {
    if (!e.target.closest('.date-range-wrapper')) {
        document.querySelectorAll('.date-range-dropdown').forEach(function(d) {
            d.classList.remove('open');
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('.date-range-dropdown input[type="date"]');

    const normalize = function(val) {
        if (!val) return '';
        const parts = val.split('.');
        if (parts.length === 3) {
            // DD.MM.YYYY -> YYYY-MM-DD
            return `${parts[2]}-${parts[1]}-${parts[0]}`;
        }
        return val;
    };

    dateInputs.forEach(function(input) {
        const val = input.dataset.value;
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

    dateInputs.forEach(function(input, idx) {
        const name = input.getAttribute('name');
        if (!name) return;

        searchForm.querySelectorAll(`input[type="hidden"][name="${name}"]`).forEach(function(h) {
            if (!hiddenMap.has(h)) h.parentNode.removeChild(h);
        });

        const hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = name;
        hidden.value = input.value || '';
        hidden.id = `hidden_date_${idx}_${name}`;

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
