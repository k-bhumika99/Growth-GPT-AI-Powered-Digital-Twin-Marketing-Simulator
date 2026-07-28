/* Growth GPT — UI interactions */

document.addEventListener("DOMContentLoaded", () => {
  initAuthTabs();
  initPasswordToggles();
  initPasswordStrength();
});

/* ---------- Auth: tab switching ---------- */
function initAuthTabs() {
  const tabs = document.querySelectorAll(".auth-tab, .auth-tab-btn");
  const panels = document.querySelectorAll(".auth-form");
  const indicator = document.querySelector(".auth-tab-indicator, .auth-active-indicator");
  const signinIllu = document.getElementById("signin-side-illustration");
  const signupIllu = document.getElementById("signup-side-illustration");
  if (!tabs.length) return;

  function activate(tabName) {
    tabs.forEach(t => t.classList.toggle("active", t.dataset.tab === tabName));
    panels.forEach(p => {
      const isMatch = p.dataset.panel === tabName;
      p.classList.toggle("active", isMatch);
      p.style.display = isMatch ? "flex" : "none";
    });
    if (indicator) indicator.classList.toggle("is-signup", tabName === "signup");

    if (signinIllu) signinIllu.style.display = tabName === "signup" ? "none" : "block";
    if (signupIllu) signupIllu.style.display = tabName === "signup" ? "block" : "none";

    const url = new URL(window.location);
    url.searchParams.set("tab", tabName);
    window.history.replaceState({}, "", url);
  }

  tabs.forEach(tab => {
    tab.addEventListener("click", () => activate(tab.dataset.tab));
  });

  document.querySelectorAll("[data-switch-to]").forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      activate(link.dataset.switchTo);
    });
  });
}

/* ---------- Auth: show/hide password ---------- */
function initPasswordToggles() {
  document.querySelectorAll(".pw-toggle").forEach(btn => {
    btn.addEventListener("click", () => {
      const input = btn.previousElementSibling;
      if (!input) return;
      const isHidden = input.type === "password";
      input.type = isHidden ? "text" : "password";
      btn.textContent = isHidden ? "🙈" : "👁️";
    });
  });
}

/* ---------- Auth: password strength meter ---------- */
function initPasswordStrength() {
  const input = document.getElementById("signup-password");
  const fill = document.getElementById("pw-strength-fill");
  const label = document.getElementById("pw-strength-label");
  if (!input || !fill || !label) return;

  const levels = [
    { min: 0, width: "6%", color: "#E87A64", text: "Password strength" },
    { min: 1, width: "28%", color: "#E87A64", text: "Weak" },
    { min: 2, width: "55%", color: "#E5A84B", text: "Fair" },
    { min: 3, width: "78%", color: "#82A796", text: "Good" },
    { min: 4, width: "100%", color: "#82A796", text: "Strong" },
  ];

  input.addEventListener("input", () => {
    const val = input.value;
    let score = 0;
    if (val.length >= 8) score++;
    if (/[A-Z]/.test(val) && /[a-z]/.test(val)) score++;
    if (/\d/.test(val)) score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;

    const level = val.length === 0 ? levels[0] : levels[Math.min(score, 4)];
    fill.style.width = level.width;
    fill.style.background = level.color;
    label.textContent = val.length === 0 ? "Password strength" : level.text;
  });
}
