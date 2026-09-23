(function () {
  "use strict";

  /* ── Config ────────────────────────────────────────────────────────── */
  const API_BASE = "";
  const USE_MOCK_DATA = false;

  /* ── DOM refs ──────────────────────────────────────────────────────── */
  const root = document.querySelector(".mycrm-admin");
  const tableBody = root.querySelector("[data-mycrm-table] tbody");
  const modal = root.querySelector("[data-mycrm-modal]");
  const modalTitle = root.querySelector("[data-mycrm-modal-title]");
  const form = root.querySelector("[data-mycrm-form]");
  const empChips = root.querySelector("[data-emp-chips]");
  const empEmpty = root.querySelector("[data-emp-empty]");
  const empHidden = root.querySelector("[data-emp-hidden]");
  const clientSelect = root.querySelector("[data-client-select]");
  const createdBySelect = root.querySelector("[data-createdby-select]");

  // Employee picker sub-modal
  const pickerModal = root.querySelector("[data-emp-picker-modal]");
  const pickerList = root.querySelector("[data-emp-picker-list]");
  const pickerSearch = root.querySelector("[data-emp-picker-search]");
  const pickerEmpty = root.querySelector("[data-emp-picker-empty]");
  const pickerLoading = root.querySelector("[data-emp-picker-loading]");
  const pickerCount = root.querySelector("[data-emp-picker-count]");

  // View modal
  const viewModal = root.querySelector("[data-project-view-modal]");

  /* ── State ─────────────────────────────────────────────────────────── */
  let projects = [];
  let allEmployees = [];
  let allClients = [];
  let allUsers = [];
  let editId = null;
  let selectedEmpIds = [];
  let draftEmpIds = [];
  let activeFilter = "all";

  /* ── Boot ──────────────────────────────────────────────────────────── */
  bindShell();
  bindProjectModal();
  bindStatCards();
  bindEmployeePicker();
  init();

  async function init() {
    await Promise.all([
      loadDropdownOptions(),
      loadProjects(),
    ]);
  }

  /* ── Sidebar ───────────────────────────────────────────────────────── */
  function bindShell() {
    const sidebar = root.querySelector("[data-mycrm-sidebar]");
    const backdrop = root.querySelector("[data-mycrm-sidebar-backdrop]");
    root.querySelector("[data-mycrm-sidebar-toggle]").addEventListener("click", () => {
      if (innerWidth <= 980) {
        sidebar.classList.toggle("mycrm-open");
        backdrop.classList.toggle("mycrm-open");
      } else {
        root.classList.toggle("mycrm-sidebar-closed");
      }
    });
    backdrop.addEventListener("click", () => {
      sidebar.classList.remove("mycrm-open");
      backdrop.classList.remove("mycrm-open");
    });
  }

  function bindStatCards() {
    root.querySelectorAll(".mycrm-stat-card").forEach(card => {
      card.addEventListener("click", () => {
        activeFilter = card.dataset.filter;
        renderProjects();
      });
    });
  }

  /* ══════════════════════════════════════════════════════════════════════
     API HELPERS
  ══════════════════════════════════════════════════════════════════════ */

  async function apiFetch(path, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
      ...options.headers,
    };
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
      credentials: "same-origin",
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`${response.status} ${response.statusText}: ${text}`);
    }
    return response.status === 204 ? null : response.json();
  }

  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  }

  /* ══════════════════════════════════════════════════════════════════════
     DROPDOWN POPULATION
  ══════════════════════════════════════════════════════════════════════ */

  async function loadDropdownOptions() {
    try {
      const [clients, users] = await Promise.all([
        apiFetch("/dashboard/api/clients/"),
        apiFetch("/dashboard/api/users/"),
      ]);

      allClients = Array.isArray(clients) ? clients : (clients.results || []);
      allUsers = Array.isArray(users) ? users : (users.results || []);

      // Client dropdown
      clientSelect.innerHTML = '<option value="">Select client</option>';
      allClients.forEach((c) => {
        const opt = new Option(c.company_name || c.name, c.id);
        clientSelect.appendChild(opt);
      });

      // Created-by dropdown
      createdBySelect.innerHTML = '<option value="">Select</option>';
      allUsers.forEach((u) => {
        const opt = new Option(u.email, u.id);
        createdBySelect.appendChild(opt);
      });
    } catch (err) {
      console.error("Failed to load dropdown options:", err);
    }
  }

  /* ══════════════════════════════════════════════════════════════════════
     PROJECTS CRUD
  ══════════════════════════════════════════════════════════════════════ */

  async function loadProjects() {
    showTableMessage("Loading…");
    try {
      const data = await apiFetch("/dashboard/api/projects/");
      projects = Array.isArray(data) ? data : (data.results || []);
      renderProjects();
    } catch (err) {
      console.error("Failed to load projects:", err);
      showTableMessage("Failed to load projects. Please try again.");
    }
  }

  async function createProject(payload) {
    return apiFetch("/dashboard/api/projects/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async function updateProject(id, payload) {
    return apiFetch(`/dashboard/api/projects/${id}/`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  async function deleteProjectById(id) {
    await apiFetch(`/dashboard/api/projects/${id}/`, { method: "DELETE" });
    projects = projects.filter((p) => p.id !== id);
  }

  /* ══════════════════════════════════════════════════════════════════════
     PROJECT MODAL - OPEN/CLOSE WITH STYLE.DISPLAY
  ══════════════════════════════════════════════════════════════════════ */

  function bindProjectModal() {
    root.querySelector("[data-mycrm-add]").addEventListener("click", () => openModal());
    root.querySelectorAll("[data-mycrm-modal-close]").forEach((btn) =>
      btn.addEventListener("click", closeModal)
    );
    root.querySelectorAll("[data-close-project-view]").forEach((btn) =>
      btn.addEventListener("click", closeProjectViewModal)
    );
    tableBody.addEventListener("click", handleTableClick);
    form.addEventListener("submit", handleFormSubmit);
  }

  function openModal(id = null) {
    editId = id;
    form.reset();
    selectedEmpIds = [];

    if (id !== null) {
      const project = projects.find((p) => p.id === id);
      if (project) {
        ["project_name", "description", "status", "priority", "budget"].forEach((key) => {
          if (form.elements[key]) form.elements[key].value = project[key] || "";
        });
        if (form.elements.client) form.elements.client.value = project.client || "";
        if (form.elements.created_by) form.elements.created_by.value = project.created_by || "";
        selectedEmpIds = (project.employees || []).map(e => e.id);
      }
    }

    renderChips();
    modalTitle.textContent = id !== null ? "Edit Project" : "Add Project";
    
    // FORCE SHOW
    modal.style.display = "flex";
    modal.classList.add("mycrm-open");
    modal.setAttribute("aria-hidden", "false");
  }

  function closeModal() {
    // FORCE HIDE
    modal.style.display = "none";
    modal.classList.remove("mycrm-open");
    modal.setAttribute("aria-hidden", "true");
    editId = null;
    selectedEmpIds = [];
  }

  function closeProjectViewModal() {
    // FORCE HIDE
    viewModal.style.display = "none";
    viewModal.classList.remove("mycrm-open");
    viewModal.setAttribute("aria-hidden", "true");
  }

  async function handleFormSubmit(e) {
    e.preventDefault();

    const fd = new FormData(form);

    const payload = {
      project_name: fd.get("project_name") || "",
      description: fd.get("description") || "",
      status: fd.get("status") || "pending",
      priority: fd.get("priority") || "medium",
      client: fd.get("client") ? Number(fd.get("client")) : null,
      budget: fd.get("budget") || "0",
      created_by: fd.get("created_by") ? Number(fd.get("created_by")) : null,
      employee_ids: selectedEmpIds.map(Number),
      deadline: fd.get("deadline") || null, 
    };

    const saveBtn = form.querySelector('[type="submit"]');
    saveBtn.disabled = true;

    try {
      if (editId !== null) {
        await updateProject(editId, payload);
        showToast("Project updated");
      } else {
        await createProject(payload);
        showToast("Project added");
      }
      await loadProjects();
      closeModal();
    } catch (err) {
      console.error("Save failed:", err);
      showToast("Save failed — check console");
    } finally {
      saveBtn.disabled = false;
    }
  }

  function handleTableClick(e) {
    const viewBtn = e.target.closest("[data-mycrm-view]");
    const editBtn = e.target.closest("[data-mycrm-edit]");
    const deleteBtn = e.target.closest("[data-mycrm-delete]");

    if (viewBtn) viewProject(Number(viewBtn.dataset.mycrmView));
    if (editBtn) openModal(Number(editBtn.dataset.mycrmEdit));
    if (deleteBtn) confirmDelete(Number(deleteBtn.dataset.mycrmDelete));
  }

  async function confirmDelete(id) {
    if (!confirm("Delete this project?")) return;
    try {
      await deleteProjectById(id);
      renderProjects();
      showToast("Project deleted");
    } catch (err) {
      console.error("Delete failed:", err);
      showToast("Delete failed — check console");
    }
  }

  /* ══════════════════════════════════════════════════════════════════════
     VIEW PROJECT - OPEN/CLOSE WITH STYLE.DISPLAY
  ══════════════════════════════════════════════════════════════════════ */

  function viewProject(id) {
    const project = projects.find((p) => p.id === id);
    if (!project) return;

    document.querySelector("[data-view-project-name]").textContent = project.project_name || "—";
    document.querySelector("[data-view-project-description]").textContent = project.description || "—";
    document.querySelector("[data-view-project-status]").textContent = project.status || "—";
    document.querySelector("[data-view-project-priority]").textContent = project.priority || "—";
    document.querySelector("[data-view-project-client]").textContent = project.client_name || "—";
    document.querySelector("[data-view-project-budget]").textContent = project.budget || "—";
    document.querySelector("[data-view-project-createdby]").textContent = project.created_by_email || "—";

    const employeeNames = (project.employees || [])
      .map(e => e.name || e.full_name || "")
      .filter(Boolean)
      .join(", ");
    document.querySelector("[data-view-project-employees]").textContent = employeeNames || "—";

    // FORCE SHOW
    viewModal.style.display = "flex";
    viewModal.classList.add("mycrm-open");
    viewModal.setAttribute("aria-hidden", "false");
  }

  /* ══════════════════════════════════════════════════════════════════════
     EMPLOYEE PICKER - OPEN/CLOSE WITH STYLE.DISPLAY
  ══════════════════════════════════════════════════════════════════════ */

  function bindEmployeePicker() {
    form.querySelector("[data-open-emp-picker]").addEventListener("click", openPicker);
    pickerModal.querySelectorAll("[data-close-emp-picker]").forEach((btn) =>
      btn.addEventListener("click", closePicker)
    );
    pickerModal.querySelector("[data-confirm-emp-picker]").addEventListener("click", confirmPicker);
    pickerSearch.addEventListener("input", renderPickerList);

    empChips.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-remove-emp]");
      if (!btn) return;
      selectedEmpIds = selectedEmpIds.filter((id) => id !== Number(btn.dataset.removeEmp));
      renderChips();
    });
  }

  async function openPicker() {
    draftEmpIds = [...selectedEmpIds];
    pickerSearch.value = "";

    if (!allEmployees.length) {
      pickerLoading.hidden = false;
      pickerList.hidden = true;
      try {
        const data = await apiFetch("/dashboard/api/employees/");
        allEmployees = Array.isArray(data) ? data : (data.results || []);
      } catch (err) {
        console.error("Failed to load employees:", err);
        showToast("Could not load employee list");
      } finally {
        pickerLoading.hidden = true;
        pickerList.hidden = false;
      }
    }

    renderPickerList();
    
    // FORCE SHOW
    pickerModal.style.display = "flex";
    pickerModal.classList.add("mycrm-open");
    pickerModal.setAttribute("aria-hidden", "false");
    pickerSearch.focus();
  }

  function closePicker() {
    // FORCE HIDE
    pickerModal.style.display = "none";
    pickerModal.classList.remove("mycrm-open");
    pickerModal.setAttribute("aria-hidden", "true");
    draftEmpIds = [];
  }

  function confirmPicker() {
    selectedEmpIds = [...draftEmpIds];
    renderChips();
    closePicker();
  }

  function renderPickerList() {
    const query = pickerSearch.value.trim().toLowerCase();
    const filtered = allEmployees.filter((emp) =>
      `${emp.name || ''} ${emp.employee_code || emp.emp_code || ''} ${emp.department || ''}`.toLowerCase().includes(query)
    );

    pickerList.textContent = "";
    pickerEmpty.hidden = filtered.length > 0;

    filtered.forEach((emp) => {
      const checked = draftEmpIds.includes(emp.id);
      const li = document.createElement("li");
      li.className = "mycrm-emp-picker-item" + (checked ? " mycrm-emp-checked" : "");
      li.innerHTML = `
        <label class="mycrm-emp-picker-row">
          <input type="checkbox" value="${emp.id}" ${checked ? "checked" : ""} data-emp-check />
          <span class="mycrm-emp-avatar">${initials(emp.name || emp.full_name)}</span>
          <span class="mycrm-emp-info">
            <strong>${escHtml(emp.name || emp.full_name)}</strong>
            <small>${escHtml(emp.employee_code || emp.emp_code || '—')} &middot; ${escHtml(emp.department || '—')}</small>
          </span>
          ${checked ? '<i class="fa-solid fa-check mycrm-emp-tick"></i>' : ""}
        </label>`;

      li.querySelector("[data-emp-check]").addEventListener("change", (e) => {
        const id = Number(e.target.value);
        if (e.target.checked) {
          if (!draftEmpIds.includes(id)) draftEmpIds.push(id);
          li.classList.add("mycrm-emp-checked");
          if (!li.querySelector(".mycrm-emp-tick")) {
            li.querySelector(".mycrm-emp-picker-row")
              .insertAdjacentHTML("beforeend", '<i class="fa-solid fa-check mycrm-emp-tick"></i>');
          }
        } else {
          draftEmpIds = draftEmpIds.filter((d) => d !== id);
          li.classList.remove("mycrm-emp-checked");
          const tick = li.querySelector(".mycrm-emp-tick");
          if (tick) tick.remove();
        }
        updatePickerCount();
      });

      pickerList.appendChild(li);
    });

    updatePickerCount();
  }

  function updatePickerCount() {
    const n = draftEmpIds.length;
    pickerCount.textContent = n === 0
      ? "None selected"
      : `${n} employee${n === 1 ? "" : "s"} selected`;
  }

  /* ══════════════════════════════════════════════════════════════════════
     CHIPS
  ══════════════════════════════════════════════════════════════════════ */

  function renderChips() {
    empChips.querySelectorAll(".mycrm-emp-chip").forEach((c) => c.remove());

    const assigned = allEmployees.filter((emp) => selectedEmpIds.includes(emp.id));
    empEmpty.hidden = assigned.length > 0;

    assigned.forEach((emp) => {
      const chip = document.createElement("span");
      chip.className = "mycrm-emp-chip";
      chip.innerHTML = `
        <span class="mycrm-emp-avatar mycrm-emp-avatar-sm">${initials(emp.name || emp.full_name)}</span>
        ${escHtml(emp.name || emp.full_name)}
        <span class="mycrm-chip-code">${escHtml(emp.employee_code || emp.emp_code || '')}</span>
        <button type="button" class="mycrm-chip-remove"
          data-remove-emp="${emp.id}" aria-label="Remove ${escHtml(emp.name || emp.full_name)}">
          <i class="fa-solid fa-xmark"></i>
        </button>`;
      empChips.appendChild(chip);
    });

    empHidden.value = selectedEmpIds.join(",");
  }

  /* ══════════════════════════════════════════════════════════════════════
     TABLE RENDERING
  ══════════════════════════════════════════════════════════════════════ */

  function renderProjects() {
    tableBody.textContent = "";

    if (!projects.length) {
      showTableMessage("No projects yet. Click Add Project to get started.");
      updateStats();
      return;
    }

    // const filteredProjects = activeFilter === "all"
    //   ? projects
    //   : projects.filter(p => (p.status || "").toLowerCase() === activeFilter);

    // const filteredProjects = activeFilter === "all"
    //     ? projects
    //     : activeFilter === "upcoming"
    //       ? projects.filter(p => {
    //           const s = (p.status || "").toLowerCase();
    //           return s === "on_hold" || s === "pending";
    //         })
    //       : projects.filter(p => (p.status || "").toLowerCase() === activeFilter);
       // project.js — renderProjects function mein
       const filteredProjects = activeFilter === "all"
          ? projects
          : activeFilter === "upcoming"
              ? projects.filter(p => (p.status || "").toLowerCase() === "on_hold")  // ← Sirf on_hold
              : projects.filter(p => (p.status || "").toLowerCase() === activeFilter);


    filteredProjects.forEach((project) => {
      const memberCount = project.team_members_count || (project.employees || []).length;
      const clientDisplay = project.client_name || "—";
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><strong>${escHtml(project.project_name)}</strong></td>
        <td>${escHtml(clientDisplay)}</td>
        <td>${memberCount}</td>
        <td>${badge(project.status)}</td>
        <td>${badge(project.priority)}</td>
        <td>
          <div class="mycrm-actions-row">
            <button class="mycrm-btn mycrm-btn-info mycrm-btn-sm"
              type="button" data-mycrm-view="${project.id}">View</button>
            <button class="mycrm-btn mycrm-btn-warning mycrm-btn-sm"
              type="button" data-mycrm-edit="${project.id}">Edit</button>
            <button class="mycrm-btn mycrm-btn-danger mycrm-btn-sm"
              type="button" data-mycrm-delete="${project.id}">Delete</button>
          </div>
        </td>`;
      tableBody.appendChild(row);
    });

    updateStats();
  }

  function updateStats() {
    const counts = {
      all: projects.length,
      in_progress: 0,
      completed: 0,
      upcoming: 0,
    };

    projects.forEach((p) => {
      const s = (p.status || "").toLowerCase();
      if (s === "in_progress") counts.in_progress++;
      else if (s === "completed") counts.completed++;
      else if (s === "on_hold") counts.upcoming++;
    });

    root.querySelector("[data-stat-all]").textContent = counts.all;
    root.querySelector("[data-stat-in_progress]").textContent = counts.in_progress;
    root.querySelector("[data-stat-completed]").textContent = counts.completed;
    root.querySelector("[data-stat-upcoming]").textContent = counts.upcoming;
  }

  function showTableMessage(msg) {
    tableBody.innerHTML = `<tr><td colspan="6" class="mycrm-table-msg">${escHtml(msg)}</td></tr>`;
  }

  /* ══════════════════════════════════════════════════════════════════════
     UTILITIES
  ══════════════════════════════════════════════════════════════════════ */

  function badge(value) {
    const key = String(value).toLowerCase();
    const type =
      key === "in_progress" ? "success" :
      key === "completed" ? "success" :
      key === "high" ? "danger" :
      key === "pending" || key === "on_hold" ? "warning" :
      key === "medium" ? "warning" : "info";
    return `<span class="mycrm-badge mycrm-badge-${type}">${escHtml(value)}</span>`;
  }

  function initials(name) {
    return String(name).split(" ").slice(0, 2).map((w) => w[0] || "").join("").toUpperCase();
  }

  function escHtml(value) {
    return String(value).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" })[c]
    );
  }

  function showToast(message) {
    const toast = root.querySelector("[data-mycrm-toast]");
    toast.textContent = message;
    toast.classList.add("mycrm-show");
    setTimeout(() => toast.classList.remove("mycrm-show"), 1800);
  }
})();




















































































// (function () {
//   "use strict";

//   /* ── Config ────────────────────────────────────────────────────────── */
//   const API_BASE = "";
//   const USE_MOCK_DATA = false;

//   /* ── DOM refs ──────────────────────────────────────────────────────── */
//   const root = document.querySelector(".mycrm-admin");
//   const tableBody = root.querySelector("[data-mycrm-table] tbody");
//   const modal = root.querySelector("[data-mycrm-modal]");
//   const modalTitle = root.querySelector("[data-mycrm-modal-title]");
//   const form = root.querySelector("[data-mycrm-form]");
//   const empChips = root.querySelector("[data-emp-chips]");
//   const empEmpty = root.querySelector("[data-emp-empty]");
//   const empHidden = root.querySelector("[data-emp-hidden]");
//   const clientSelect = root.querySelector("[data-client-select]");
//   const createdBySelect = root.querySelector("[data-createdby-select]");

//   // Employee picker sub-modal
//   const pickerModal = root.querySelector("[data-emp-picker-modal]");
//   const pickerList = root.querySelector("[data-emp-picker-list]");
//   const pickerSearch = root.querySelector("[data-emp-picker-search]");
//   const pickerEmpty = root.querySelector("[data-emp-picker-empty]");
//   const pickerLoading = root.querySelector("[data-emp-picker-loading]");
//   const pickerCount = root.querySelector("[data-emp-picker-count]");

//   // View modal
//   const viewModal = root.querySelector("[data-project-view-modal]");

//   /* ── State ─────────────────────────────────────────────────────────── */
//   let projects = [];
//   let allEmployees = [];
//   let allClients = [];
//   let allUsers = [];
//   let editId = null;
//   let selectedEmpIds = [];
//   let draftEmpIds = [];
//   let activeFilter = "all";

//   /* ── Boot ──────────────────────────────────────────────────────────── */
//   bindShell();
//   bindProjectModal();
//   bindStatCards();
//   bindEmployeePicker();
//   init();

//   async function init() {
//     await Promise.all([
//       loadDropdownOptions(),
//       loadProjects(),
//     ]);
//   }

//   /* ── Sidebar ───────────────────────────────────────────────────────── */
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

//   function bindStatCards() {
//     root.querySelectorAll(".mycrm-stat-card").forEach(card => {
//       card.addEventListener("click", () => {
//         activeFilter = card.dataset.filter;
//         renderProjects();
//       });
//     });
//   }

//   /* ══════════════════════════════════════════════════════════════════════
//      API HELPERS
//   ══════════════════════════════════════════════════════════════════════ */

//   async function apiFetch(path, options = {}) {
//     const headers = {
//       "Content-Type": "application/json",
//       "X-CSRFToken": getCsrfToken(),
//       ...options.headers,
//     };
//     const response = await fetch(`${API_BASE}${path}`, {
//       ...options,
//       headers,
//       credentials: "same-origin",
//     });
//     if (!response.ok) {
//       const text = await response.text();
//       throw new Error(`${response.status} ${response.statusText}: ${text}`);
//     }
//     return response.status === 204 ? null : response.json();
//   }

//   function getCsrfToken() {
//     const match = document.cookie.match(/csrftoken=([^;]+)/);
//     return match ? match[1] : "";
//   }

//   /* ══════════════════════════════════════════════════════════════════════
//      DROPDOWN POPULATION
//   ══════════════════════════════════════════════════════════════════════ */

//   async function loadDropdownOptions() {
//     try {
//       const [clients, users] = await Promise.all([
//         apiFetch("/dashboard/api/clients/"),
//         apiFetch("/dashboard/api/users/"),
//       ]);

//       allClients = Array.isArray(clients) ? clients : (clients.results || []);
//       allUsers = Array.isArray(users) ? users : (users.results || []);

//       // Client dropdown
//       clientSelect.innerHTML = '<option value="">Select client</option>';
//       allClients.forEach((c) => {
//         const opt = new Option(c.company_name || c.name, c.id);
//         clientSelect.appendChild(opt);
//       });

//       // Created-by dropdown
//       createdBySelect.innerHTML = '<option value="">Select</option>';
//       allUsers.forEach((u) => {
//         const opt = new Option(u.email, u.id);
//         createdBySelect.appendChild(opt);
//       });
//     } catch (err) {
//       console.error("Failed to load dropdown options:", err);
//     }
//   }

//   /* ══════════════════════════════════════════════════════════════════════
//      PROJECTS CRUD
//   ══════════════════════════════════════════════════════════════════════ */

//   async function loadProjects() {
//     showTableMessage("Loading…");
//     try {
//       const data = await apiFetch("/dashboard/api/projects/");
//       projects = Array.isArray(data) ? data : (data.results || []);
//       renderProjects();
//     } catch (err) {
//       console.error("Failed to load projects:", err);
//       showTableMessage("Failed to load projects. Please try again.");
//     }
//   }

//   async function createProject(payload) {
//     return apiFetch("/dashboard/api/projects/", {
//       method: "POST",
//       body: JSON.stringify(payload),
//     });
//   }

//   async function updateProject(id, payload) {
//     return apiFetch(`/dashboard/api/projects/${id}/`, {
//       method: "PUT",
//       body: JSON.stringify(payload),
//     });
//   }

//   async function deleteProjectById(id) {
//     await apiFetch(`/dashboard/api/projects/${id}/`, { method: "DELETE" });
//     projects = projects.filter((p) => p.id !== id);
//   }

//   /* ══════════════════════════════════════════════════════════════════════
//      PROJECT MODAL
//   ══════════════════════════════════════════════════════════════════════ */

//   function bindProjectModal() {
//     root.querySelector("[data-mycrm-add]").addEventListener("click", () => openModal());
//     root.querySelectorAll("[data-mycrm-modal-close]").forEach((btn) =>
//       btn.addEventListener("click", closeModal)
//     );
//     root.querySelectorAll("[data-close-project-view]").forEach((btn) =>
//       btn.addEventListener("click", closeProjectViewModal)
//     );
//     tableBody.addEventListener("click", handleTableClick);
//     form.addEventListener("submit", handleFormSubmit);
//   }

//   function openModal(id = null) {
//     editId = id;
//     form.reset();
//     selectedEmpIds = [];

//     if (id !== null) {
//       const project = projects.find((p) => p.id === id);
//       if (project) {
//         ["project_name", "description", "status", "priority", "budget"].forEach((key) => {
//           if (form.elements[key]) form.elements[key].value = project[key] || "";
//         });
//         if (form.elements.client) form.elements.client.value = project.client || "";
//         if (form.elements.created_by) form.elements.created_by.value = project.created_by || "";
//         selectedEmpIds = (project.employees || []).map(e => e.id);
//       }
//     }

//     renderChips();
//     modalTitle.textContent = id !== null ? "Edit Project" : "Add Project";
//     modal.classList.add("mycrm-open");
//     modal.setAttribute("aria-hidden", "false");
//   }

//   function closeModal() {
//     modal.classList.remove("mycrm-open");
//     modal.setAttribute("aria-hidden", "true");
//     editId = null;
//     selectedEmpIds = [];
//   }

//   function closeProjectViewModal() {
//     viewModal.classList.remove("mycrm-open");
//     viewModal.setAttribute("aria-hidden", "true");
//   }

//   async function handleFormSubmit(e) {
//     e.preventDefault();

//     const fd = new FormData(form);

//     const payload = {
//       project_name: fd.get("project_name") || "",
//       description: fd.get("description") || "",
//       status: fd.get("status") || "pending",
//       priority: fd.get("priority") || "medium",
//       client: fd.get("client") ? Number(fd.get("client")) : null,
//       budget: fd.get("budget") || "0",
//       created_by: fd.get("created_by") ? Number(fd.get("created_by")) : null,
//       employee_ids: selectedEmpIds.map(Number),
//     };

//     const saveBtn = form.querySelector('[type="submit"]');
//     saveBtn.disabled = true;

//     try {
//       if (editId !== null) {
//         await updateProject(editId, payload);
//         showToast("Project updated");
//       } else {
//         await createProject(payload);
//         showToast("Project added");
//       }
//       await loadProjects();
//       closeModal();
//     } catch (err) {
//       console.error("Save failed:", err);
//       showToast("Save failed — check console");
//     } finally {
//       saveBtn.disabled = false;
//     }
//   }

//   function handleTableClick(e) {
//     const viewBtn = e.target.closest("[data-mycrm-view]");
//     const editBtn = e.target.closest("[data-mycrm-edit]");
//     const deleteBtn = e.target.closest("[data-mycrm-delete]");

//     if (viewBtn) viewProject(Number(viewBtn.dataset.mycrmView));
//     if (editBtn) openModal(Number(editBtn.dataset.mycrmEdit));
//     if (deleteBtn) confirmDelete(Number(deleteBtn.dataset.mycrmDelete));
//   }

//   async function confirmDelete(id) {
//     if (!confirm("Delete this project?")) return;
//     try {
//       await deleteProjectById(id);
//       renderProjects();
//       showToast("Project deleted");
//     } catch (err) {
//       console.error("Delete failed:", err);
//       showToast("Delete failed — check console");
//     }
//   }

//   /* ══════════════════════════════════════════════════════════════════════
//      VIEW PROJECT
//   ══════════════════════════════════════════════════════════════════════ */

//   function viewProject(id) {
//     const project = projects.find((p) => p.id === id);
//     if (!project) return;

//     document.querySelector("[data-view-project-name]").textContent = project.project_name || "—";
//     document.querySelector("[data-view-project-description]").textContent = project.description || "—";
//     document.querySelector("[data-view-project-status]").textContent = project.status || "—";
//     document.querySelector("[data-view-project-priority]").textContent = project.priority || "—";
//     document.querySelector("[data-view-project-client]").textContent = project.client_name || "—";
//     document.querySelector("[data-view-project-budget]").textContent = project.budget || "—";
//     document.querySelector("[data-view-project-createdby]").textContent = project.created_by_email || "—";

//     const employeeNames = (project.employees || [])
//       .map(e => e.name || e.full_name || "")
//       .filter(Boolean)
//       .join(", ");
//     document.querySelector("[data-view-project-employees]").textContent = employeeNames || "—";

//     viewModal.classList.add("mycrm-open");
//     viewModal.setAttribute("aria-hidden", "false");
//   }

//   /* ══════════════════════════════════════════════════════════════════════
//      EMPLOYEE PICKER
//   ══════════════════════════════════════════════════════════════════════ */

//   function bindEmployeePicker() {
//     form.querySelector("[data-open-emp-picker]").addEventListener("click", openPicker);
//     pickerModal.querySelectorAll("[data-close-emp-picker]").forEach((btn) =>
//       btn.addEventListener("click", closePicker)
//     );
//     pickerModal.querySelector("[data-confirm-emp-picker]").addEventListener("click", confirmPicker);
//     pickerSearch.addEventListener("input", renderPickerList);

//     empChips.addEventListener("click", (e) => {
//       const btn = e.target.closest("[data-remove-emp]");
//       if (!btn) return;
//       selectedEmpIds = selectedEmpIds.filter((id) => id !== Number(btn.dataset.removeEmp));
//       renderChips();
//     });
//   }

//   async function openPicker() {
//     draftEmpIds = [...selectedEmpIds];
//     pickerSearch.value = "";

//     if (!allEmployees.length) {
//       pickerLoading.hidden = false;
//       pickerList.hidden = true;
//       try {
//         const data = await apiFetch("/dashboard/api/employees/");
//         allEmployees = Array.isArray(data) ? data : (data.results || []);
//       } catch (err) {
//         console.error("Failed to load employees:", err);
//         showToast("Could not load employee list");
//       } finally {
//         pickerLoading.hidden = true;
//         pickerList.hidden = false;
//       }
//     }

//     renderPickerList();
//     pickerModal.classList.add("mycrm-open");
//     pickerModal.setAttribute("aria-hidden", "false");
//     pickerSearch.focus();
//   }

//   function closePicker() {
//     pickerModal.classList.remove("mycrm-open");
//     pickerModal.setAttribute("aria-hidden", "true");
//     draftEmpIds = [];
//   }

//   function confirmPicker() {
//     selectedEmpIds = [...draftEmpIds];
//     renderChips();
//     closePicker();
//   }

//   function renderPickerList() {
//     const query = pickerSearch.value.trim().toLowerCase();
//     const filtered = allEmployees.filter((emp) =>
//       `${emp.name || ''} ${emp.employee_code || emp.emp_code || ''} ${emp.department || ''}`.toLowerCase().includes(query)
//     );

//     pickerList.textContent = "";
//     pickerEmpty.hidden = filtered.length > 0;

//     filtered.forEach((emp) => {
//       const checked = draftEmpIds.includes(emp.id);
//       const li = document.createElement("li");
//       li.className = "mycrm-emp-picker-item" + (checked ? " mycrm-emp-checked" : "");
//       li.innerHTML = `
//         <label class="mycrm-emp-picker-row">
//           <input type="checkbox" value="${emp.id}" ${checked ? "checked" : ""} data-emp-check />
//           <span class="mycrm-emp-avatar">${initials(emp.name || emp.full_name)}</span>
//           <span class="mycrm-emp-info">
//             <strong>${escHtml(emp.name || emp.full_name)}</strong>
//             <small>${escHtml(emp.employee_code || emp.emp_code || '—')} &middot; ${escHtml(emp.department || '—')}</small>
//           </span>
//           ${checked ? '<i class="fa-solid fa-check mycrm-emp-tick"></i>' : ""}
//         </label>`;

//       li.querySelector("[data-emp-check]").addEventListener("change", (e) => {
//         const id = Number(e.target.value);
//         if (e.target.checked) {
//           if (!draftEmpIds.includes(id)) draftEmpIds.push(id);
//           li.classList.add("mycrm-emp-checked");
//           if (!li.querySelector(".mycrm-emp-tick")) {
//             li.querySelector(".mycrm-emp-picker-row")
//               .insertAdjacentHTML("beforeend", '<i class="fa-solid fa-check mycrm-emp-tick"></i>');
//           }
//         } else {
//           draftEmpIds = draftEmpIds.filter((d) => d !== id);
//           li.classList.remove("mycrm-emp-checked");
//           const tick = li.querySelector(".mycrm-emp-tick");
//           if (tick) tick.remove();
//         }
//         updatePickerCount();
//       });

//       pickerList.appendChild(li);
//     });

//     updatePickerCount();
//   }

//   function updatePickerCount() {
//     const n = draftEmpIds.length;
//     pickerCount.textContent = n === 0
//       ? "None selected"
//       : `${n} employee${n === 1 ? "" : "s"} selected`;
//   }

//   /* ══════════════════════════════════════════════════════════════════════
//      CHIPS
//   ══════════════════════════════════════════════════════════════════════ */

//   function renderChips() {
//     empChips.querySelectorAll(".mycrm-emp-chip").forEach((c) => c.remove());

//     const assigned = allEmployees.filter((emp) => selectedEmpIds.includes(emp.id));
//     empEmpty.hidden = assigned.length > 0;

//     assigned.forEach((emp) => {
//       const chip = document.createElement("span");
//       chip.className = "mycrm-emp-chip";
//       chip.innerHTML = `
//         <span class="mycrm-emp-avatar mycrm-emp-avatar-sm">${initials(emp.name || emp.full_name)}</span>
//         ${escHtml(emp.name || emp.full_name)}
//         <span class="mycrm-chip-code">${escHtml(emp.employee_code || emp.emp_code || '')}</span>
//         <button type="button" class="mycrm-chip-remove"
//           data-remove-emp="${emp.id}" aria-label="Remove ${escHtml(emp.name || emp.full_name)}">
//           <i class="fa-solid fa-xmark"></i>
//         </button>`;
//       empChips.appendChild(chip);
//     });

//     empHidden.value = selectedEmpIds.join(",");
//   }

//   /* ══════════════════════════════════════════════════════════════════════
//      TABLE RENDERING
//   ══════════════════════════════════════════════════════════════════════ */

//   function renderProjects() {
//     tableBody.textContent = "";

//     if (!projects.length) {
//       showTableMessage("No projects yet. Click Add Project to get started.");
//       updateStats();
//       return;
//     }

//     const filteredProjects = activeFilter === "all"
//       ? projects
//       : projects.filter(p => (p.status || "").toLowerCase() === activeFilter);

//     filteredProjects.forEach((project) => {
//       const memberCount = project.team_members_count || (project.employees || []).length;
//       const clientDisplay = project.client_name || "—";
//       const row = document.createElement("tr");
//       row.innerHTML = `
//         <td><strong>${escHtml(project.project_name)}</strong></td>
//         <td>${escHtml(clientDisplay)}</td>
//         <td>${memberCount}</td>
//         <td>${badge(project.status)}</td>
//         <td>${badge(project.priority)}</td>
//         <td>
//           <div class="mycrm-actions-row">
//             <button class="mycrm-btn mycrm-btn-info mycrm-btn-sm"
//               type="button" data-mycrm-view="${project.id}">View</button>
//             <button class="mycrm-btn mycrm-btn-warning mycrm-btn-sm"
//               type="button" data-mycrm-edit="${project.id}">Edit</button>
//             <button class="mycrm-btn mycrm-btn-danger mycrm-btn-sm"
//               type="button" data-mycrm-delete="${project.id}">Delete</button>
//           </div>
//         </td>`;
//       tableBody.appendChild(row);
//     });

//     updateStats();
//   }

//   function updateStats() {
//     const counts = {
//       all: projects.length,
//       in_progress: 0,
//       completed: 0,
//       upcoming: 0,
//     };

//     projects.forEach((p) => {
//       const s = (p.status || "").toLowerCase();
//       if (s === "in_progress") counts.in_progress++;
//       else if (s === "completed") counts.completed++;
//       else if (s === "on_hold" || s === "pending") counts.upcoming++;
//     });

//     root.querySelector("[data-stat-all]").textContent = counts.all;
//     root.querySelector("[data-stat-in_progress]").textContent = counts.in_progress;
//     root.querySelector("[data-stat-completed]").textContent = counts.completed;
//     root.querySelector("[data-stat-upcoming]").textContent = counts.upcoming;
//   }

//   function showTableMessage(msg) {
//     tableBody.innerHTML = `<tr><td colspan="6" class="mycrm-table-msg">${escHtml(msg)}</td></tr>`;
//   }

//   /* ══════════════════════════════════════════════════════════════════════
//      UTILITIES
//   ══════════════════════════════════════════════════════════════════════ */

//   function badge(value) {
//     const key = String(value).toLowerCase();
//     const type =
//       key === "in_progress" ? "success" :
//       key === "completed" ? "success" :
//       key === "high" ? "danger" :
//       key === "pending" || key === "on_hold" ? "warning" :
//       key === "medium" ? "warning" : "info";
//     return `<span class="mycrm-badge mycrm-badge-${type}">${escHtml(value)}</span>`;
//   }

//   function initials(name) {
//     return String(name).split(" ").slice(0, 2).map((w) => w[0] || "").join("").toUpperCase();
//   }

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