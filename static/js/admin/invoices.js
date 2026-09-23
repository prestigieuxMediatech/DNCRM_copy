document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.querySelector("[data-mycrm-table] tbody");
  const createEditModal = document.querySelector("[data-mycrm-modal]");
  const viewModal = document.querySelector("[data-view-modal]");
  const invoiceForm = document.querySelector("[data-mycrm-form]");
  const clientSelect = document.querySelector("[data-client-select]");
  const statusSelect = document.querySelector("[data-status-select]");
  const invoiceNumberInput = document.querySelector("[data-invoice-number]");
  const modalTitle = document.querySelector("[data-mycrm-modal-title]");
  const addBtn = document.querySelector("[data-mycrm-add]");
  const toast = document.querySelector("[data-mycrm-toast]");

  const searchInput = document.getElementById("invoiceSearch");
  const statusFilterSelect = document.getElementById("statusFilter");
  const toggleDeletedBtn = document.getElementById("toggleDeletedBtn");
  const tableHeaderTitle = document.getElementById("tableHeaderTitle");
  const tableHeadRow = document.getElementById("tableHeadRow");

  let activeInvoiceId = null;
  let showingDeleted = false;

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie("csrftoken");

  function getStatusBadgeHTML(status) {
    const st = (status || "draft").toLowerCase();
    let badgeClass = "badge-draft";
    let label = "Draft";

    if (st === "sent") {
      badgeClass = "badge-sent";
      label = "Sent";
    } else if (st === "paid") {
      badgeClass = "badge-paid";
      label = "Paid";
    } else if (st === "cancelled") {
      badgeClass = "badge-cancelled";
      label = "Cancelled";
    }

    return `<span class="mycrm-badge ${badgeClass}">${label}</span>`;
  }

  function parseNotesToHTML(rawNotes) {
    if (!rawNotes || rawNotes.trim() === "" || rawNotes === "—") {
      return "<em>No notes or terms provided.</em>";
    }

    const cleanNotes = rawNotes.trim();
    const hasBullets = cleanNotes.includes("•") || cleanNotes.includes("- ") || cleanNotes.includes("* ");
    const hasNewlines = cleanNotes.includes("\n");

    if (hasBullets || hasNewlines) {
      const lines = cleanNotes.split(/\r?\n/);
      let htmlList = '<ul class="mycrm-view-notes-list">';
      let validItemsCount = 0;

      lines.forEach((line) => {
        const trimmedLine = line.trim();
        if (trimmedLine.length > 0) {
          const cleanText = trimmedLine.replace(/^[•\-\*]\s*/, "");
          htmlList += `<li>${cleanText}</li>`;
          validItemsCount++;
        }
      });

      htmlList += "</ul>";
      return validItemsCount > 0 ? htmlList : cleanNotes;
    }

    return cleanNotes;
  }

  function showToast(message, isError = false) {
    if (!toast) return;
    toast.textContent = message;
    toast.style.background = isError ? "#ef4444" : "#334155";
    toast.style.display = "block";
    setTimeout(() => {
      toast.style.display = "none";
    }, 3500);
  }

  function openModal(modal) {
    if (modal) {
      modal.style.display = "flex";
      modal.setAttribute("aria-hidden", "false");
    }
  }

  function closeModal(modal) {
    if (modal) {
      modal.style.display = "none";
      modal.setAttribute("aria-hidden", "true");
    }
  }

  document.querySelectorAll("[data-mycrm-modal-close]").forEach((btn) => {
    btn.addEventListener("click", () => closeModal(createEditModal));
  });

  document.querySelectorAll("[data-close-view]").forEach((btn) => {
    btn.addEventListener("click", () => closeModal(viewModal));
  });

  if (addBtn) {
    addBtn.addEventListener("click", () => {
      activeInvoiceId = null;
      if (invoiceForm) invoiceForm.reset();
      if (modalTitle) modalTitle.textContent = "Create Invoice";
      if (statusSelect) statusSelect.value = "draft";
      openModal(createEditModal);
    });
  }

  async function fetchClients() {
    if (!clientSelect) return;
    try {
      const res = await fetch("/dashboard/api/clients/", {
        headers: { Accept: "application/json", "X-CSRFToken": csrftoken },
      });
      if (!res.ok) throw new Error(`Status: ${res.status}`);
      const data = await res.json();
      const clientsList = Array.isArray(data) ? data : data.results || [];

      clientSelect.innerHTML = '<option value="">Select client</option>';
      clientsList.forEach((c) => {
        const clientName = c.client_name || c.name || "Client";
        const companyName = c.company_name ? ` (${c.company_name})` : "";
        clientSelect.innerHTML += `<option value="${c.id}">${clientName}${companyName}</option>`;
      });
    } catch (err) {
      console.error("Error loading clients:", err);
    }
  }

  async function loadInvoices() {
    if (!tableBody) return;
    try {
      const query = searchInput ? searchInput.value.trim() : "";
      const statusVal = statusFilterSelect ? statusFilterSelect.value : "";
      
      const url = `/dashboard/api/invoices/?show_deleted=${showingDeleted}&search=${encodeURIComponent(query)}&status=${encodeURIComponent(statusVal)}`;
      
      const response = await fetch(url, {
        headers: { Accept: "application/json", "X-CSRFToken": csrftoken },
      });

      if (!response.ok) throw new Error(`Server status ${response.status}`);

      const invoices = await response.json();
      tableBody.innerHTML = "";

      const invoicesList = Array.isArray(invoices) ? invoices : invoices.results || [];

      if (showingDeleted) {
        tableHeaderTitle.textContent = "Deleted Invoices History";
        tableHeadRow.innerHTML = `
          <th>Invoice #</th>
          <th>Client</th>
          <th>Status</th>
          <th>Total</th>
          <th>Deleted At</th>
          <th>Deleted By</th>
        `;
      } else {
        tableHeaderTitle.textContent = "All Active Invoices";
        tableHeadRow.innerHTML = `
          <th>Invoice</th>
          <th>Client</th>
          <th>Status</th>
          <th>Total</th>
          <th>Date</th>
          <th>Actions</th>
        `;
      }

      if (invoicesList.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 2rem; color: #64748b;">No Invoices Found</td></tr>`;
        return;
      }

      invoicesList.forEach((inv) => {
        const tr = document.createElement("tr");

        if (showingDeleted) {
          const deletedDate = inv.deleted_at ? new Date(inv.deleted_at).toLocaleDateString() : "—";
          tr.innerHTML = `
            <td><strong>${inv.invoice_number || "#" + inv.id}</strong></td>
            <td>${inv.client_name || "N/A"}</td>
            <td>${getStatusBadgeHTML(inv.status)}</td>
            <td>₹${parseFloat(inv.total_amount || 0).toFixed(2)}</td>
            <td>${deletedDate}</td>
            <td>${inv.deleted_by_name || "System/Admin"}</td>
          `;
        } else {
          tr.innerHTML = `
            <td><strong>${inv.invoice_number || "#" + inv.id}</strong></td>
            <td>${inv.client_name || "N/A"}</td>
            <td>${getStatusBadgeHTML(inv.status)}</td>
            <td>₹${parseFloat(inv.total_amount || 0).toFixed(2)}</td>
            <td>${inv.issue_date || "—"}</td>
            <td class="action-btns">
              <button class="action-btn view" data-id="${inv.id}" title="View Details">
                <i class="fa-solid fa-eye"></i>
              </button>
              <button class="action-btn edit" data-id="${inv.id}" title="Edit Invoice">
                <i class="fa-solid fa-pen-to-square"></i>
              </button>
              <button class="action-btn delete" data-id="${inv.id}" title="Delete Invoice">
                <i class="fa-solid fa-trash"></i>
              </button>
              <a href="/dashboard/api/invoices/${inv.id}/pdf/" target="_blank" class="action-btn pdf" title="Download PDF">
                <i class="fa-solid fa-file-pdf"></i>
              </a>
            </td>
          `;
        }
        tableBody.appendChild(tr);
      });
    } catch (err) {
      console.error("Fetch Error:", err);
      showToast("Error loading invoices: " + err.message, true);
    }
  }

  // Filter & Search Events
  let debounceTimer;
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(loadInvoices, 300);
    });
  }

  if (statusFilterSelect) {
    statusFilterSelect.addEventListener("change", loadInvoices);
  }

  if (toggleDeletedBtn) {
    toggleDeletedBtn.addEventListener("click", () => {
      showingDeleted = !showingDeleted;
      if (showingDeleted) {
        toggleDeletedBtn.innerHTML = `<i class="fa-solid fa-list"></i> Active Invoices List`;
        toggleDeletedBtn.classList.replace("mycrm-btn-secondary", "mycrm-btn-primary");
      } else {
        toggleDeletedBtn.innerHTML = `<i class="fa-solid fa-clock-rotate-left"></i> Deleted Invoices History`;
        toggleDeletedBtn.classList.replace("mycrm-btn-primary", "mycrm-btn-secondary");
      }
      loadInvoices();
    });
  }

  if (invoiceForm) {
    invoiceForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(invoiceForm);
      const data = Object.fromEntries(formData.entries());

      const isEdit = activeInvoiceId !== null;
      const url = isEdit
        ? `/dashboard/api/invoices/${activeInvoiceId}/update/`
        : `/dashboard/api/invoices/create/`;
      const method = isEdit ? "PUT" : "POST";

      try {
        const res = await fetch(url, {
          method: method,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
          },
          body: JSON.stringify(data),
        });

        if (res.ok) {
          showToast(isEdit ? "Invoice updated successfully" : "Invoice created successfully");
          closeModal(createEditModal);
          loadInvoices();
        } else {
          const errors = await res.json();
          let errorMsg = "Validation Error";
          if (errors.invoice_number) {
            errorMsg = Array.isArray(errors.invoice_number) ? errors.invoice_number[0] : errors.invoice_number;
          } else if (errors.detail) {
            errorMsg = errors.detail;
          } else {
            errorMsg = JSON.stringify(errors);
          }
          showToast(errorMsg, true);
        }
      } catch (err) {
        showToast("Network Error", true);
      }
    });
  }

  if (tableBody) {
    tableBody.addEventListener("click", async (e) => {
      const targetBtn = e.target.closest(".action-btn");
      if (!targetBtn) return;

      const id = targetBtn.dataset.id;

      if (targetBtn.classList.contains("view")) {
        try {
          const res = await fetch(`/dashboard/api/invoices/${id}/`);
          if (res.ok) {
            const inv = await res.json();
            document.querySelector("[data-view-number]").textContent = inv.invoice_number || "#" + inv.id;
            document.querySelector("[data-view-client]").textContent = inv.client_name || "N/A";
            document.querySelector("[data-view-status]").innerHTML = getStatusBadgeHTML(inv.status);
            document.querySelector("[data-view-date]").textContent = inv.issue_date || "—";
            document.querySelector("[data-view-total]").textContent = "₹" + parseFloat(inv.total_amount || 0).toFixed(2);
            
            const notesNode = document.querySelector("[data-view-notes]");
            if (notesNode) notesNode.innerHTML = parseNotesToHTML(inv.notes);

            openModal(viewModal);
          }
        } catch (err) {
          showToast("Unable to fetch invoice details", true);
        }
      }

      if (targetBtn.classList.contains("edit")) {
        try {
          const res = await fetch(`/dashboard/api/invoices/${id}/`);
          if (res.ok) {
            const inv = await res.json();

            activeInvoiceId = id;
            if (modalTitle) modalTitle.textContent = "Edit Invoice";

            if (invoiceNumberInput) invoiceNumberInput.value = inv.invoice_number || "";
            if (invoiceForm.elements["client"]) invoiceForm.elements["client"].value = inv.client || "";
            if (invoiceForm.elements["issue_date"]) invoiceForm.elements["issue_date"].value = inv.issue_date || "";
            if (invoiceForm.elements["status"]) invoiceForm.elements["status"].value = inv.status || "draft";
            if (invoiceForm.elements["notes"]) invoiceForm.elements["notes"].value = inv.notes || "";

            openModal(createEditModal);
          }
        } catch (err) {
          showToast("Error fetching invoice data", true);
        }
      }

      if (targetBtn.classList.contains("delete")) {
        if (confirm("Are you sure you want to delete this invoice?")) {
          try {
            const res = await fetch(`/dashboard/api/invoices/${id}/delete/`, {
              method: "DELETE",
              headers: { "X-CSRFToken": csrftoken },
            });
            if (res.ok) {
              showToast("Invoice marked as deleted");
              loadInvoices();
            } else {
              const errData = await res.json();
              showToast(errData.detail || "Failed to delete invoice", true);
            }
          } catch (err) {
            showToast("Network Error", true);
          }
        }
      }
    });
  }

  fetchClients();
  loadInvoices();
});


