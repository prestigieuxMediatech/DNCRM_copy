/**
 * MYCRM - Invoice Items Dynamic Handler
 * HTML attributes, Lock Status, API Integration, Dynamic Renderings & Event Control
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements Reference matching provided HTML
  const selectInvoiceEl = document.querySelector('[data-invoice-select]');
  const lockBannerEl = document.querySelector('[data-lock-banner]');
  const invoiceInfoCard = document.querySelector('[data-invoice-info]');
  const infoNumberEl = document.querySelector('[data-info-number]');
  const infoClientEl = document.querySelector('[data-info-client]');
  const infoStatusEl = document.querySelector('[data-info-status]');
  const infoDateEl = document.querySelector('[data-info-date]');
  const infoTotalEl = document.querySelector('[data-info-total]');
  const itemsTableBody = document.querySelector('[data-items-table] tbody');
  const btnPdf = document.querySelector('[data-btn-pdf]');
  const btnAdd = document.querySelector('[data-mycrm-add]');

  // Modal Elements
  const modalEl = document.querySelector('[data-mycrm-modal]');
  const modalTitleEl = document.querySelector('[data-mycrm-modal-title]');
  const formEl = document.querySelector('[data-mycrm-form]');
  const selectServiceEl = document.querySelector('[data-service-select]');
  const selectProjectEl = document.querySelector('[data-project-select]');
  const inputServiceNameEl = document.querySelector('[data-service-name]');
  const inputAmountEl = document.querySelector('[data-amount]');
  const modalCloseBtns = document.querySelectorAll('[data-mycrm-modal-close]');
  const toastEl = document.querySelector('[data-mycrm-toast]');

  // Internal Application State
  let currentInvoiceId = null;
  let editingItemId = null;
  let isInvoiceLocked = false;
  let invoicesCache = [];
  let servicesCache = [];
  let projectsCache = [];

  // Helper: Toast Notifications
  const showToast = (message, isError = false) => {
    if (!toastEl) return;
    toastEl.textContent = message;
    toastEl.style.backgroundColor = isError ? '#ef4444' : '#0f172a';
    toastEl.classList.add('show');
    setTimeout(() => {
      toastEl.classList.remove('show');
    }, 3000);
  };

  // Helper: Modal Controller
  const openModal = (title = 'Add Item', itemData = null) => {
    if (isInvoiceLocked) {
      showToast('Locked Invoice: Changes allowed nahi hain.', true);
      return;
    }

    modalTitleEl.textContent = title;

    if (itemData) {
      editingItemId = itemData.id;
      selectServiceEl.value = itemData.service || '';
      selectProjectEl.value = itemData.project || '';
      inputServiceNameEl.value = itemData.service_name || '';
      inputAmountEl.value = itemData.amount || '';
    } else {
      editingItemId = null;
      formEl.reset();
    }

    modalEl.style.display = 'flex';
    modalEl.setAttribute('aria-hidden', 'false');
  };

  const closeModal = () => {
    modalEl.style.display = 'none';
    modalEl.setAttribute('aria-hidden', 'true');
    formEl.reset();
    editingItemId = null;
  };

  // Close Button / Overlay Click Event Handlers
  modalCloseBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      closeModal();
    });
  });

  // Helper: CSRF Token Generator
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + '=') {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Helper: Fetch API Utility Wrapper
  const fetchAPI = async (url, options = {}) => {
    try {
      const defaults = {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || '',
        },
      };
      const response = await fetch(url, { ...defaults, ...options });
      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      if (response.status === 204) return true;
      return await response.json();
    } catch (error) {
      console.error(`[API Error] ${url}:`, error);
      showToast('API Operation Failed', true);
      return null;
    }
  };

  // Load Dropdown Resources
  const initializeData = async () => {
    const invoices = await fetchAPI('/dashboard/api/invoices/');
    if (invoices) {
      invoicesCache = Array.isArray(invoices) ? invoices : invoices.results || [];
      selectInvoiceEl.innerHTML = '<option value="">-- Select an Invoice --</option>';
      invoicesCache.forEach((inv) => {
        const opt = document.createElement('option');
        opt.value = inv.id;
        opt.textContent = `${inv.invoice_number || '#' + inv.id} (${inv.client_name || 'Client'})`;
        selectInvoiceEl.appendChild(opt);
      });
    }





    const services = await fetchAPI('/dashboard/api/services/');
    if (services) {
      servicesCache = Array.isArray(services) ? services : services.results || [];
      selectServiceEl.innerHTML = '<option value="">-- Select Service --</option>';
      servicesCache.forEach((srv) => {
        const opt = document.createElement('option');
        opt.value = srv.id;
        opt.textContent = srv.title || srv.name;
        selectServiceEl.appendChild(opt);
      });
    }

    const projects = await fetchAPI('/dashboard/api/projects/');
    if (projects) {
      projectsCache = Array.isArray(projects) ? projects : projects.results || [];
      selectProjectEl.innerHTML = '<option value="">-- Select Project --</option>';
      projectsCache.forEach((prj) => {
        const opt = document.createElement('option');
        opt.value = prj.id;
        opt.textContent = prj.project_name || prj.name || prj.title;
        selectProjectEl.appendChild(opt);
      });
    }
  };





  // Auto-fill Service Name and Amount when Service is picked
  selectServiceEl.addEventListener('change', (e) => {
    const selectedId = parseInt(e.target.value);
    const matched = servicesCache.find((s) => s.id === selectedId);
    if (matched) {
      inputServiceNameEl.value = matched.title || matched.name || '';
      if (matched.price || matched.amount) {
        inputAmountEl.value = matched.price || matched.amount;
      }
    }
  });

  // Render Selected Invoice Details and Items
  const loadInvoiceItems = async (invoiceId) => {
    currentInvoiceId = invoiceId;

    // Fetch Full Invoice Details
    const currentInv = await fetchAPI(`/dashboard/api/invoices/${invoiceId}/`);

    if (currentInv) {
      // Lock status validation
      const st = (currentInv.status || 'draft').toLowerCase();
      isInvoiceLocked = st === 'paid' || st === 'cancelled';

      if (lockBannerEl) {
        lockBannerEl.style.display = isInvoiceLocked ? 'flex' : 'none';
      }

      if (btnAdd) {
        btnAdd.disabled = isInvoiceLocked;
      }

      // Populate Info Bar
      infoNumberEl.textContent = currentInv.invoice_number || `INV-${currentInv.id}`;
      infoClientEl.textContent = currentInv.client_name || 'N/A';
      infoStatusEl.textContent = `Status: ${currentInv.status || 'Draft'}`;
      infoDateEl.textContent = currentInv.issue_date || 'N/A';

      // Items calculation
      itemsTableBody.innerHTML = '';
      let calcTotal = 0;
      const itemsList = currentInv.items || (await fetchAPI(`/dashboard/api/invoices/${invoiceId}/items/`)) || [];

      if (itemsList && itemsList.length > 0) {
        itemsList.forEach((item, index) => {
          const amt = parseFloat(item.amount) || 0;
          calcTotal += amt;

          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${item.service_name || 'Item'}</strong></td>
            <td>${item.project_name || '-'}</td>
            <td>₹${amt.toFixed(2)}</td>
            <td>
              <button class="mycrm-btn mycrm-btn-sm" data-action="edit" data-id="${item.id}" ${isInvoiceLocked ? 'disabled' : ''}>
                <i class="fa-solid fa-pen-to-square"></i>
              </button>
              <button class="mycrm-btn mycrm-btn-sm mycrm-btn-danger" data-action="delete" data-id="${item.id}" ${isInvoiceLocked ? 'disabled' : ''}>
                <i class="fa-solid fa-trash"></i>
              </button>
            </td>
          `;
          itemsTableBody.appendChild(tr);
        });
      } else {
        itemsTableBody.innerHTML = `
          <tr>
            <td colspan="5" style="text-align: center; color: var(--mycrm-muted); padding: 2rem;">
              No invoice items added yet. Click <strong>Add Item</strong> to add one.
            </td>
          </tr>
        `;
      }

      infoTotalEl.textContent = `₹${parseFloat(currentInv.total_amount || calcTotal).toFixed(2)}`;
      invoiceInfoCard.style.display = 'block';
    }
  };





  // Event: Invoice Selection Dropdown
  selectInvoiceEl.addEventListener('change', (e) => {
    const val = e.target.value;
    if (val) {
      loadInvoiceItems(val);
    } else {
      invoiceInfoCard.style.display = 'none';
      if (lockBannerEl) lockBannerEl.style.display = 'none';
      currentInvoiceId = null;
    }
  });

  // Event: Open Add Item Modal
  btnAdd.addEventListener('click', () => {
    if (!currentInvoiceId) {
      showToast('Select an invoice first', true);
      return;
    }
    openModal('Add Item');
  });

  // Event: Form Submit (Create / Update Item)
  formEl.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (isInvoiceLocked) {
      showToast('Locked Invoice me changes submit nahi ho sakte', true);
      return;
    }

    const payload = {
      invoice: parseInt(currentInvoiceId),
      service_name: inputServiceNameEl.value,
      amount: parseFloat(inputAmountEl.value),
      service: selectServiceEl.value ? parseInt(selectServiceEl.value) : null,
      project: selectProjectEl.value ? parseInt(selectProjectEl.value) : null,
    };

    let result = null;

    if (editingItemId) {
      result = await fetchAPI(`/dashboard/api/invoice-items/${editingItemId}/update/`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
      if (result) showToast('Item updated successfully');
    } else {
      result = await fetchAPI(`/dashboard/api/invoice-items/create/`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      if (result) showToast('Item created successfully');
    }

    if (result) {
      closeModal();
      loadInvoiceItems(currentInvoiceId);
    }
  });

  // Event: Table Item Edit & Delete Actions
  itemsTableBody.addEventListener('click', async (e) => {
    const btn = e.target.closest('button[data-action]');
    if (!btn || btn.disabled || isInvoiceLocked) return;

    const action = btn.getAttribute('data-action');
    const id = btn.getAttribute('data-id');

    if (action === 'edit') {
      const item = await fetchAPI(`/dashboard/api/invoice-items/${id}/`);
      if (item) openModal('Edit Item', item);
    } else if (action === 'delete') {
      if (confirm('Are you sure you want to delete this item?')) {
        const success = await fetchAPI(`/dashboard/api/invoice-items/${id}/delete/`, {
          method: 'DELETE',
        });
        if (success) {
          showToast('Item deleted successfully');
          loadInvoiceItems(currentInvoiceId);
        }
      }
    }
  });

  // Event: Download PDF


  if (btnPdf) {
    btnPdf.addEventListener('click', () => {
      if (!currentInvoiceId) return;
      window.open(`/dashboard/api/invoices/${currentInvoiceId}/pdf/`, '_blank');
    });
  }



  // Initial Data Load
  initializeData();
});