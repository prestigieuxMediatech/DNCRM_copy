document.addEventListener("DOMContentLoaded", () => {
  const adminShell = document.querySelector(".mycrm-admin");
  const sidebar = document.querySelector("[data-mycrm-sidebar]");
  const toggle = document.querySelector("[data-mycrm-sidebar-toggle]");

  if (!adminShell || !sidebar || !toggle) {
    return;
  }

  const closeMobileSidebar = () => {
    sidebar.classList.remove("mycrm-open");
    adminShell.querySelectorAll("[data-mycrm-sidebar-backdrop]").forEach((backdrop) => {
      backdrop.classList.remove("mycrm-open");
    });
  };

  // Close the drawer immediately when a destination is chosen. This also
  // prevents a stale backdrop from blocking the next page on touch devices.
  sidebar.addEventListener("click", (event) => {
    if (event.target.closest("a[href]")) {
      closeMobileSidebar();
    }
  });

  adminShell.querySelectorAll("[data-mycrm-sidebar-backdrop]").forEach((backdrop) => {
    backdrop.addEventListener("click", closeMobileSidebar);
  });

  window.addEventListener("resize", () => {
    if (!window.matchMedia("(max-width: 980px)").matches) {
      closeMobileSidebar();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMobileSidebar();
  });

  // Page-specific scripts also bind this button. Handle it in capture phase
  // and stop their duplicate toggles so the drawer and backdrop stay in sync.
  toggle.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopImmediatePropagation();
    if (window.matchMedia("(max-width: 980px)").matches) {
      const opening = !sidebar.classList.contains("mycrm-open");
      sidebar.classList.toggle("mycrm-open", opening);
      adminShell.querySelectorAll("[data-mycrm-sidebar-backdrop]").forEach((backdrop) => {
        backdrop.classList.toggle("mycrm-open", opening);
      });
      return;
    }

    adminShell.classList.toggle("mycrm-sidebar-closed");
  }, true);
});
