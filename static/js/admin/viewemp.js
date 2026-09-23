// viewEmp.js — Read-only employee profile page

const params    = new URLSearchParams(window.location.search);
const index     = params.get("index");
const employees = JSON.parse(localStorage.getItem("mycrm_employees") || "[]");
const emp       = employees[index];

// ── Sidebar toggle ──────────────────────────────────────
document.getElementById("sidebarToggle").addEventListener("click", () => {
  document.getElementById("sidebar").classList.toggle("open");
  document.getElementById("sidebarBackdrop").classList.toggle("open");
});
document.getElementById("sidebarBackdrop").addEventListener("click", () => {
  document.getElementById("sidebar").classList.remove("open");
  document.getElementById("sidebarBackdrop").classList.remove("open");
});

// ── Helpers ─────────────────────────────────────────────
function fmt(val) {
  return (val && String(val).trim()) ? String(val).trim() : null;
}

function setVal(id, val) {
  const el = document.getElementById(id);
  if (!el) return;
  if (val) {
    el.textContent = val;
    el.classList.remove("empty");
  } else {
    el.textContent = "Not provided";
    el.classList.add("empty");
  }
}

function fmtDate(d) {
  if (!d) return null;
  const dt = new Date(d);
  if (isNaN(dt.getTime())) return d;
  return dt.toLocaleDateString("en-IN", {
    day: "2-digit", month: "short", year: "numeric"
  });
}

function getInitials(name) {
  if (!name) return "?";
  const parts = name.trim().split(" ").filter(Boolean);
  return ((parts[0]?.[0] || "") + (parts[1]?.[0] || "")).toUpperCase() || "?";
}

// ── Not Found ───────────────────────────────────────────
if (!emp) {
  document.getElementById("mainCard").style.display     = "none";
  document.getElementById("notFoundCard").style.display = "block";

} else {

  const name = fmt(emp.name) || "Unknown Employee";

  // Breadcrumb
  document.getElementById("bcName").textContent = name;

  // Employee Code Badge
  if (fmt(emp.emp_code)) {
    document.getElementById("empCodeBadge").textContent = emp.emp_code;
  }

  // ── Card Header ──────────────────────────────────────
  document.getElementById("avatarInitials").textContent = getInitials(name);

  if (emp.profileImage) {
    document.getElementById("cardAvatar").innerHTML =
      `<img src="${emp.profileImage}" alt="${name}">`;
  }

  document.getElementById("hdName").textContent = name;
  document.getElementById("hdSub").textContent  =
    [fmt(emp.designation), fmt(emp.department)].filter(Boolean).join(" · ") || "—";

  // ── Status Pill ──────────────────────────────────────
  const statusMap = {
    active:    { label: "Active",        cls: "active"    },
    probation: { label: "Probation",     cls: "probation" },
    notice:    { label: "Notice Period", cls: "notice"    },
    inactive:  { label: "Inactive",      cls: "inactive"  }
  };
  const sKey  = (fmt(emp.status) || "active").toLowerCase();
  const sInfo = statusMap[sKey] || { label: emp.status, cls: "inactive" };
  const pill  = document.getElementById("statusPill");
  pill.textContent = sInfo.label;
  pill.className   = `status-pill ${sInfo.cls}`;

  // ── Personal Information ──────────────────────────────
  setVal("vEmail",     fmt(emp.email));
  setVal("vPhone",     fmt(emp.phone));
  setVal("vDob",       fmtDate(emp.dob));
  setVal("vEmergency", fmt(emp.emergency_contact));
  setVal("vAddress",   fmt(emp.address));
  setVal("vBio",       fmt(emp.bio));

  // ── Skills ───────────────────────────────────────────
  const skillsEl = document.getElementById("vSkills");
  if (emp.skills && emp.skills.trim()) {
    emp.skills.split(",").forEach(s => {
      const sk = s.trim();
      if (!sk) return;
      const span       = document.createElement("span");
      span.className   = "skill-tag";
      span.textContent = sk;
      skillsEl.appendChild(span);
    });
  } else {
    skillsEl.innerHTML =
      `<span class="field-value empty">No skills listed</span>`;
  }

  // ── Employment Details ────────────────────────────────
  setVal("vCode",    fmt(emp.emp_code));
  setVal("vStatus",  sInfo.label);
  setVal("vDept",    fmt(emp.department));
  setVal("vDesig",   fmt(emp.designation));
  setVal("vJoining", fmtDate(emp.joining));
  setVal("vSalary",  fmt(emp.salary));

  // mono styling for emp code
  const codeEl = document.getElementById("vCode");
  if (codeEl && fmt(emp.emp_code)) codeEl.classList.add("mono");
}