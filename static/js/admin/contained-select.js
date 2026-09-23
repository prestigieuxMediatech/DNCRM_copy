document.addEventListener("DOMContentLoaded", () => {
  const targets = [
    ...document.querySelectorAll(".mycrm-dept-select"),
    ...document.querySelectorAll(".select-wrap select"),
    ...document.querySelectorAll(".status-select-wrap select"),
    ...document.querySelectorAll("[data-mycrm-form] select"),
    ...document.querySelectorAll(".mycrm-modal-card select"),
  ];

  targets.forEach((select) => {
    if (select.dataset.containedPicker === "true") return;
    select.dataset.containedPicker = "true";

    const container = select.parentElement;
    const picker = document.createElement("div");
    picker.className = "mycrm-contained-select";
    picker.innerHTML = '<button type="button" class="mycrm-contained-select-trigger" aria-haspopup="listbox" aria-expanded="false"></button><div class="mycrm-contained-select-menu" role="listbox"></div>';
    container.appendChild(picker);
    select.classList.add("mycrm-contained-select-native");

    const trigger = picker.querySelector(".mycrm-contained-select-trigger");
    const menu = picker.querySelector(".mycrm-contained-select-menu");
    const placeMenu = () => {
      const rect = trigger.getBoundingClientRect();
      const limit = Math.min(220, window.innerHeight * 0.35);
      const desired = Math.min(limit, Math.max(36, menu.children.length * 38));
      const below = window.innerHeight - rect.bottom - 8;
      const above = rect.top - 8;
      const openBelow = below >= desired || below >= above;
      const available = Math.max(72, Math.min(limit, openBelow ? below : above));
      menu.style.left = `${Math.max(8, Math.min(rect.left, window.innerWidth - Math.min(rect.width, window.innerWidth - 16) - 8))}px`;
      menu.style.width = `${Math.min(rect.width, window.innerWidth - 16)}px`;
      menu.style.maxHeight = `${available}px`;
      menu.style.top = openBelow
        ? `${Math.min(rect.bottom + 4, window.innerHeight - available - 8)}px`
        : `${Math.max(8, rect.top - available - 4)}px`;
    };
    const refresh = () => {
      trigger.textContent = select.selectedOptions[0]?.textContent.trim() || "Select";
      menu.querySelectorAll("[role=option]").forEach((option) => {
        option.setAttribute("aria-selected", String(option.dataset.value === select.value));
      });
    };

    Array.from(select.options).forEach((sourceOption) => {
      const option = document.createElement("button");
      option.type = "button";
      option.className = "mycrm-contained-select-option";
      option.setAttribute("role", "option");
      option.dataset.value = sourceOption.value;
      option.textContent = sourceOption.textContent.trim();
      option.addEventListener("click", () => {
        select.value = sourceOption.value;
        select.dispatchEvent(new Event("change", { bubbles: true }));
        picker.classList.remove("is-open");
        trigger.setAttribute("aria-expanded", "false");
        refresh();
      });
      menu.appendChild(option);
    });

    trigger.addEventListener("click", () => {
      const open = picker.classList.toggle("is-open");
      trigger.setAttribute("aria-expanded", String(open));
      if (open) placeMenu();
    });
    select.addEventListener("change", refresh);
    select.form?.addEventListener("reset", () => window.setTimeout(refresh));
    document.addEventListener("click", (event) => {
      if (!picker.contains(event.target)) {
        picker.classList.remove("is-open");
        trigger.setAttribute("aria-expanded", "false");
      }
    });
    picker.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        picker.classList.remove("is-open");
        trigger.setAttribute("aria-expanded", "false");
        trigger.focus();
      }
    });
    refresh();
  });
});
