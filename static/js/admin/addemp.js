(function () {
  const form = document.getElementById("empForm");
  if (!form) return;

  const profileInput = document.getElementById("profileImageInput");
  const fileNameDisplay = document.getElementById("fileNameDisplay");
  const avatarPreview = document.getElementById("avatarPreview");

  if (profileInput) {
    profileInput.addEventListener("change", function () {
      const file = this.files && this.files[0];
      if (!file) return;

      if (fileNameDisplay) fileNameDisplay.textContent = file.name;

      const reader = new FileReader();
      reader.onload = (event) => {
        if (avatarPreview) {
          avatarPreview.innerHTML = `<img src="${event.target.result}" alt="Preview" />`;
        }
      };
      reader.readAsDataURL(file);
    });
  }

  const statusSelect = document.getElementById("statusSelect");
  const statusDot = document.getElementById("statusDot");
  const dotColors = {
    active: "#16a34a",
    probation: "#d97706",
    notice: "#2557d6",
    inactive: "#9096b0",
  };

  function updateDot() {
    if (statusSelect && statusDot) {
      statusDot.style.background = dotColors[statusSelect.value] || "#9096b0";
    }
  }

  if (statusSelect) {
    statusSelect.addEventListener("change", updateDot);
    updateDot();
  }

  const tagsWrap = document.getElementById("tagsWrap");
  const tagsInput = document.getElementById("tagsInput");
  const skillsHidden = document.getElementById("skillsHidden");
  const tags = (skillsHidden?.value || "")
    .split(",")
    .map((skill) => skill.trim())
    .filter(Boolean);

  function renderTags() {
    if (!tagsWrap || !tagsInput || !skillsHidden) return;

    tagsWrap.querySelectorAll(".tag").forEach((tag) => tag.remove());
    tags.forEach((tag, index) => {
      const el = document.createElement("span");
      el.className = "tag";
      el.innerHTML = `${tag} <button type="button" data-i="${index}" aria-label="Remove ${tag}"><i class="fa-solid fa-xmark"></i></button>`;
      tagsWrap.insertBefore(el, tagsInput);
    });
    skillsHidden.value = tags.join(",");
  }

  if (tagsInput && tagsWrap) {
    tagsInput.addEventListener("keydown", (event) => {
      if ((event.key === "Enter" || event.key === ",") && tagsInput.value.trim()) {
        event.preventDefault();
        const value = tagsInput.value.replace(/,/g, "").trim();
        if (value && !tags.includes(value)) {
          tags.push(value);
          renderTags();
        }
        tagsInput.value = "";
      }

      if (event.key === "Backspace" && !tagsInput.value && tags.length) {
        tags.pop();
        renderTags();
      }
    });

    tagsWrap.addEventListener("click", (event) => {
      const button = event.target.closest("[data-i]");
      if (button) {
        tags.splice(Number(button.dataset.i), 1);
        renderTags();
      }
      tagsInput.focus();
    });

    renderTags();
  }
})();
