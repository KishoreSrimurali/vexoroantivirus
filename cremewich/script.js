// Mobile nav toggle
const toggle = document.querySelector(".nav-toggle");
const links = document.getElementById("nav-links");

toggle.addEventListener("click", () => {
  const open = toggle.getAttribute("aria-expanded") === "true";
  toggle.setAttribute("aria-expanded", String(!open));
  toggle.setAttribute("aria-label", open ? "Open menu" : "Close menu");
  links.classList.toggle("is-open", !open);
});

links.addEventListener("click", (e) => {
  if (e.target.closest("a")) {
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open menu");
    links.classList.remove("is-open");
  }
});

// Menu filters
const filters = document.querySelectorAll(".filter");
const items = document.querySelectorAll("#menu [data-category]");

filters.forEach((btn) => {
  btn.addEventListener("click", () => {
    const filter = btn.dataset.filter;
    filters.forEach((b) => {
      const active = b === btn;
      b.classList.toggle("is-active", active);
      b.setAttribute("aria-pressed", String(active));
    });
    items.forEach((item) => {
      item.hidden = filter !== "all" && item.dataset.category !== filter;
    });
  });
});

// Contact form (client-side only: validates and confirms; wire to a backend or form service to deliver)
const form = document.getElementById("contact-form");
const status = form.querySelector(".form-status");

form.addEventListener("submit", (e) => {
  e.preventDefault();
  let valid = true;
  form.querySelectorAll("input, textarea").forEach((field) => {
    const ok = field.checkValidity() && field.value.trim() !== "";
    field.classList.toggle("is-invalid", !ok);
    if (!ok) valid = false;
  });

  if (!valid) {
    status.textContent = "Please fill in every field with a valid email.";
    status.className = "form-status err";
    return;
  }

  const name = form.elements.name.value.trim().split(" ")[0];
  status.textContent = `Thanks, ${name}! We'll be in touch soon.`;
  status.className = "form-status ok";
  form.reset();
});

document.getElementById("year").textContent = new Date().getFullYear();
