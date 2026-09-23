(function () {
  const root = document.querySelector(".mycrm-admin");
  const tableBody = document.getElementById("desigTableBody");
  const modal = root.querySelector("[data-mycrm-modal]");
  const delModal = document.getElementById("delModal");
  const form = root.querySelector("[data-mycrm-form]");
  const modalTitle = document.getElementById("modalTitle");
  const desigIdInput = document.getElementById("desigId");
  const desigTitleInput = document.getElementById("desigTitle");
  const desigDeptInput = document.getElementById("desigDept");
  const titleError = document.getElementById("titleError");
  const deptError = document.getElementById("deptError");
  
  const csrfEl = document.querySelector("[name=csrfmiddlewaretoken]");
  if (!csrfEl) {
    console.error("❌ CSRF token nahi mila!");
    return;
  }
  const csrfToken = csrfEl.value;

  let deleteTargetId = null;

  bindShell();
  bindDesignationModal();

  function bindShell() {
    const sidebar = root.querySelector("[data-mycrm-sidebar]");
    const backdrop = root.querySelector("[data-mycrm-sidebar-backdrop]");
    
    if (!sidebar || !backdrop) return;
    
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

  function bindDesignationModal() {
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
    form.addEventListener("submit", saveDesignation);
    
    document.getElementById("cancelDel").addEventListener("click", () => {
      delModal.classList.remove("mycrm-open");
      deleteTargetId = null;
    });
    
    document.getElementById("confirmDel").addEventListener("click", deleteDesignation);
    
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

  function openModal(desigId = null, title = "", deptId = "") {
    form.reset();
    titleError.style.display = "none";
    deptError.style.display = "none";
    
    if (desigId) {
      modalTitle.textContent = "Edit Designation";
      desigIdInput.value = desigId;
      desigTitleInput.value = title;
      desigDeptInput.value = deptId;
      desigDeptInput.dispatchEvent(new Event("change", { bubbles: true }));
    } else {
      modalTitle.textContent = "Add Designation";
      desigIdInput.value = "";
      desigTitleInput.value = "";
      desigDeptInput.value = "";
      desigDeptInput.dispatchEvent(new Event("change", { bubbles: true }));
    }
    
    modal.classList.add("mycrm-open");
    modal.setAttribute("aria-hidden", "false");
    desigTitleInput.focus();
  }

  function closeModal() {
    modal.classList.remove("mycrm-open");
    modal.setAttribute("aria-hidden", "true");
    titleError.style.display = "none";
    deptError.style.display = "none";
  }

  function handleAction(e) {
    const editBtn = e.target.closest("[data-mycrm-edit]");
    const deleteBtn = e.target.closest("[data-mycrm-delete]");
    
    if (editBtn) {
      openModal(
        editBtn.dataset.mycrmEdit,
        editBtn.dataset.desigTitle,
        editBtn.dataset.desigDept
      );
    }
    
    if (deleteBtn) {
      deleteTargetId = deleteBtn.dataset.mycrmDelete;
      document.getElementById("delDesigTitle").textContent = deleteBtn.dataset.desigTitle;
      delModal.classList.add("mycrm-open");
    }
  }

  // ─── SAVE (ADD/EDIT) ───
  async function saveDesignation(e) {
    e.preventDefault();
    
    const title = desigTitleInput.value.trim();
    const deptId = desigDeptInput.value;
    
    let hasError = false;
    if (!title) {
      titleError.style.display = "block";
      hasError = true;
    } else {
      titleError.style.display = "none";
    }
    
    if (!deptId) {
      deptError.style.display = "block";
      hasError = true;
    } else {
      deptError.style.display = "none";
    }
    
    if (hasError) return;
    
    const id = desigIdInput.value;
    
    // ✅ SAHI URL FORMAT - /dashboard/ prefix + id/edit/ order
    const url = id 
      ? `/dashboard/admin/designations/${id}/edit/` 
      : `/dashboard/admin/designations/add/`;
    
    console.log("📤 Sending to:", url);
    console.log("📤 Title:", title, "Dept:", deptId);
    
    const formData = new FormData();
    formData.append("title", title);
    formData.append("department", deptId);
    
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
        body: formData,
      });
      
      console.log("📥 Status:", res.status);
      
      if (!res.ok) {
        showToast(`Server error: ${res.status}`, "error");
        return;
      }
      
      const data = await res.json();
      console.log("📥 Response:", data);
      
      if (data.success) {
        showToast(data.message);
        closeModal();
        
        if (!id) {
          // ADD
          const emptyRow = document.getElementById("emptyRow");
          if (emptyRow) emptyRow.remove();
          
          const newRow = document.createElement("tr");
          newRow.dataset.desigId = data.designation.id;
          newRow.innerHTML = `
            <td><strong class="desig-title">${escapeHtml(data.designation.title)}</strong></td>
            <td><span class="desig-dept">${escapeHtml(data.designation.department)}</span></td>
            <td>
              <div class="mycrm-actions-row">
                <button class="mycrm-btn mycrm-btn-warning mycrm-btn-sm" 
                  data-mycrm-edit="${data.designation.id}" 
                  data-desig-title="${escapeHtml(data.designation.title)}"
                  data-desig-dept="${data.designation.department_id || ''}">Edit</button>
                <button class="mycrm-btn mycrm-btn-danger mycrm-btn-sm" 
                  data-mycrm-delete="${data.designation.id}" 
                  data-desig-title="${escapeHtml(data.designation.title)}">Delete</button>
              </div>
            </td>
          `;
          tableBody.insertBefore(newRow, tableBody.firstChild);
          updateCount();
        } else {
          // EDIT
          const row = document.querySelector(`tr[data-desig-id="${id}"]`);
          if (row) {
            row.querySelector(".desig-title").textContent = data.designation.title;
            row.querySelector(".desig-dept").textContent = data.designation.department;
            const editBtn = row.querySelector("[data-mycrm-edit]");
            const delBtn = row.querySelector("[data-mycrm-delete]");
            editBtn.dataset.desigTitle = data.designation.title;
            editBtn.dataset.desigDept = data.designation.department_id || '';
            delBtn.dataset.desigTitle = data.designation.title;
          }
        }
      } else {
        showToast(data.error || "Something went wrong", "error");
      }
    } catch (err) {
      console.error("❌ Error:", err);
      showToast("Network error - Check console", "error");
    }
  }

  // ─── DELETE ───
  async function deleteDesignation() {
    if (!deleteTargetId) return;
    
    // ✅ SAHI URL FORMAT - /dashboard/ prefix + id/delete/ order
    const url = `/dashboard/admin/designations/${deleteTargetId}/delete/`;
    
    console.log("🗑️ Deleting:", url);
    
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
      });
      
      const data = await res.json();
      console.log("📥 Delete response:", data);
      
      if (data.success) {
        showToast(data.message);
        const row = document.querySelector(`tr[data-desig-id="${deleteTargetId}"]`);
        if (row) row.remove();
        
        if (tableBody.children.length === 0) {
          tableBody.innerHTML = `
            <tr id="emptyRow">
              <td colspan="3" style="text-align:center;padding:28px;color:#687385;">
                No Designations Found
              </td>
            </tr>
          `;
        }
        updateCount();
      } else {
        showToast(data.error || "Cannot delete", "error");
      }
    } catch (err) {
      console.error("❌ Delete Error:", err);
      showToast("Network error", "error");
    }
    
    delModal.classList.remove("mycrm-open");
    deleteTargetId = null;
  }

  function updateCount() {
    const count = tableBody.querySelectorAll("tr:not(#emptyRow)").length;
    document.getElementById("designationTitle").textContent = `Designation Matrix (${count})`;
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
  
  console.log("✅ designation.js loaded");
})();
