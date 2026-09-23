/**
 * punch_sessions.js
 *
 * Read-only punch sessions list - CURRENT DAY ONLY.
 * Shows only employees who punched in today.
 */

(function () {
  /* ── Config ──────────────────────────────────────────────────────────── */
  const API_BASE = "";
  const API_ENDPOINT = "/dashboard/api/punch-sessions/";
  const USE_SEED_DATA = false;

  /* ── DOM refs ─────────────────────────────────────────────────────────── */
  const root = document.querySelector(".mycrm-admin");
  if (!root) return;
  const tableBody = root.querySelector("[data-mycrm-table] tbody");
  const listFooter = root.querySelector("[data-mycrm-list-footer]");
  if (!tableBody || !listFooter) return; 

  /* ── State ────────────────────────────────────────────────────────────── */
  let sessions = [];
  let isLoading = false;

  /* ── Boot ─────────────────────────────────────────────────────────────── */
  bindShell();
  loadData();

  /* ── Sidebar wiring ───────────────────────────────────────────────────── */
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

  /* ── Data loading ─────────────────────────────────────────────────────── */
  async function loadData() {
    await fetchSessions();
  }

  async function fetchSessions() {
    if (isLoading) return;
    isLoading = true;
    showTableMessage("Loading…");

    try {
      const response = await fetch(`${API_BASE}${API_ENDPOINT}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        credentials: "same-origin"
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data = await response.json();
      sessions = Array.isArray(data) ? data : (data.results || []);
      renderSessions();
    } catch (error) {
      console.error("Failed to fetch punch sessions:", error);
      showTableMessage("Failed to load punch sessions. Please try again.");
    } finally {
      isLoading = false;
    }
  }

  /* ── Render ───────────────────────────────────────────────────────────── */
  function renderSessions() {
    const visible = sessions; // No filter needed - backend already filtered by today
    tableBody.textContent = "";

    if (!visible.length) {
      showTableMessage("No employees punched in today");
      listFooter.textContent = "0 punch sessions today";
      return;
    }

    visible.forEach((session) => {
      const row = document.createElement("tr");
      addHtmlCell(row, `<strong>${escapeHtml(session.employee)}</strong>`);
      addTextCell(row, session.emp_code || "—");
      addTextCell(row, session.department || "—");
      addTextCell(row, formatDate(session.date));
      addTextCell(row, formatDateTime(session.punch_in_date, session.punch_in_time));
      addTextCell(row, formatDateTime(session.punch_out_date, session.punch_out_time) || "—");
      addTextCell(row, decimalHours(session) + " hrs");
      addHtmlCell(row, badge(session.status));
      tableBody.appendChild(row);
    });

    listFooter.textContent = `${visible.length} punch session${visible.length === 1 ? "" : "s"} today`;
  }

  /* ── Table helpers ────────────────────────────────────────────────────── */
  function showTableMessage(message) {
    tableBody.innerHTML = `<tr class="mycrm-empty-row"><td colspan="8">${escapeHtml(message)}</td></tr>`;
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

  // function badge(status) {
  //   if (!status) return `<span class="mycrm-badge mycrm-badge-warning">—</span>`;
  //   const type =
  //     status === "Active" ? "success" :
  //     status === "Completed" ? "info" : "warning";
  //   return `<span class="mycrm-badge mycrm-badge-${type}">${escapeHtml(status)}</span>`;
  // }


  function badge(status) {
    if (!status) return `<span class="mycrm-badge mycrm-badge-warning">—</span>`;
    const s = String(status).toLowerCase();  // ← normalize karo
    const type =
      s === "active" ? "success" :
      s === "completed" ? "info" : "warning";
    return `<span class="mycrm-badge mycrm-badge-${type}">${escapeHtml(status)}</span>`;
}

  /* ── Formatting helpers ───────────────────────────────────────────────── */
     
    function decimalHours(session) {
        const status = String(session.status || "").toLowerCase();
        if (status === "active") {
              return "In Progress";
        }
        const hours = Number(session.total_hours || 0);
        return isNaN(hours) ? "0.00" : hours.toFixed(2);
        // return hours.toFixed(2);
}
//   function decimalHours(session) {
//     const hours = Number(session.total_hours || 0);
//     const minutes = Number(session.total_minutes || 0);
//     return (hours + minutes / 60).toFixed(2);
//   }

  function formatDate(value) {
    if (!value) return "";
    return parseDate(value).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric"
    });
  }

  // function formatDateTime(date, time) {
  //   if (!date || !time) return "";
  //   return `${formatDate(date)}, ${formatTime(time)}`;
  // }







  function formatDateTime(date, time) {
    if (!date || !time) return "";
    return `${formatDate(date)}, ${time}`;  // Direct time use karo!
}









  // function formatTime(time) {
  //   const [hours, minutes] = time.split(":").map(Number);
  //   return new Date(2000, 0, 1, hours, minutes).toLocaleTimeString("en-IN", {
  //     hour: "numeric",
  //     minute: "2-digit"
  //   });
  // }



//   function formatTime(time) {
//     // "10:23 AM" ya "05:10 PM" handle kare
//     const match = time.match(/(\d+):(\d+)\s*(AM|PM)/i);
//     if (!match) return time;
    
//     let [, hours, minutes, period] = match;
//     hours = parseInt(hours);
//     minutes = parseInt(minutes);
//     period = period.toUpperCase();
    
//     // 24-hour convert karo taaki Date object bane
//     if (period === "PM" && hours !== 12) hours += 12;
//     if (period === "AM" && hours === 12) hours = 0;
    
//     // Wapas 12-hour format mein return karo jo user dekhna chahta hai
//     return new Date(2000, 0, 1, hours, minutes).toLocaleTimeString("en-IN", {
//         hour: "numeric",
//         minute: "2-digit",
//         hour12: true  // ← Ye ensure karega "AM/PM" dikhe
//     });
// }





  function parseDate(value) {
    const [year, month, day] = value.split("-").map(Number);
    return new Date(year, month - 1, day);
  }

  function escapeHtml(value) {
    if (value === null || value === undefined) return "";
    return String(value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;"
    })[char]);
  }
})();

























































































// /**
//  * punch_sessions.js
//  *
//  * Read-only punch sessions list.
//  * Data is fetched from the Django REST API.
//  */

// (function () {
//   /* ── Config ──────────────────────────────────────────────────────────── */
//   const API_BASE = "";
//   const API_ENDPOINT = "/dashboard/api/punch-sessions/";
//   const USE_SEED_DATA = false;

//   /* ── DOM refs ─────────────────────────────────────────────────────────── */
//   const root = document.querySelector(".mycrm-admin");
//   const tableBody = root.querySelector("[data-mycrm-table] tbody");
//   const listFooter = root.querySelector("[data-mycrm-list-footer]");

//   /* ── State ────────────────────────────────────────────────────────────── */
//   let sessions = [];
//   let isLoading = false;

//   /* ── Boot ─────────────────────────────────────────────────────────────── */
//   bindShell();
//   bindFilters();
//   loadData();

//   /* ── Sidebar wiring ───────────────────────────────────────────────────── */
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

//   /* ── Filter wiring ────────────────────────────────────────────────────── */
//   function bindFilters() {
//     // Future filter implementation
//   }

//   /* ── Data loading ─────────────────────────────────────────────────────── */
//   async function loadData() {
//     await fetchSessions();
//   }

//   async function fetchSessions() {
//     if (isLoading) return;
//     isLoading = true;
//     showTableMessage("Loading…");

//     try {
//       const response = await fetch(`${API_BASE}${API_ENDPOINT}`, {
//         method: "GET",
//         headers: {
//           "Content-Type": "application/json",
//           "X-Requested-With": "XMLHttpRequest",
//         },
//         credentials: "same-origin"
//       });

//       if (!response.ok) {
//         throw new Error(`Server responded with ${response.status}`);
//       }

//       const data = await response.json();
//       sessions = Array.isArray(data) ? data : (data.results || []);
//       renderSessions();
//     } catch (error) {
//       console.error("Failed to fetch punch sessions:", error);
//       showTableMessage("Failed to load punch sessions. Please try again.");
//     } finally {
//       isLoading = false;
//     }
//   }

//   /* ── Render ───────────────────────────────────────────────────────────── */
//   function renderSessions() {
//     const visible = filteredSessions();
//     tableBody.textContent = "";

//     if (!visible.length) {
//       showTableMessage("No punch sessions found");
//       listFooter.textContent = "0 punch sessions";
//       return;
//     }

//     visible.forEach((session) => {
//       const row = document.createElement("tr");
//       addHtmlCell(row, `<strong>${escapeHtml(session.employee)}</strong>`);
//       addTextCell(row, session.emp_code || "—");
//       addTextCell(row, session.department || "—");
//       addTextCell(row, formatDate(session.date));
//       addTextCell(row, formatDateTime(session.punch_in_date, session.punch_in_time));
//       addTextCell(row, formatDateTime(session.punch_out_date, session.punch_out_time) || "—");
//       addTextCell(row, decimalHours(session) + " hrs");
//       addHtmlCell(row, badge(session.status));
//       tableBody.appendChild(row);
//     });

//     listFooter.textContent = `${visible.length} punch session${visible.length === 1 ? "" : "s"}`;
//   }

//   function filteredSessions() {
//     return sessions;
//   }

//   /* ── Table helpers ────────────────────────────────────────────────────── */
//   function showTableMessage(message) {
//     tableBody.innerHTML = `<tr class="mycrm-empty-row"><td colspan="8">${escapeHtml(message)}</td></tr>`;
//   }

//   function addTextCell(row, value) {
//     const cell = document.createElement("td");
//     cell.textContent = value;
//     row.appendChild(cell);
//   }

//   function addHtmlCell(row, html) {
//     const cell = document.createElement("td");
//     cell.insertAdjacentHTML("beforeend", html);
//     row.appendChild(cell);
//   }

//   function badge(status) {
//     const type =
//       status === "Active" ? "success" :
//       status === "Completed" ? "info" : "warning";
//     return `<span class="mycrm-badge mycrm-badge-${type}">${escapeHtml(status)}</span>`;
//   }

//   /* ── Formatting helpers ───────────────────────────────────────────────── */
//   function decimalHours(session) {
//     const hours = Number(session.total_hours || 0);
//     const minutes = Number(session.total_minutes || 0);
//     return (hours + minutes / 60).toFixed(2);
//   }

//   function formatDate(value) {
//     if (!value) return "";
//     return parseDate(value).toLocaleDateString("en-IN", {
//       day: "2-digit",
//       month: "short",
//       year: "numeric"
//     });
//   }

//   function formatDateTime(date, time) {
//     if (!date || !time) return "";
//     return `${formatDate(date)}, ${formatTime(time)}`;
//   }

//   function formatTime(time) {
//     const [hours, minutes] = time.split(":").map(Number);
//     return new Date(2000, 0, 1, hours, minutes).toLocaleTimeString("en-IN", {
//       hour: "numeric",
//       minute: "2-digit"
//     });
//   }

//   function parseDate(value) {
//     const [year, month, day] = value.split("-").map(Number);
//     return new Date(year, month - 1, day);
//   }

//   function escapeHtml(value) {
//     return String(value).replace(/[&<>"']/g, (char) => ({
//       "&": "&amp;",
//       "<": "&lt;",
//       ">": "&gt;",
//       '"': "&quot;",
//       "'": "&#039;"
//     })[char]);
//   }

//   function showToast(message) {
//     const toast = root.querySelector("[data-mycrm-toast]");
//     toast.textContent = message;
//     toast.classList.add("mycrm-show");
//     setTimeout(() => toast.classList.remove("mycrm-show"), 1800);
//   }
// })();