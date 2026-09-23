(function () {
  const root = document.querySelector(".mycrm-admin");
  const tableBody = root.querySelector("[data-mycrm-table] tbody");

  const statusFilter = root.querySelector("[data-mycrm-status-filter]");
  const listFooter = root.querySelector("[data-mycrm-list-footer]");
  let leaves = [];

  function loadLeaves() {
    const scriptTag = document.getElementById("leaves-data");
    if (scriptTag) {
      try {
        leaves = JSON.parse(scriptTag.textContent);
      } catch (e) {
        console.error("Failed to parse leaves data:", e);
        leaves = [];
      }
    }
  }

  bindShell();
  bindLeaveActions();
  loadLeaves();
  renderLeaves();

  function bindShell() {
    const sidebar = root.querySelector("[data-mycrm-sidebar]");
    const backdrop = root.querySelector("[data-mycrm-sidebar-backdrop]");
    const toggle = root.querySelector("[data-mycrm-sidebar-toggle]");

    if (!toggle) return;

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

  function bindLeaveActions() {
    tableBody.addEventListener("click", handleTableAction);
    statusFilter.addEventListener("change", renderLeaves);
  }

  function handleTableAction(event) {
    const action = event.target.closest("[data-mycrm-action]");
    if (!action) return;
    const id = Number(action.dataset.leaveId);
    const type = action.dataset.mycrmAction;

    if (type === "approve") updateStatus(id, "approved");
    if (type === "reject") updateStatus(id, "rejected");
  }

  async function updateStatus(id, status) {
    const btn = tableBody.querySelector(`[data-leave-id="${id}"][data-mycrm-action]`);
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Processing...";
    }

    try {
      const response = await fetch(window.MYCRM_URLS.updateLeaveStatus, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": window.MYCRM_CSRF_TOKEN,
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ leave_id: id, status: status }),
      });

      const data = await response.json();

      if (data.success) {
        leaves = leaves.map((leave) => {
          if (leave.id !== id) return leave;
          return {
            ...leave,
            status: data.leave.status,
            reviewed_by: data.leave.reviewed_by,
            reviewed_at: data.leave.reviewed_at,
          };
        });

        renderLeaves();
        showToast(`Leave ${statusLabel(status).toLowerCase()}`);
      } else {
        showToast(data.error || "Failed to update status");
        renderLeaves();
      }
    } catch (error) {
      console.error("Error updating leave status:", error);
      showToast("Network error. Please try again.");
      renderLeaves();
    }
  }

  function renderLeaves() {
    const visible = filteredLeaves();
    tableBody.textContent = "";

    if (!visible.length) {
      tableBody.insertAdjacentHTML(
        "beforeend",
        '<tr class="mycrm-empty-row"><td colspan="7">No leave requests found</td></tr>',
      );
    }

    visible.forEach((leave) => {
      const row = document.createElement("tr");
      addHtmlCell(row, personCell(leave.employee));
      addTextCell(row, leaveTypeLabel(leave.leave_type));
      addTextCell(row, formatDate(leave.start_date));
      addTextCell(row, formatDate(leave.end_date));
      addReasonCell(row, leave.reason);
      addHtmlCell(row, badge(leave.status));
      addHtmlCell(row, rowActions(leave));
      tableBody.appendChild(row);
    });

    listFooter.textContent = `${visible.length} leave request${visible.length === 1 ? "" : "s"}`;
  }

  function filteredLeaves() {
    return leaves.filter((leave) => {
      const selected = statusFilter.value;
      return selected === "All" || leave.status === selected.toLowerCase();
    });
  }

  function addTextCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value || "-";
    row.appendChild(cell);
  }

  function addReasonCell(row, value) {
    const cell = document.createElement("td");
    cell.className = "mycrm-reason-cell";
    cell.textContent = value || "-";
    row.appendChild(cell);
  }

  function addHtmlCell(row, html) {
    const cell = document.createElement("td");
    cell.insertAdjacentHTML("beforeend", html);
    row.appendChild(cell);
  }

  function personCell(employee) {
    const fullName = `${employee.first_name} ${employee.last_name}`;
    const initials = `${employee.first_name[0] || ""}${employee.last_name[0] || ""}`.toUpperCase();
    return `<div class="mycrm-person-cell"><span class="mycrm-avatar">${initials}</span><strong>${escapeHtml(fullName)}</strong></div>`;
  }

  function leaveTypeLabel(value) {
    const labels = {
      sick_leave: "Sick Leave",
      casual_leave: "Casual Leave",
      emergency_leave: "Emergency Leave",
    };
    return labels[value] || value;
  }

  function statusLabel(status) {
    const labels = {
      pending: "Pending",
      approved: "Approved",
      rejected: "Rejected",
    };
    return labels[status] || status;
  }

  function badge(status) {
    const type =
      status === "approved"
        ? "success"
        : status === "rejected"
          ? "danger"
          : "warning";
    return `<span class="mycrm-badge mycrm-badge-${type}">${escapeHtml(statusLabel(status))}</span>`;
  }

  function rowActions(leave) {
    if (leave.status === "pending") {
      return `<div class="mycrm-action-icons"><button class="mycrm-approve-btn" type="button" data-mycrm-action="approve" data-leave-id="${leave.id}" aria-label="Approve leave" title="Approve">Approve</button><button class="mycrm-reject-btn" type="button" data-mycrm-action="reject" data-leave-id="${leave.id}" aria-label="Reject leave" title="Reject">Reject</button></div>`;
    }
    const by = escapeHtml(leave.reviewed_by || "Admin");
    const action = leave.status === "approved" ? "Approved" : "Rejected";
    return `<div class="mycrm-reviewed-info">${action} by ${by}</div>`;
  }

  function formatDate(value) {
    if (!value) return "";
    const [year, month, day] = value.split("-").map(Number);
    return new Date(year, month - 1, day).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
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