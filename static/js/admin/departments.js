(function () {
  const root = document.querySelector(".mycrm-admin");
  const tableBody = document.getElementById("deptTableBody");
  const modal = root.querySelector("[data-mycrm-modal]");
  const delModal = document.getElementById("delModal");
  const form = root.querySelector("[data-mycrm-form]");
  const modalTitle = document.getElementById("modalTitle");
  const deptIdInput = document.getElementById("deptId");
  const deptNameInput = document.getElementById("deptName");
  const nameError = document.getElementById("nameError");
  
  const csrfEl = document.querySelector("[name=csrfmiddlewaretoken]");
  if (!csrfEl) {
    console.error("❌ CSRF token nahi mila!");
    return;
  }
  const csrfToken = csrfEl.value;

  let deleteTargetId = null;

  bindShell();
  bindDepartmentModal();

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
    
    if (backdrop) {
      backdrop.addEventListener("click", () => {
        sidebar.classList.remove("mycrm-open");
        backdrop.classList.remove("mycrm-open");
      });
    }
  }

  function bindDepartmentModal() {
    const addBtn = root.querySelector("[data-mycrm-add]");
    if (!addBtn) {
      console.error("❌ Add button nahi mila!");
      return;
    }
    addBtn.addEventListener("click", () => openModal());
    
    root.querySelectorAll("[data-mycrm-modal-close]").forEach((btn) => {
      btn.addEventListener("click", closeModal);
    });
    
    tableBody.addEventListener("click", handleAction);
    form.addEventListener("submit", saveDepartment);
    
    document.getElementById("cancelDel").addEventListener("click", () => {
      delModal.classList.remove("mycrm-open");
      deleteTargetId = null;
    });
    
    document.getElementById("confirmDel").addEventListener("click", deleteDepartment);
    
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeModal();
    });
    delModal.addEventListener("click", (e) => {
      if (e.target === delModal) {
        delModal.classList.remove("mycrm-open");
        deleteTargetId = null;
      }
    });
  }

  function openModal(deptId = null, deptName = "") {
    form.reset();
    nameError.style.display = "none";
    
    if (deptId) {
      modalTitle.textContent = "Edit Department";
      deptIdInput.value = deptId;
      deptNameInput.value = deptName;
    } else {
      modalTitle.textContent = "Add Department";
      deptIdInput.value = "";
      deptNameInput.value = "";
    }
    
    modal.classList.add("mycrm-open");
    modal.setAttribute("aria-hidden", "false");
    deptNameInput.focus();
  }

  function closeModal() {
    modal.classList.remove("mycrm-open");
    modal.setAttribute("aria-hidden", "true");
    nameError.style.display = "none";
  }

  function handleAction(e) {
    const editBtn = e.target.closest("[data-mycrm-edit]");
    const deleteBtn = e.target.closest("[data-mycrm-delete]");
    
    if (editBtn) {
      openModal(editBtn.dataset.mycrmEdit, editBtn.dataset.deptName);
    }
    
    if (deleteBtn) {
      deleteTargetId = deleteBtn.dataset.mycrmDelete;
      document.getElementById("delDeptName").textContent = deleteBtn.dataset.deptName;
      delModal.classList.add("mycrm-open");
    }
  }

  // ─── SAVE (ADD/EDIT) ───
  async function saveDepartment(e) {
    e.preventDefault();
    
    const name = deptNameInput.value.trim();
    if (!name) {
      nameError.style.display = "block";
      return;
    }
    nameError.style.display = "none";
    
    const id = deptIdInput.value;
    // ✅ FIXED URL - /dashboard/ prefix add kiya
    const url = id 
      ? `/dashboard/admin/departments/${id}/edit/` 
      : "/dashboard/admin/departments/add/";
    
    const formData = new FormData();
    formData.append("name", name);
    
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
        body: formData,
      });
      
      const data = await res.json();
      
      if (data.success) {
        showToast(data.message);
        closeModal();
        
        if (!id) {
          // ADD
          const emptyRow = document.getElementById("emptyRow");
          if (emptyRow) emptyRow.remove();
          
          const newRow = document.createElement("tr");
          newRow.dataset.deptId = data.department.id;
          newRow.innerHTML = `
            <td><strong class="dept-name">${escapeHtml(data.department.name)}</strong></td>
            <td>
              <div class="mycrm-actions-row">
                <button class="mycrm-btn mycrm-btn-warning mycrm-btn-sm" 
                  data-mycrm-edit="${data.department.id}" 
                  data-dept-name="${escapeHtml(data.department.name)}">Edit</button>
                <button class="mycrm-btn mycrm-btn-danger mycrm-btn-sm" 
                  data-mycrm-delete="${data.department.id}" 
                  data-dept-name="${escapeHtml(data.department.name)}">Delete</button>
              </div>
            </td>
          `;
          tableBody.insertBefore(newRow, tableBody.firstChild);
          updateCount();
        } else {
          // EDIT
          const row = document.querySelector(`tr[data-dept-id="${id}"]`);
          if (row) {
            row.querySelector(".dept-name").textContent = data.department.name;
            row.querySelector("[data-mycrm-edit]").dataset.deptName = data.department.name;
            row.querySelector("[data-mycrm-delete]").dataset.deptName = data.department.name;
          }
        }
      } else {
        showToast(data.error || "Something went wrong", "error");
      }
    } catch (err) {
      console.error("Error:", err);
      showToast("Network error", "error");
    }
  }

  // ─── DELETE ───
  async function deleteDepartment() {
    if (!deleteTargetId) return;
    
    // ✅ FIXED URL - /dashboard/ prefix add kiya
    const url = `/dashboard/admin/departments/${deleteTargetId}/delete/`;
    
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
      });
      
      const data = await res.json();
      
      if (data.success) {
        showToast(data.message);
        const row = document.querySelector(`tr[data-dept-id="${deleteTargetId}"]`);
        if (row) row.remove();
        
        if (tableBody.children.length === 0) {
          tableBody.innerHTML = `
            <tr id="emptyRow">
              <td colspan="2" style="text-align:center;padding:28px;color:#687385;">
                No Departments Found
              </td>
            </tr>
          `;
        }
        updateCount();
      } else {
        showToast(data.error || "Cannot delete", "error");
      }
    } catch (err) {
      console.error("Delete Error:", err);
      showToast("Network error", "error");
    }
    
    delModal.classList.remove("mycrm-open");
    deleteTargetId = null;
  }

  function updateCount() {
    const count = tableBody.querySelectorAll("tr:not(#emptyRow)").length;
    document.getElementById("departmentTitle").textContent = `Department List (${count})`;
  }

  function showToast(message, type = "success") {
    const toast = root.querySelector("[data-mycrm-toast]");
    toast.textContent = message;
    toast.classList.add("mycrm-show");
    setTimeout(() => toast.classList.remove("mycrm-show"), 2000);
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
})();