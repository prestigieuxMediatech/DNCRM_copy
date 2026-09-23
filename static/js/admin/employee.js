(function () {

  let employees =
    JSON.parse(localStorage.getItem("mycrm_employees")) || [];

  const root      = document.querySelector(".mycrm-admin");
  const tableBody = root.querySelector("[data-mycrm-table] tbody");
  const searchInput  = root.querySelector("[data-mycrm-search]");
  const deptFilter   = root.querySelector("[data-mycrm-dept-filter]");

  bindShell();
  populateDeptFilter();
  renderEmployees();

  function bindShell() {

    const sidebar  = root.querySelector("[data-mycrm-sidebar]");
    const backdrop = root.querySelector("[data-mycrm-sidebar-backdrop]");

    root.querySelector("[data-mycrm-sidebar-toggle]")
      .addEventListener("click", () => {
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

    tableBody.addEventListener("click", handleEmployeeAction);

    // search & filter listeners
    searchInput.addEventListener("input", renderEmployees);
    deptFilter.addEventListener("change", renderEmployees);
  }

  // ── Populate dept dropdown from actual data ──────────────
  function populateDeptFilter() {
    const depts = [...new Set(
      employees.map(e => (e.department || "").trim()).filter(Boolean)
    )].sort();

    depts.forEach(d => {
      const opt = document.createElement("option");
      opt.value = d;
      opt.textContent = d;
      deptFilter.appendChild(opt);
    });
  }

  function handleEmployeeAction(event) {
    const deleteButton = event.target.closest("[data-mycrm-delete]");
    if (deleteButton) {
      deleteEmployee(Number(deleteButton.dataset.mycrmDelete));
    }
  }

  function deleteEmployee(index) {
    employees.splice(index, 1);
    localStorage.setItem("mycrm_employees", JSON.stringify(employees));

    // rebuild dept dropdown after delete
    deptFilter.innerHTML = '<option value="">All Departments</option>';
    populateDeptFilter();

    renderEmployees();
    showToast("Employee deleted");
  }

  function renderEmployees() {

    const query    = searchInput.value.trim().toLowerCase();
    const deptVal  = deptFilter.value;

    const filtered = employees.filter((emp, _) => {
      const matchName = !query ||
        (emp.name || "").toLowerCase().includes(query) ||
        (emp.emp_code || "").toLowerCase().includes(query) ||
        (emp.email || "").toLowerCase().includes(query);

      const matchDept = !deptVal ||
        (emp.department || "").trim() === deptVal;

      return matchName && matchDept;
    });

    tableBody.textContent = "";

    if (filtered.length === 0) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 8;
      td.textContent = "No employees found.";
      td.style.cssText = "text-align:center;padding:28px;color:#687385;";
      tr.appendChild(td);
      tableBody.appendChild(tr);
      return;
    }

    filtered.forEach((employee) => {
      // use real index from employees array for edit/delete/view
      const realIndex = employees.indexOf(employee);

      const row = document.createElement("tr");

      addTextCell(row, employee.emp_code || "-");
      addHtmlCell(row, personCell(employee.name || "-"));
      addTextCell(row, employee.email || "-");
      addTextCell(row, employee.department || "-");
      addTextCell(row, employee.designation || "-");
      addTextCell(row, employee.salary || "-");
      addHtmlCell(row, badge(employee.status || "active"));
      addHtmlCell(row, rowActions(realIndex));

      tableBody.appendChild(row);
    });
  }

  function addTextCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value;
    row.appendChild(cell);
  }

  function addHtmlCell(row, html) {
    const cell = document.createElement("td");
    cell.insertAdjacentHTML("beforeend", html);
    row.appendChild(cell);
  }

  function personCell(name) {
    return `
      <div class="mycrm-person-cell">
        <strong>${name}</strong>
      </div>
    `;
  }

  function badge(value) {
    const type = value.toLowerCase() === "active" ? "success" : "warning";
    return `<span class="mycrm-badge mycrm-badge-${type}">${value}</span>`;
  }

  function rowActions(index) {
    return `
      <div class="mycrm-actions-row">
        <a href="viewEmp.html?index=${index}">
          <button class="mycrm-btn mycrm-btn-info mycrm-btn-sm" type="button">View</button>
        </a>
        <a href="editEmp.html?index=${index}">
          <button class="mycrm-btn mycrm-btn-warning mycrm-btn-sm" type="button">Edit</button>
        </a>
        <button class="mycrm-btn mycrm-btn-danger mycrm-btn-sm" type="button"
          data-mycrm-delete="${index}">Delete</button>
      </div>
    `;
  }

  function showToast(message) {
    const toast = root.querySelector("[data-mycrm-toast]");
    toast.textContent = message;
    toast.classList.add("mycrm-show");
    setTimeout(() => toast.classList.remove("mycrm-show"), 1800);
  }

})();