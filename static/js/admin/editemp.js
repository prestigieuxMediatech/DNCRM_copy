(function () {
  const form = document.getElementById("empForm");
  if (!form) return;

  const profileInput = document.getElementById("profileImageInput");
  const fileNameDisplay = document.getElementById("fileNameDisplay");
  const avatarPreview = document.getElementById("avatarPreview");
  const cardAvatar = document.getElementById("cardAvatar");

  if (profileInput) {
    profileInput.addEventListener("change", function () {
      const file = this.files && this.files[0];
      if (!file) return;

      if (fileNameDisplay) fileNameDisplay.textContent = file.name;

      const reader = new FileReader();
      reader.onload = (event) => {
        const image = `<img src="${event.target.result}" alt="Preview" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" />`;
        if (avatarPreview) avatarPreview.innerHTML = image;
        if (cardAvatar) cardAvatar.innerHTML = image;
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
  const tags = (skillsHidden?.value || window.initialSkills || "")
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

  const deleteButton = document.getElementById("deleteBtn");
  const deleteBackdrop = document.getElementById("delModalBackdrop");
  const cancelButton = document.getElementById("delCancelBtn");
  const confirmButton = document.getElementById("delConfirmBtn");

  if (deleteButton && deleteBackdrop) {
    deleteButton.addEventListener("click", () => deleteBackdrop.classList.add("show"));
  }

  if (cancelButton && deleteBackdrop) {
    cancelButton.addEventListener("click", () => deleteBackdrop.classList.remove("show"));
  }

  if (confirmButton) {
    confirmButton.addEventListener("click", () => {
      const deleteUrl = form.dataset.deleteUrl;
      const csrf = form.querySelector("[name=csrfmiddlewaretoken]")?.value;
      if (!deleteUrl || !csrf) return;

      fetch(deleteUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrf,
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            window.location.href = form.dataset.listUrl || "/dashboard/admin/employees/";
          }
        });
    });
  }
})();
