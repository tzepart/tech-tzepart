(function () {
  var root = document.documentElement;
  var toggle = document.getElementById("themeToggle");
  var stored = localStorage.getItem("theme");

  if (stored) {
    root.setAttribute("data-theme", stored);
    toggle.textContent = stored === "dark" ? "☀️" : "🌙";
  }

  toggle.addEventListener("click", function () {
    var isDark = root.getAttribute("data-theme") === "dark" ||
      (!root.getAttribute("data-theme") && window.matchMedia("(prefers-color-scheme: dark)").matches);
    var next = isDark ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
    toggle.textContent = next === "dark" ? "☀️" : "🌙";
  });
})();
