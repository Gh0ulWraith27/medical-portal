// =========================================================
// MediCare Portal JavaScript
// This file handles small browser-side interactions.
// The actual account and prescription data is handled by Python.
// =========================================================

document.addEventListener("DOMContentLoaded", () => {
  // Doctor/Patient tabs on the login page.
  const tabs = document.querySelectorAll(".tab");
  const panels = document.querySelectorAll(".form-card");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const role = tab.dataset.role;

      tabs.forEach(t => t.classList.toggle("active", t === tab));
      panels.forEach(panel => {
        panel.classList.toggle("active", panel.dataset.rolePanel === role);
      });
    });
  });

  // Automatically fade temporary alerts after a few seconds.
  const alert = document.querySelector(".alert");
  if (alert) {
    setTimeout(() => {
      alert.style.transition = "opacity .5s";
      alert.style.opacity = "0";
    }, 4500);
  }
});
