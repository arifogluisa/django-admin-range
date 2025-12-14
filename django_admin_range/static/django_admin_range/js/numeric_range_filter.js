function toggleNumericDropdown(fieldName) {
    const dropdown = document.getElementById('num_dropdown_' + fieldName);
    const allDropdowns = document.querySelectorAll('.numeric-range-dropdown');

    allDropdowns.forEach(function (d) {
        if (d.id !== 'num_dropdown_' + fieldName) {
            d.classList.remove('open');
        }
    });

    if (dropdown) dropdown.classList.toggle('open');
}

function clearNumericFilter(fieldName) {
    const from = document.getElementById('num_gte_' + fieldName);
    const to = document.getElementById('num_lte_' + fieldName);
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
    if (!e.target.closest('.numeric-range-wrapper')) {
        document.querySelectorAll('.numeric-range-dropdown').forEach(function (d) {
            d.classList.remove('open');
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const numInputs = document.querySelectorAll('.numeric-range-dropdown input[type="number"]');

    const searchForm =
        document.getElementById('changelist-search') ||
        document.querySelector('#changelist-form') ||
        document.querySelector('form[action][method="get"]');

    if (!searchForm) return;

    searchForm.action = window.location.pathname;

    const hiddenMap = new Map();

    numInputs.forEach(function (input, idx) {
        const name = input.getAttribute('name');
        if (!name) return;

        searchForm.querySelectorAll(`input[type="hidden"][name="${name}"]`).forEach(function (h) {
            if (!hiddenMap.has(h)) h.parentNode.removeChild(h);
        });

        const hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = name;
        hidden.value = input.value || '';
        hidden.id = `hidden_num_${idx}_${name}`;

        input.removeAttribute('name');
        input.dataset.hiddenId = hidden.id;

        searchForm.appendChild(hidden);
        hiddenMap.set(input, hidden);

        const sync = () => {
            const v = (input.value || '').trim();
            if (v !== '') {
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
