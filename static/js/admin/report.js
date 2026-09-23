(function () {
  const root = document.querySelector(".mycrm-admin");
  const tableBody = root.querySelector("[data-mycrm-table] tbody");
  const modal = root.querySelector("[data-mycrm-modal]");
  const listFooter = root.querySelector("[data-mycrm-list-footer]");
  
  // ═══════════════════════════════════════════════════════════════
  // DYNAMIC: Django se injected data use karo
  // ═══════════════════════════════════════════════════════════════
  let reports = loadReports();

  bindShell();
  bindReportTabs();
  bindReportActions();
  renderReports();

  function bindShell() {
    const sidebar = root.querySelector("[data-mycrm-sidebar]");
    const backdrop = root.querySelector("[data-mycrm-sidebar-backdrop]");
    const toggle = root.querySelector("[data-mycrm-sidebar-toggle]");

    toggle.addEventListener("click", () => {
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

  function bindReportTabs() {
    root.querySelectorAll("[data-mycrm-report]").forEach((button) => {
      button.addEventListener("click", () => {
        root
          .querySelectorAll("[data-mycrm-report]")
          .forEach((tab) => tab.classList.remove("mycrm-active"));
        button.classList.add("mycrm-active");
        root.querySelector("[data-mycrm-section] h2").textContent = button.dataset.mycrmReport;
      });
    });
  }

  function bindReportActions() {
    root.querySelectorAll("[data-mycrm-modal-close]").forEach((button) => {
      button.addEventListener("click", closeModal);
    });
    tableBody.addEventListener("click", handleTableAction);
  }

  // ═══════════════════════════════════════════════════════════════
  // DYNAMIC: Django template se injected data read karo
  // ═══════════════════════════════════════════════════════════════
  function loadReports() {
    // Django template ne window.MYCRM_REPORTS mein data inject kiya hoga
    // Agar nahi mila toh empty array return karo
    if (typeof window.MYCRM_REPORTS !== "undefined" && Array.isArray(window.MYCRM_REPORTS)) {
      return window.MYCRM_REPORTS;
    }
    // Fallback: agar kuch bhi nahi mila
    console.warn("MYCRM_REPORTS not found — make sure to inject reports_data in template");
    return [];
  }

  function openViewModal(id) {
    const report = reports.find((item) => item.id === id);
    if (!report) return;

    root.querySelector("[data-mycrm-view-employee]").textContent = employeeName(report.employee);
    root.querySelector("[data-mycrm-view-subject]").textContent = report.subject || "-";
    root.querySelector("[data-mycrm-view-summary]").textContent = report.work_summary || "-";
    root.querySelector("[data-mycrm-view-date]").textContent = formatDate(report.report_date);
    root.querySelector("[data-mycrm-view-submitted]").textContent = formatDateTime(report.submitted_at);
    root.querySelector("[data-mycrm-view-updated]").textContent = formatDateTime(report.updated_at);

     // NEW: Attachment display
    const attachmentContainer = root.querySelector("[data-mycrm-view-attachment]");
    if (report.attachment) {
        const fileName = report.attachment.split('/').pop();
        attachmentContainer.innerHTML = `
            <a href="${report.attachment}" target="_blank" class="mycrm-attachment-link" download>
                <i class="fa-solid fa-download"></i>
                <span>${escapeHtml(fileName)}</span>
            </a>
        `;
    } else {
        attachmentContainer.innerHTML = '<span class="mycrm-no-attachment">No file attached</span>';
    }
    

    modal.classList.add("mycrm-open");
    modal.setAttribute("aria-hidden", "false");
  }

  function closeModal() {
    modal.classList.remove("mycrm-open");
    modal.setAttribute("aria-hidden", "true");
  }

  function handleTableAction(event) {
    const action = event.target.closest("[data-mycrm-action]");
    if (!action) return;
    const id = Number(action.dataset.reportId);
    if (action.dataset.mycrmAction === "view") openViewModal(id);
  }

  function renderReports() {
    tableBody.textContent = "";

    if (!reports.length) {
      tableBody.insertAdjacentHTML(
        "beforeend",
        '<tr class="mycrm-empty-row"><td colspan="6">No reports found</td></tr>'
      );
      listFooter.textContent = "0 reports";
      return;
    }

    reports.forEach((report) => {
      const row = document.createElement("tr");
      addHtmlCell(row, personCell(report.employee));
      addTextCell(row, formatDate(report.report_date));
      addTextCell(row, report.subject);
      addWrapCell(row, report.work_summary);
      addHtmlCell(row, attachmentCell(report.attachment));  // NEW: Attachment cell
      addHtmlCell(row, rowActions(report.id));
      tableBody.appendChild(row);
    });

    listFooter.textContent = `${reports.length} report${reports.length === 1 ? "" : "s"}`;
  }



  // NEW: Attachment cell banane ka function
function attachmentCell(attachmentUrl) {
    if (!attachmentUrl) {
        return `<span class="mycrm-no-attachment">No file</span>`;
    }
    
    const fileName = attachmentUrl.split('/').pop();
    return `
        <div class="mycrm-attachment-cell">
            <a href="${attachmentUrl}" target="_blank" class="mycrm-attachment-link" title="Download ${fileName}">
                <i class="fa-solid fa-paperclip"></i>
                <span class="mycrm-attachment-name">${escapeHtml(fileName)}</span>
            </a>
        </div>
    `;
}



  function addWrapCell(row, value) {
    const cell = document.createElement("td");
    cell.innerHTML = `
      <div class="mycrm-table-summary">
        ${escapeHtml(value || "-")}
      </div>
    `;
    row.appendChild(cell);
  }

  function addTextCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value || "-";
    row.appendChild(cell);
  }

  function addHtmlCell(row, html) {
    const cell = document.createElement("td");
    cell.insertAdjacentHTML("beforeend", html);
    row.appendChild(cell);
  }

  function employeeName(employee) {
    if (!employee) return "-";
    return `${employee.first_name} ${employee.last_name}`;
  }

  function personCell(employee) {
    return `<div class="mycrm-person-cell"><strong>${escapeHtml(employeeName(employee))}</strong></div>`;
  }

  function rowActions(id) {
    return `<div class="mycrm-action-icons"><button class="mycrm-icon-btn mycrm-view-btn" type="button" data-mycrm-action="view" data-report-id="${id}" aria-label="View report" title="View"><i class="fa-solid fa-eye"></i></button></div>`;
  }

  function formatDate(value) {
    if (!value) return "-";
    const [year, month, day] = value.split("-").map(Number);
    return new Date(year, month - 1, day).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  }

  function formatDateTime(value) {
    if (!value) return "-";
    const date = new Date(value);
    return date.toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      }[char];
    });
  }

  function showToast(message) {
    const toast = root.querySelector("[data-mycrm-toast]");
    toast.textContent = message;
    toast.classList.add("mycrm-show");
    setTimeout(() => toast.classList.remove("mycrm-show"), 1800);
  }
})();