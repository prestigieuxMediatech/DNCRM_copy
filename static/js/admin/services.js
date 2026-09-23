(function () {
  "use strict";

  const API_LIST = "/dashboard/api/services/";
  const API_CREATE = "/dashboard/api/services/create/";
  const API_GET_ONE = (id) => `/dashboard/api/services/${id}/`;
  const API_UPDATE = (id) => `/dashboard/api/services/${id}/update/`;
  const API_DELETE = (id) => `/dashboard/api/services/${id}/delete/`;

  const root = document.querySelector(".mycrm-admin") || document.body;
  const tableBody = root.querySelector("[data-mycrm-table] tbody");
  const modal = root.querySelector("[data-mycrm-modal]");
  const modalTitle = root.querySelector("[data-mycrm-modal-title]");
  const form = root.querySelector("[data-mycrm-form]");

  let services = [];
  let editId = null;

  bindModal();
  init();

  async function init() {
    await loadServices();
  }

  async function apiFetch(url, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
      ...(options.headers || {})
    };
    const response = await fetch(url, {
      ...options,
      headers,
      credentials: "same-origin",
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`${response.status}: ${text}`);
    }
    if (response.status === 204) return null;
    return response.json();
  }

  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  }

  async function loadServices() {
    showTableMessage("Loading services...");
    try {
      const data = await apiFetch(API_LIST);
      services = Array.isArray(data) ? data : [];
      renderServices();
    } catch (err) {
      console.error("Failed to load services:", err);
      showTableMessage("Failed to load services.");
    }
  }

  async function createService(payload) {
    return apiFetch(API_CREATE, { method: "POST", body: JSON.stringify(payload) });
  }

  async function updateService(id, payload) {
    return apiFetch(API_UPDATE(id), { method: "PUT", body: JSON.stringify(payload) });
  }

  async function deleteServiceById(id) {
    return apiFetch(API_DELETE(id), { method: "DELETE" });
  }

  function bindModal() {
    const addBtn = root.querySelector("[data-mycrm-add]");
    if (addBtn) {
      addBtn.addEventListener("click", () => openModal());
    }

    root.querySelectorAll("[data-mycrm-modal-close]").forEach((btn) =>
      btn.addEventListener("click", closeModal)
    );

    if (tableBody) {
      tableBody.addEventListener("click", handleTableClick);
    }

    if (form) {
      form.addEventListener("submit", saveService);
    }
  }

  function openModal(id = null) {
    editId = id;
    if (form) form.reset();

    if (id !== null) {
      const svc = services.find((s) => s.id === id);
      if (svc && form) {
        form.elements.name.value = svc.name || "";
        form.elements.description.value = svc.description || "";
        form.elements.base_price.value = svc.base_price || "";
        form.elements.is_active.checked = svc.is_active !== false;
      }
      if (modalTitle) modalTitle.textContent = "Edit Service";
    } else {
      if (modalTitle) modalTitle.textContent = "Add Service";
      if (form && form.elements.is_active) form.elements.is_active.checked = true;
    }

    if (modal) {
      modal.classList.add("mycrm-open");
      modal.setAttribute("aria-hidden", "false");
    }
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    if (modal) {
      modal.classList.remove("mycrm-open");
      modal.setAttribute("aria-hidden", "true");
    }
    document.body.style.overflow = "";
    editId = null;
  }

  async function saveService(e) {
    e.preventDefault();
    const payload = {
      name: form.elements.name.value,
      description: form.elements.description.value,
      base_price: form.elements.base_price.value,
      is_active: form.elements.is_active.checked,
    };
    const saveBtn = form.querySelector('[type="submit"]');
    if (saveBtn) saveBtn.disabled = true;

    try {
      if (editId !== null) {
        await updateService(editId, payload);
        showToast("Service updated successfully");
      } else {
        await createService(payload);
        showToast("Service added successfully");
      }
      await loadServices();
      closeModal();
    } catch (err) {
      console.error(err);
      showToast("Save failed — check console for details");
    } finally {
      if (saveBtn) saveBtn.disabled = false;
    }
  }

  function handleTableClick(e) {
    const editBtn = e.target.closest("[data-mycrm-edit]");
    const deleteBtn = e.target.closest("[data-mycrm-delete]");
    if (editBtn) openModal(Number(editBtn.dataset.mycrmEdit));
    if (deleteBtn) confirmDelete(Number(deleteBtn.dataset.mycrmDelete));
  }

  async function confirmDelete(id) {
    if (!confirm("Are you sure you want to delete this service?")) return;
    try {
      await deleteServiceById(id);
      await loadServices();
      showToast("Service deleted");
    } catch (err) {
      showToast("Delete failed");
    }
  }

  function renderServices() {
    if (!tableBody) return;
    tableBody.innerHTML = "";

    if (!services.length) {
      showTableMessage("No services found. Click 'Add Service' to create one.");
      return;
    }

    services.forEach((svc) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><strong>${escHtml(svc.name)}</strong></td>
        <td>₹${escHtml(svc.base_price)}</td>
        <td>${svc.is_active ? '<span class="mycrm-badge mycrm-badge-success">Active</span>' : '<span class="mycrm-badge mycrm-badge-danger">Inactive</span>'}</td>
        <td class="text-right">
          <div class="mycrm-actions-row" style="justify-content: flex-end;">
            <button class="mycrm-btn mycrm-btn-warning mycrm-btn-sm" data-mycrm-edit="${svc.id}">Edit</button>
            <button class="mycrm-btn mycrm-btn-danger mycrm-btn-sm" data-mycrm-delete="${svc.id}">Delete</button>
          </div>
        </td>`;
      tableBody.appendChild(row);
    });
  }

  function showTableMessage(msg) {
    if (!tableBody) return;
    tableBody.innerHTML = `<tr><td colspan="4" class="mycrm-table-msg">${escHtml(msg)}</td></tr>`;
  }

  function escHtml(value) {
    if (value == null) return "";
    return String(value).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" })[c]
    );
  }

  function showToast(message) {
    const toast = root.querySelector("[data-mycrm-toast]");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("mycrm-show");
    setTimeout(() => toast.classList.remove("mycrm-show"), 2500);
  }
})();














