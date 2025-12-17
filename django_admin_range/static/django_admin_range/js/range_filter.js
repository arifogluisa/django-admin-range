function toggleRangeFilterDropdown(fieldName) {
  const dropdown = document.getElementById("dropdown_" + fieldName);
  const allDropdowns = document.querySelectorAll(".range-filter-dropdown");

  allDropdowns.forEach(function (d) {
    if (d.id !== "dropdown_" + fieldName) {
      d.classList.remove("open");
    }
  });

  if (dropdown) {
    dropdown.classList.toggle("open");
  }
}

function clearRangeFilter(fieldName) {
  const from = document.getElementById("field_gte_" + fieldName);
  const to = document.getElementById("field_lte_" + fieldName);
  if (from) from.value = "";
  if (to) to.value = "";
}

function submitRangeFilter(btn) {
  const fieldName = btn.dataset.fieldName;
  if (!fieldName) return;

  const wrapper = document.getElementById("wrapper_" + fieldName);
  if (!wrapper) return;

  const fromInput = wrapper.querySelector("#field_gte_" + fieldName);
  const toInput = wrapper.querySelector("#field_lte_" + fieldName);

  const url = new URL(window.location.href);

  const gteKey = fieldName + "__gte";
  const lteKey = fieldName + "__lte";

  // Clean previous params for this field
  url.searchParams.delete(gteKey);
  url.searchParams.delete(lteKey);

  if (fromInput && fromInput.value) {
    url.searchParams.set(gteKey, fromInput.value);
  }
  if (toInput && toInput.value) {
    url.searchParams.set(lteKey, toInput.value);
  }

  window.location.href = url.toString();
}

const normalize = function (val, inputType) {
  if (!val) return "";

  if (inputType === "date") {
    const parts = val.split(".");
    if (parts.length === 3) {
      // DD.MM.YYYY -> YYYY-MM-DD
      return `${parts[2]}-${parts[1]}-${parts[0]}`;
    }
    return val;
  } else if (inputType === "datetime-local") {
    const cleaned = val.trim().replace(" ", "T");
    const match = cleaned.match(
      /^(\d{4}-\d{2}-\d{2})[T ]?(\d{2}:\d{2})(?::\d{2})?/
    );
    if (match) {
      return `${match[1]}T${match[2]}`;
    }
    return cleaned;
  } else if (inputType === "number") {
    // No normalization needed for numbers
    return val;
  }

  return val;
};

document.addEventListener("click", function (e) {
  if (!e.target.closest(".range-filter-wrapper")) {
    document.querySelectorAll(".range-filter-dropdown").forEach(function (d) {
      d.classList.remove("open");
    });
  }
});

function initRangeFilter() {
  // Avoid running twice if the script is loaded multiple times or re-initialised.
  if (window.__djangoAdminRangeInitialized) return;
  window.__djangoAdminRangeInitialized = true;

  const inputs = document.querySelectorAll(".range-filter-dropdown input");

  inputs.forEach(function (input) {
    const val = input.dataset.value || input.value;
    if (val) {
      input.value = normalize(val, input.type);
    }
  });

  const submitButtons = document.querySelectorAll(
    ".range-filter-btn[data-field-name]"
  );

  submitButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      submitRangeFilter(btn);
    });
  });
}

// Support both normal script loading and late/dynamic injection.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initRangeFilter);
} else {
  initRangeFilter();
}
