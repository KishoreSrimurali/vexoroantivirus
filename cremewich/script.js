(function () {
  // Mobile nav
  const toggle = document.querySelector(".nav-toggle");
  const links = document.getElementById("nav-links");
  toggle.addEventListener("click", () => {
    const open = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  });
  links.addEventListener("click", (e) => {
    if (e.target.closest("a")) {
      links.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Open menu");
    }
  });

  // Toast
  const toast = document.getElementById("toast");
  let toastTimer;
  function showToast(message) {
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 2400);
  }

  // Add to box
  let count = 0;
  document.querySelectorAll(".add").forEach((btn) => {
    btn.addEventListener("click", () => {
      count += 1;
      showToast(`${btn.dataset.item} added · ${count} in your box`);
    });
  });

  // Contact form (front-end only)
  const form = document.getElementById("contact-form");
  const status = form.querySelector(".form-status");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    let valid = true;
    form.querySelectorAll("input, textarea").forEach((field) => {
      const ok = field.value.trim() !== "" && field.checkValidity();
      field.classList.toggle("invalid", !ok);
      if (!ok) valid = false;
    });
    if (!valid) {
      status.textContent = "Please fill in every field with a valid email.";
      return;
    }
    status.textContent = "Thanks! We'll get back to you soon.";
    form.reset();
  });

  document.getElementById("year").textContent = new Date().getFullYear();
})();
