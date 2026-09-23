(function () {
  "use strict";

  /* ==========================================================================
     HELPERS & TOAST
  ========================================================================== */
  const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];

  function showToast(msg) {
    var toast = document.querySelector("[data-mycrm-toast]");
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("mycrm-show");
    setTimeout(function () { toast.classList.remove("mycrm-show"); }, 2000);
  }

  /* ==========================================================================
     SHELL — Sidebar Toggle
  ========================================================================== */
  var root = document.querySelector(".mycrm-admin");
  if (root) {
    var sidebar  = root.querySelector("[data-mycrm-sidebar]");
    var backdrop = root.querySelector("[data-mycrm-sidebar-backdrop]");
    var toggle   = root.querySelector("[data-mycrm-sidebar-toggle]");

    if (toggle) {
      toggle.addEventListener("click", function () {
        if (window.innerWidth <= 980) {
          sidebar.classList.toggle("mycrm-open");
          backdrop.classList.toggle("mycrm-open");
        } else {
          root.classList.toggle("mycrm-sidebar-closed");
        }
      });
    }
    if (backdrop) {
      backdrop.addEventListener("click", function () {
        sidebar.classList.remove("mycrm-open");
        backdrop.classList.remove("mycrm-open");
      });
    }
  }

  /* ==========================================================================
     MODAL — State & Dropdowns
  ========================================================================== */
  var modalBackdrop = document.getElementById("att-modal-backdrop");
  var modalClose    = document.getElementById("modal-close");
  var currentEmpId  = null;
  var modalYear     = new Date().getFullYear();
  var modalMonth    = new Date().getMonth() + 1; // 1-based

  var monthSel = document.getElementById("modal-month-sel");
  var yearSel  = document.getElementById("modal-year-sel");

  // Populate Month Dropdown
  if (monthSel) {
    monthSel.innerHTML = "";
    MONTHS.forEach(function (name, i) {
      var o = document.createElement("option");
      o.value = i + 1;
      o.textContent = name;
      monthSel.appendChild(o);
    });
    monthSel.value = modalMonth;
  }

  // Populate Year Dropdown (Current Year ± 2)
  if (yearSel) {
    yearSel.innerHTML = "";
    var currentY = new Date().getFullYear();
    for (var y = currentY - 2; y <= currentY + 2; y++) {
      var o = document.createElement("option");
      o.value = y;
      o.textContent = y;
      yearSel.appendChild(o);
    }
    yearSel.value = modalYear;
  }

  /* ==========================================================================
     FETCH CALENDAR DATA (Specific Employee)
  ========================================================================== */
  function fetchCalendarData(empId, year, month) {
    var baseUrl = window.calendarApiUrl || "/admin/attendance/api/calendar/";
    if (!baseUrl.endsWith("/")) {
      baseUrl += "/";
    }

    // Clean URL: /admin/attendance/api/calendar/12/?year=2026&month=7
    var url = baseUrl + empId + "/?year=" + year + "&month=" + month;

    return fetch(url, {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json",
      },
      credentials: "same-origin"
    })
    .then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.json();
    })
    .catch(function (err) {
      console.error("Calendar fetch error:", err);
      showToast("Failed to load attendance calendar.");
      throw err;
    });
  }

  /* ==========================================================================
     MODAL CONTROLS
  ========================================================================== */
  function openAttendanceModal(empId, empName) {
    currentEmpId = empId;

    var now = new Date();
    modalYear  = now.getFullYear();
    modalMonth = now.getMonth() + 1;

    if (monthSel) monthSel.value = modalMonth;
    if (yearSel)  yearSel.value = modalYear;

    fetchCalendarData(empId, modalYear, modalMonth)
      .then(function (data) {
        renderModalFromData(data);
        if (modalBackdrop) modalBackdrop.classList.add("mycrm-open");
        document.body.style.overflow = "hidden";
      })
      .catch(function () {
        currentEmpId = null;
      });
  }

  function closeAttendanceModal() {
    if (modalBackdrop) modalBackdrop.classList.remove("mycrm-open");
    document.body.style.overflow = "";
    currentEmpId = null;
  }

  if (modalClose) {
    modalClose.addEventListener("click", closeAttendanceModal);
  }
  if (modalBackdrop) {
    modalBackdrop.addEventListener("click", function (e) {
      if (e.target === modalBackdrop) closeAttendanceModal();
    });
  }

  /* ==========================================================================
     RENDER CALENDAR MODAL
  ========================================================================== */
  function renderModalFromData(data) {
    var emp = data.employee;

    // Header info
    document.getElementById("modal-title").textContent    = "Attendance — " + (emp.name || "");
    document.getElementById("modal-avatar").textContent   = emp.initials || "";
    document.getElementById("modal-emp-name").textContent = emp.name || "";
    document.getElementById("modal-emp-code").textContent = emp.employee_code || "";
    document.getElementById("modal-dept").textContent     = emp.department || "";
    document.getElementById("modal-desig").textContent    = emp.designation || "";
    document.getElementById("modal-email").textContent    = emp.email || "";
    document.getElementById("modal-joining").textContent  = emp.joining_date || "";

    // Month label
    document.getElementById("modal-month-label").textContent = data.month_name + " " + data.year;

    // Summary counts
    document.getElementById("ms-present").textContent = data.summary.present || 0;
    document.getElementById("ms-absent").textContent  = data.summary.absent || 0;
    document.getElementById("ms-leave").textContent   = data.summary.leave || 0;
    document.getElementById("ms-half").textContent    = data.summary.half_day || 0;

    renderCalendarGrid(data);
  }

  function renderCalendarGrid(data) {
    var cal = document.getElementById("modal-cal-body");
    if (!cal) return;
    cal.innerHTML = "";

    var jsFirstDow = (data.first_day_of_week + 1) % 7;
    var daysInMonth = data.days_in_month;

    // Leading empty cells
    for (var i = 0; i < jsFirstDow; i++) {
      var leadEmpty = document.createElement("div");
      leadEmpty.className = "att-cal-day empty";
      cal.appendChild(leadEmpty);
    }

    // Days
    data.calendar_days.forEach(function (dayData) {
      var cell = document.createElement("div");
      var className = "att-cal-day";

      if (dayData.is_today) className += " today";
      if (dayData.is_before_joining) className += " before-joining";
      if (dayData.is_future) className += " future";

      cell.className = className;

      var numEl = document.createElement("div");
      numEl.className = "day-num";
      numEl.textContent = dayData.day;
      cell.appendChild(numEl);

      if (!dayData.is_before_joining && !dayData.is_future && dayData.dot_class) {
        var dotEl = document.createElement("div");
        dotEl.className = "day-dot " + dayData.dot_class;
        dotEl.textContent = dayData.short_status;
        cell.appendChild(dotEl);
      }

      cal.appendChild(cell);
    });

    // Trailing empty cells
    var total = jsFirstDow + daysInMonth;
    var rem = total % 7 === 0 ? 0 : 7 - (total % 7);
    for (var r = 0; r < rem; r++) {
      var trailEmpty = document.createElement("div");
      trailEmpty.className = "att-cal-day empty";
      cal.appendChild(trailEmpty);
    }
  }

  // function refreshCalendar() {
  //   if (!currentEmpId) return;
  //   fetchCalendarData(currentEmpId, modalYear, modalMonth)
  //     .then(function (data) {
  //       renderModalFromData(data);
  //     });
  // }


  function refreshCalendar() {
    if (!currentEmpId) return;
    fetchCalendarData(currentEmpId, modalYear, modalMonth)
      .then(renderModalFromData)
      .catch(function(err) {
        console.error("Refresh failed:", err);
      });
}

  // Month & Year Listeners
  var prevBtn = document.getElementById("modal-prev-month");
  var nextBtn = document.getElementById("modal-next-month");

  if (prevBtn) {
    prevBtn.addEventListener("click", function () {
      modalMonth--;
      if (modalMonth < 1) { modalMonth = 12; modalYear--; }
      if (monthSel) monthSel.value = modalMonth;
      if (yearSel)  yearSel.value = modalYear;
      refreshCalendar();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", function () {
      modalMonth++;
      if (modalMonth > 12) { modalMonth = 1; modalYear++; }
      if (monthSel) monthSel.value = modalMonth;
      if (yearSel)  yearSel.value = modalYear;
      refreshCalendar();
    });
  }

  if (monthSel) {
    monthSel.addEventListener("change", function () {
      modalMonth = +monthSel.value;
      refreshCalendar();
    });
  }

  if (yearSel) {
    yearSel.addEventListener("change", function () {
      modalYear = +yearSel.value;
      refreshCalendar();
    });
  }

  /* ==========================================================================
     EVENT DELEGATION: View buttons on table rows
  ========================================================================== */
  var tbody = document.getElementById("attendance-tbody");
  if (tbody) {
    tbody.addEventListener("click", function (e) {
      var btn = e.target.closest(".mycrm-view-btn");
      if (!btn) return;
      var empId = +btn.dataset.empId;
      var empName = btn.dataset.empName || "";
      openAttendanceModal(empId, empName);
    });
  }

})();