// static/js/admin/clients.js
(function () {
  "use strict";

  /* ── API URLs ─────────────────────────────────────────────────────── */
  const API_LIST = "/dashboard/api/clients/";
  const API_CREATE = "/dashboard/api/clients/create/";
  const API_GET_ONE = (id) => `/dashboard/api/clients/${id}/`;
  const API_UPDATE = (id) => `/dashboard/api/clients/${id}/update/`;
  const API_DELETE = (id) => `/dashboard/api/clients/${id}/delete/`;

  /* ── DOM refs ─────────────────────────────────────────────────────── */
  const root = document.querySelector(".mycrm-admin");
  const tableBody = root.querySelector("[data-mycrm-table] tbody");
  const modal = root.querySelector("[data-mycrm-modal]");
  const modalTitle = root.querySelector("[data-mycrm-modal-title]");
  const form = root.querySelector("[data-mycrm-form]");
  const viewModal = document.querySelector("[data-view-modal]");
  
  /* ── State ────────────────────────────────────────────────────────── */
  let clients = [];
  let editId = null;

  /* ── Boot ─────────────────────────────────────────────────────────── */
  bindShell();
  bindClientModal();
  init();

  async function init() {
    await loadClients();
  }

  /* ═══════════════════════════════════════════════════════════════════
     SIDEBAR
  ═══════════════════════════════════════════════════════════════════ */
  function bindShell() {
    const sidebar = root.querySelector("[data-mycrm-sidebar]");
    const backdrop = root.querySelector("[data-mycrm-sidebar-backdrop]");
    
    if (!sidebar || !backdrop) return;
    
    const toggleBtn = root.querySelector("[data-mycrm-sidebar-toggle]");
    if (toggleBtn) {
      toggleBtn.addEventListener("click", () => {
        if (innerWidth <= 980) {
          sidebar.classList.toggle("mycrm-open");
          backdrop.classList.toggle("mycrm-open");
        } else {
          root.classList.toggle("mycrm-sidebar-closed");
        }
      });
    }
    
    backdrop.addEventListener("click", () => {
      sidebar.classList.remove("mycrm-open");
      backdrop.classList.remove("mycrm-open");
    });
  }

  /* ═══════════════════════════════════════════════════════════════════
     API HELPERS
  ═══════════════════════════════════════════════════════════════════ */
  async function apiFetch(url, options = {}) {
    const headers = {
      "X-CSRFToken": getCsrfToken(),
    };
    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }
    
    try {
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
      
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return response.json();
      }
      return null;
      
    } catch (err) {
      console.error("API Error:", err);
      throw err;
    }
  }

  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  }

  /* ═══════════════════════════════════════════════════════════════════
     CLIENT CRUD — API CALLS
  ═══════════════════════════════════════════════════════════════════ */
  async function loadClients() {
    showTableMessage("Loading...");
    try {
      const data = await apiFetch(API_LIST);
      console.log("API Response:", data);
      
      if (Array.isArray(data)) {
        clients = data;
      } else if (data && Array.isArray(data.results)) {
        clients = data.results;
      } else if (data && typeof data === 'object') {
        clients = Object.values(data);
      } else {
        clients = [];
      }
      
      renderClients();
    } catch (err) {
      console.error("Failed to load clients:", err);
      showTableMessage("Failed to load clients. Please try again.");
    }
  }

  async function createClient(formData) {
    return apiFetch(API_CREATE, {
      method: "POST",
      body: formData,
    });
  }

  async function updateClient(id, formData) {
    return apiFetch(API_UPDATE(id), {
      method: "PUT",
      body: formData,
    });
  }

  async function deleteClientById(id) {
    return apiFetch(API_DELETE(id), {
      method: "DELETE",
    });
  }

  /* ═══════════════════════════════════════════════════════════════════
     MODAL — OPEN / CLOSE
  ═══════════════════════════════════════════════════════════════════ */
  function bindClientModal() {
    const addBtn = root.querySelector("[data-mycrm-add]");
    if (addBtn) {
      addBtn.addEventListener("click", () => openClientModal());
    }
    
    root.querySelectorAll("[data-mycrm-modal-close]").forEach((btn) =>
      btn.addEventListener("click", closeClientModal)
    );
    
    const closeViewBtns = document.querySelectorAll("[data-close-view]");
    closeViewBtns.forEach((btn) => {
      btn.addEventListener("click", closeViewModal);
    });
    
    tableBody.addEventListener("click", handleClientAction);
    form.addEventListener("submit", saveClient);  // ← YEH LINE IMPORTANT
  }

  function openClientModal(id = null) {
    closeViewModal();
    editId = id;
    form.reset();
    
    if (modalTitle) {
      modalTitle.textContent = id !== null ? "Edit Client" : "Add Client";
    }
    
    if (id !== null) {
      const client = clients.find((c) => c.id === id);
      if (client) {
        const fields = ["company_name", "client_name", "email", "phone", "address", "client_since"];
        fields.forEach((f) => {
          if (form.elements[f]) form.elements[f].value = client[f] || "";
        });
        if (form.elements.is_active) {
          form.elements.is_active.checked = client.is_active !== false;
        }
      }
    } else {
      if (form.elements.is_active) {
        form.elements.is_active.checked = true;
      }
    }
    
    modal.classList.add("mycrm-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeClientModal() {
    modal.classList.remove("mycrm-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    editId = null;
  }

  /* ═══════════════════════════════════════════════════════════════════
     SAVE CLIENT (CREATE + UPDATE) — YEH FUNCTION MISSING THA!
  ═══════════════════════════════════════════════════════════════════ */
  async function saveClient(event) {
    event.preventDefault();

    const formData = new FormData(form);
    
    // Checkbox manually handle karo
    formData.set("is_active", form.elements.is_active.checked ? "true" : "false");

    // Agar logo file nahi select ki, toh empty mat bhejo
    const logoFile = formData.get("logo");
    if (logoFile && logoFile.size === 0) {
      formData.delete("logo");
    }

    const saveBtn = form.querySelector('[type="submit"]');
    if (saveBtn) saveBtn.disabled = true;

    try {
      if (editId !== null) {
        await updateClient(editId, formData);
        showToast("Client updated successfully");
      } else {
        await createClient(formData);
        showToast("Client added successfully");
      }
      await loadClients();
      closeClientModal();
    } catch (err) {
      console.error("Save failed:", err);
      showToast("Save failed — check console");
    } finally {
      if (saveBtn) saveBtn.disabled = false;
    }
  }

  /* ═══════════════════════════════════════════════════════════════════
     TABLE ACTIONS — VIEW / EDIT / DELETE
  ═══════════════════════════════════════════════════════════════════ */
  function handleClientAction(event) {
    const viewBtn = event.target.closest("[data-mycrm-view]");
    const editBtn = event.target.closest("[data-mycrm-edit]");
    const deleteBtn = event.target.closest("[data-mycrm-delete]");

    if (viewBtn) viewClient(Number(viewBtn.dataset.mycrmView));
    if (editBtn) openClientModal(Number(editBtn.dataset.mycrmEdit));
    if (deleteBtn) confirmDelete(Number(deleteBtn.dataset.mycrmDelete));
  }

  async function confirmDelete(id) {
    if (!confirm("Are you sure you want to delete this client?")) return;
    try {
      await deleteClientById(id);
      await loadClients();
      showToast("Client deleted successfully");
    } catch (err) {
      console.error("Delete failed:", err);
      showToast("Delete failed — check console");
    }
  }

  /* ═══════════════════════════════════════════════════════════════════
     VIEW CLIENT DETAILS
  ═══════════════════════════════════════════════════════════════════ */
  function viewClient(id) {
    closeClientModal();
    const client = clients.find((c) => c.id === id);
    if (!client) {
      console.error("Client not found:", id);
      return;
    }

    const setText = (selector, value) => {
      const el = document.querySelector(selector);
      if (el) el.textContent = value || "—";
    };

    setText("[data-view-name]", client.client_name);
    setText("[data-view-company]", client.company_name);
    setText("[data-view-email]", client.email);
    setText("[data-view-phone]", client.phone);
    setText("[data-view-address]", client.address);
    setText("[data-view-client-since]", client.client_since);
    setText("[data-view-status]", client.is_active ? "Active" : "Inactive");

    const logo = document.querySelector("[data-view-logo]");
    if (logo) {
      if (client.logo_url) {
        logo.src = client.logo_url;
        logo.style.display = "block";
      } else {
        logo.style.display = "none";
      }
    }

    if (viewModal) {
      viewModal.classList.add("mycrm-open");
      viewModal.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
    }
  }

  function closeViewModal() {
    if (viewModal) {
      viewModal.classList.remove("mycrm-open");
      viewModal.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }
  }

  /* ═══════════════════════════════════════════════════════════════════
     RENDER TABLE
  ═══════════════════════════════════════════════════════════════════ */
  function renderClients() {
    tableBody.textContent = "";

    if (!clients || !clients.length) {
      showTableMessage("No clients yet. Click Add Client to get started.");
      return;
    }

    clients.forEach((client) => {
      console.log("RENDERING CLIENT:", client);
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${personCell(client.client_name)}</td>
        <td>${escHtml(client.company_name)}</td>
        <td>${escHtml(client.email || "—")}</td>
        <td>${escHtml(client.phone || "—")}</td>
        <td>${rowActions(client.id)}</td>
      `;
      tableBody.appendChild(row);
    });
  }

  function personCell(name) {
    return `<div class="mycrm-person-cell"><strong>${escHtml(name || "")}</strong></div>`;
  }

  function rowActions(id) {
    return `<div class="mycrm-actions-row">
      <button class="mycrm-btn mycrm-btn-info mycrm-btn-sm" type="button" data-mycrm-view="${id}">View</button>
      <button class="mycrm-btn mycrm-btn-warning mycrm-btn-sm" type="button" data-mycrm-edit="${id}">Edit</button>
      <button class="mycrm-btn mycrm-btn-danger mycrm-btn-sm" type="button" data-mycrm-delete="${id}">Delete</button>
    </div>`;
  }

  function showTableMessage(msg) {
    tableBody.innerHTML = `<tr><td colspan="5" class="mycrm-table-msg">${escHtml(msg)}</td></tr>`;
  }

  /* ═══════════════════════════════════════════════════════════════════
     UTILITIES
  ═══════════════════════════════════════════════════════════════════ */
  function escHtml(value) {
    if (value === null || value === undefined) return "";
    return String(value).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" })[c]
    );
  }

  function showToast(message) {
    const toast = root.querySelector("[data-mycrm-toast]");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("mycrm-show");
    setTimeout(() => toast.classList.remove("mycrm-show"), 1800);
  }
})();


































































































// // static/js/admin/client.js
// (function () {
//   "use strict";

//   /* ── API URLs ─────────────────────────────────────────────────────── */
//   const API_LIST = "/dashboard/api/clients/";
//   const API_CREATE = "/dashboard/api/clients/create/";
//   const API_GET_ONE = (id) => `/dashboard/api/clients/${id}/`;
//   const API_UPDATE = (id) => `/dashboard/api/clients/${id}/update/`;
//   const API_DELETE = (id) => `/dashboard/api/clients/${id}/delete/`;

//   /* ── DOM refs ─────────────────────────────────────────────────────── */
//   const root = document.querySelector(".mycrm-admin");
//   const tableBody = root.querySelector("[data-mycrm-table] tbody");
//   const modal = root.querySelector("[data-mycrm-modal]");
//   const modalTitle = root.querySelector("[data-mycrm-modal-title]");
//   const form = root.querySelector("[data-mycrm-form]");
//   const viewModal = document.querySelector("[data-view-modal]");
  
//   /* ── State ────────────────────────────────────────────────────────── */
//   let clients = [];
//   let editId = null;

//   /* ── Boot ─────────────────────────────────────────────────────────── */
//   bindShell();
//   bindClientModal();
//   init();

//   async function init() {
//     await loadClients();
//   }

//   /* ═══════════════════════════════════════════════════════════════════
//      SIDEBAR
//   ═══════════════════════════════════════════════════════════════════ */
//   function bindShell() {
//     const sidebar = root.querySelector("[data-mycrm-sidebar]");
//     const backdrop = root.querySelector("[data-mycrm-sidebar-backdrop]");
//     root.querySelector("[data-mycrm-sidebar-toggle]").addEventListener("click", () => {
//       if (innerWidth <= 980) {
//         sidebar.classList.toggle("mycrm-open");
//         backdrop.classList.toggle("mycrm-open");
//       } else {
//         root.classList.toggle("mycrm-sidebar-closed");
//       }
//     });
//     backdrop.addEventListener("click", () => {
//       sidebar.classList.remove("mycrm-open");
//       backdrop.classList.remove("mycrm-open");
//     });
//   }

//   /* ═══════════════════════════════════════════════════════════════════
//      API HELPERS
//   ═══════════════════════════════════════════════════════════════════ */
//   async function apiFetch(url, options = {}) {
//     const headers = {
//       "X-CSRFToken": getCsrfToken(),
//     };
//     // FormData ke liye Content-Type mat set karo — browser khud set karega
//     if (!(options.body instanceof FormData)) {
//       headers["Content-Type"] = "application/json";
//     }
//     const response = await fetch(url, {
//       ...options,
//       headers,
//       credentials: "same-origin",
//     });
//     if (!response.ok) {
//       const text = await response.text();
//       throw new Error(`${response.status}: ${text}`);
//     }
//     if (response.status === 204) return null;
//     return response.json();
//   }

//   function getCsrfToken() {
//     const match = document.cookie.match(/csrftoken=([^;]+)/);
//     return match ? match[1] : "";
//   }

//   /* ═══════════════════════════════════════════════════════════════════
//      CLIENT CRUD — API CALLS
//   ═══════════════════════════════════════════════════════════════════ */
//   async function loadClients() {
//     showTableMessage("Loading...");
//     try {
//       clients = await apiFetch(API_LIST);
//       renderClients();
//     } catch (err) {
//       console.error("Failed to load clients:", err);
//       showTableMessage("Failed to load clients. Please try again.");
//     }
//   }

//   async function createClient(formData) {
//     return apiFetch(API_CREATE, {
//       method: "POST",
//       body: formData,
//     });
//   }

//   async function updateClient(id, formData) {
//     return apiFetch(API_UPDATE(id), {
//       method: "PUT",
//       body: formData,
//     });
//   }

//   async function deleteClientById(id) {
//     return apiFetch(API_DELETE(id), {
//       method: "DELETE",
//     });
//   }

//   /* ═══════════════════════════════════════════════════════════════════
//      MODAL — OPEN / CLOSE
//   ═══════════════════════════════════════════════════════════════════ */
//   function bindClientModal() {
//     root.querySelector("[data-mycrm-add]").addEventListener("click", () => openClientModal());
//     root.querySelectorAll("[data-mycrm-modal-close]").forEach((btn) =>
//       btn.addEventListener("click", closeClientModal)
//     );
//     document.querySelector("[data-close-view]")?.addEventListener("click", closeViewModal);
//     tableBody.addEventListener("click", handleClientAction);
//     form.addEventListener("submit", saveClient);
//   }

//   function openClientModal(id = null) {
//     editId = id;
//     form.reset();
    
//     if (id !== null) {
//       const client = clients.find((c) => c.id === id);
//       if (client) {
//         // Form fields fill karo
//         const fields = ["company_name", "client_name", "email", "phone", "address", "client_since"];
//         fields.forEach((f) => {
//           if (form.elements[f]) form.elements[f].value = client[f] || "";
//         });
//         // Checkbox
//         if (form.elements.is_active) {
//           form.elements.is_active.checked = client.is_active;
//         }
//       }
//       modalTitle.textContent = "Edit Client";
//     } else {
//       modalTitle.textContent = "Add Client";
//     }
    
//     modal.classList.add("mycrm-open");
//     modal.setAttribute("aria-hidden", "false");
//   }

//   function closeClientModal() {
//     modal.classList.remove("mycrm-open");
//     modal.setAttribute("aria-hidden", "true");
//     editId = null;
//   }

//   function closeViewModal() {
//     viewModal?.classList.remove("mycrm-open");
//   }

//   /* ═══════════════════════════════════════════════════════════════════
//      SAVE CLIENT (CREATE + UPDATE)
//   ═══════════════════════════════════════════════════════════════════ */
//   async function saveClient(event) {
//     event.preventDefault();

//     const formData = new FormData(form);
    
//     // Checkbox manually handle karo
//     formData.set("is_active", form.elements.is_active.checked ? "true" : "false");

//     // Agar logo file nahi select ki, toh empty mat bhejo
//     const logoFile = formData.get("logo");
//     if (logoFile && logoFile.size === 0) {
//       formData.delete("logo");
//     }

//     const saveBtn = form.querySelector('[type="submit"]');
//     saveBtn.disabled = true;

//     try {
//       if (editId !== null) {
//         await updateClient(editId, formData);
//         showToast("Client updated successfully");
//       } else {
//         await createClient(formData);
//         showToast("Client added successfully");
//       }
//       await loadClients();
//       closeClientModal();
//     } catch (err) {
//       console.error("Save failed:", err);
//       showToast("Save failed — check console");
//     } finally {
//       saveBtn.disabled = false;
//     }
//   }

//   /* ═══════════════════════════════════════════════════════════════════
//      TABLE ACTIONS — VIEW / EDIT / DELETE
//   ═══════════════════════════════════════════════════════════════════ */
//   function handleClientAction(event) {
//     const viewBtn = event.target.closest("[data-mycrm-view]");
//     const editBtn = event.target.closest("[data-mycrm-edit]");
//     const deleteBtn = event.target.closest("[data-mycrm-delete]");

//     if (viewBtn) viewClient(Number(viewBtn.dataset.mycrmView));
//     if (editBtn) openClientModal(Number(editBtn.dataset.mycrmEdit));
//     if (deleteBtn) confirmDelete(Number(deleteBtn.dataset.mycrmDelete));
//   }

//   async function confirmDelete(id) {
//     if (!confirm("Are you sure you want to delete this client?")) return;
//     try {
//       await deleteClientById(id);
//       await loadClients();
//       showToast("Client deleted successfully");
//     } catch (err) {
//       console.error("Delete failed:", err);
//       showToast("Delete failed — check console");
//     }
//   }

//   /* ═══════════════════════════════════════════════════════════════════
//      VIEW CLIENT DETAILS
//   ═══════════════════════════════════════════════════════════════════ */
//   function viewClient(id) {
//     const client = clients.find((c) => c.id === id);
//     if (!client) return;

//     document.querySelector("[data-view-name]").textContent = client.client_name || "—";
//     document.querySelector("[data-view-company]").textContent = client.company_name || "—";
//     document.querySelector("[data-view-email]").textContent = client.email || "—";
//     document.querySelector("[data-view-phone]").textContent = client.phone || "—";
//     document.querySelector("[data-view-address]").textContent = client.address || "—";
//     document.querySelector("[data-view-client-since]").textContent = client.client_since || "—";
//     document.querySelector("[data-view-status]").textContent = client.is_active ? "Active" : "Inactive";

//     const logo = document.querySelector("[data-view-logo]");
//     if (client.logo_url) {
//       logo.src = client.logo_url;
//       logo.style.display = "block";
//     } else {
//       logo.style.display = "none";
//     }

//     viewModal.classList.add("mycrm-open");
//   }

//   /* ═══════════════════════════════════════════════════════════════════
//      RENDER TABLE
//   ═══════════════════════════════════════════════════════════════════ */
//   function renderClients() {
//     tableBody.textContent = "";

//     if (!clients.length) {
//       showTableMessage("No clients yet. Click Add Client to get started.");
//       return;
//     }

//     clients.forEach((client) => {
//       const row = document.createElement("tr");
//       row.innerHTML = `
//         <td>${personCell(client.client_name, client.company_name)}</td>
//         <td>${escHtml(client.company_name)}</td>
//         <td>${escHtml(client.email)}</td>
//         <td>${escHtml(client.phone)}</td>
//         <td>${rowActions(client.id)}</td>
//       `;
//       tableBody.appendChild(row);
//     });
//   }

//   function personCell(name, company) {
//     return `<div class="mycrm-person-cell"><strong>${escHtml(name)}</strong><small>${escHtml(company)}</small></div>`;
//   }

//   function rowActions(id) {
//     return `<div class="mycrm-actions-row">
//       <button class="mycrm-btn mycrm-btn-info mycrm-btn-sm" type="button" data-mycrm-view="${id}">View</button>
//       <button class="mycrm-btn mycrm-btn-warning mycrm-btn-sm" type="button" data-mycrm-edit="${id}">Edit</button>
//       <button class="mycrm-btn mycrm-btn-danger mycrm-btn-sm" type="button" data-mycrm-delete="${id}">Delete</button>
//     </div>`;
//   }

//   function showTableMessage(msg) {
//     tableBody.innerHTML = `<tr><td colspan="5" class="mycrm-table-msg">${escHtml(msg)}</td></tr>`;
//   }

//   /* ═══════════════════════════════════════════════════════════════════
//      UTILITIES
//   ═══════════════════════════════════════════════════════════════════ */
//   function escHtml(value) {
//     return String(value).replace(/[&<>"']/g, (c) =>
//       ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" })[c]
//     );
//   }

//   function showToast(message) {
//     const toast = root.querySelector("[data-mycrm-toast]");
//     toast.textContent = message;
//     toast.classList.add("mycrm-show");
//     setTimeout(() => toast.classList.remove("mycrm-show"), 1800);
//   }
// })();
