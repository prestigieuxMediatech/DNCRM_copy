(function () {

  /* ── Config ── */
  const API_URL    = window.MYCRM_USER_API_URL || "/dashboard/admin/users/api/";
  const CSRF_TOKEN = document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? "";

  let editId = null;

  /* ── DOM ── */
  const root      = document.querySelector(".mycrm-admin");
  const tableBody = root.querySelector("[data-mycrm-table] tbody");
  const modal     = root.querySelector("[data-mycrm-modal]");
  const form      = root.querySelector("[data-mycrm-form]");

  init();

  function init() {
    initRolePicker();
    /* Modal */
    root.querySelector("[data-mycrm-add]").addEventListener("click", () => openModal());
    root.querySelectorAll("[data-mycrm-modal-close]").forEach(btn =>
      btn.addEventListener("click", closeModal)
    );
    tableBody.addEventListener("click", handleTableClick);
    form.addEventListener("submit", saveUser);

    fetchAndRender();  // page load pe data fetch karo
  }

  function initRolePicker() {
    const select = form.elements["role"];
    if (!select) return;

    const group = select.closest(".mycrm-form-group");
    const picker = document.createElement("div");
    picker.className = "mycrm-role-picker";
    picker.innerHTML = '<button type="button" class="mycrm-role-picker-trigger" aria-haspopup="listbox" aria-expanded="false"></button><div class="mycrm-role-picker-options" role="listbox"></div>';
    group.appendChild(picker);
    select.classList.add("mycrm-role-native-select");

    const trigger = picker.querySelector(".mycrm-role-picker-trigger");
    const options = picker.querySelector(".mycrm-role-picker-options");
    const refresh = () => {
      const selected = select.selectedOptions[0];
      trigger.textContent = selected ? selected.textContent.trim() : "Select Role";
      options.querySelectorAll("[role=option]").forEach((item) => {
        item.setAttribute("aria-selected", String(item.dataset.value === select.value));
      });
    };

    Array.from(select.options).forEach((option) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "mycrm-role-picker-option";
      item.setAttribute("role", "option");
      item.dataset.value = option.value;
      item.textContent = option.textContent.trim();
      item.addEventListener("click", () => {
        select.value = option.value;
        select.dispatchEvent(new Event("change", { bubbles: true }));
        picker.classList.remove("is-open");
        trigger.setAttribute("aria-expanded", "false");
        refresh();
      });
      options.appendChild(item);
    });

    trigger.addEventListener("click", () => {
      const open = picker.classList.toggle("is-open");
      trigger.setAttribute("aria-expanded", String(open));
    });
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
    select.addEventListener("change", refresh);
    form.addEventListener("reset", () => window.setTimeout(refresh));
    refresh();
  }

  /* ── Fetch & Render ── */
  async function fetchAndRender() {
    try {
      const res  = await fetch(API_URL);
      const data = await res.json();
      renderTable(data.users);
    } catch {
      showToast("Failed to load users", true);
    }
  }

  /* ── Modal ── */
  function openModal(user = null) {
    editId = user ? user.id : null;
    form.reset();

    const heading = modal.querySelector(".mycrm-modal-header h2");

    if (user) {
      form.elements["email"].value       = user.email;
      form.elements["role"].value        = user.role;
      form.elements["role"].dispatchEvent(new Event("change", { bubbles: true }));
      form.elements["is_active"].checked = user.is_active;
      form.elements["is_staff"].checked  = user.is_staff;
      heading.textContent = "Edit User Details";

      // Edit mein password required nahi
      form.elements["password"].removeAttribute("required");
      form.elements["confirm_password"].removeAttribute("required");
    } else {
      heading.textContent = "Add User Details";
      form.elements["password"].setAttribute("required", "");
      form.elements["confirm_password"].setAttribute("required", "");
    }

    modal.classList.add("mycrm-open");
    modal.setAttribute("aria-hidden", "false");
  }

  function closeModal() {
    modal.classList.remove("mycrm-open");
    modal.setAttribute("aria-hidden", "true");
  }

  /* ── Save (Add / Edit) ── */
  async function saveUser(e) {
    e.preventDefault();

    const email    = form.elements["email"].value.trim();
    const role     = form.elements["role"].value;
    const password = form.elements["password"].value;
    const confirm  = form.elements["confirm_password"].value;
    const isActive = form.elements["is_active"].checked;
    const isStaff  = form.elements["is_staff"].checked;

    // Frontend password check
    if (password && password !== confirm) {
      showToast("Passwords do not match", true);
      return;
    }

    const payload = { email, role, password, confirm_password: confirm,
                      is_active: isActive, is_staff: isStaff };

    try {
      let res;

      if (editId === null) {
        // ADD
        res = await fetch(API_URL, {
          method:  "POST",
          headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF_TOKEN },
          body:    JSON.stringify(payload),
        });
      } else {
        // EDIT
        res = await fetch(`${API_URL}${editId}/`, {
          method:  "PUT",
          headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF_TOKEN },
          body:    JSON.stringify(payload),
        });
      }

      const data = await res.json();

      if (!res.ok) {
        showToast(data.error || "Something went wrong", true);
        return;
      }

      showToast(data.message);
      closeModal();
      fetchAndRender();  // table refresh karo

    } catch {
      showToast("Network error", true);
    }
  }

  /* ── Table click ── */
  function handleTableClick(e) {
    const editBtn   = e.target.closest("[data-mycrm-edit]");
    const deleteBtn = e.target.closest("[data-mycrm-delete]");

    if (editBtn) {
      // Edit ke liye user data DOM se nahi, API se lo
      const userId = Number(editBtn.dataset.mycrmEdit);
      openModalById(userId);
    }
    if (deleteBtn) {
      deleteUser(Number(deleteBtn.dataset.mycrmDelete));
    }
  }

  async function openModalById(userId) {
    try {
      const res  = await fetch(API_URL);
      const data = await res.json();
      const user = data.users.find(u => u.id === userId);
      if (user) openModal(user);
    } catch {
      showToast("Failed to load user", true);
    }
  }

  /* ── Delete ── */
  async function deleteUser(id) {
    try {
      const res  = await fetch(`${API_URL}${id}/`, {
        method:  "DELETE",
        headers: { "X-CSRFToken": CSRF_TOKEN },
      });
      const data = await res.json();

      if (!res.ok) {
        showToast(data.error || "Delete failed", true);
        return;
      }

      showToast(data.message);
      fetchAndRender();

    } catch {
      showToast("Network error", true);
    }
  }

  /* ── Render Table ── */
  function renderTable(users) {
    tableBody.innerHTML = "";

    if (!users || users.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#687385;padding:28px">No users found</td></tr>`;
      return;
    }

    users.forEach(u => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${escHtml(u.email)}</td>
        <td>${capitalize(u.role)}</td>
        <td>${badge(u.is_active)}</td>
        <td>${badge(u.is_staff)}</td>
        <td>${badge(u.is_superuser)}</td>
        <td>
          <div class="mycrm-actions-row">
            <button class="mycrm-btn mycrm-btn-warning mycrm-btn-sm" type="button" data-mycrm-edit="${u.id}">Edit</button>
            <button class="mycrm-btn mycrm-btn-danger  mycrm-btn-sm" type="button" data-mycrm-delete="${u.id}">Delete</button>
          </div>
        </td>`;
      tableBody.appendChild(tr);
    });
  }

  /* ── Helpers ── */
  function badge(val) {
    return `<span class="mycrm-badge ${val ? "mycrm-badge-success" : "mycrm-badge-warning"}">${val ? "Yes" : "No"}</span>`;
  }
  function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : "—";
  }
  function escHtml(str) {
    return String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }
  function showToast(msg, isError = false) {
    const toast = root.querySelector("[data-mycrm-toast]");
    toast.textContent = msg;
    toast.style.background = isError ? "#dc2626" : "#111827";
    toast.classList.add("mycrm-show");
    setTimeout(() => toast.classList.remove("mycrm-show"), 2000);
  }

})();
