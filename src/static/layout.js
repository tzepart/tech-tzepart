(function () {
  var root = document.documentElement;

  function store(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (e) {}
  }

  function label(button, text) {
    button.setAttribute("aria-label", text);
    button.title = text;
  }

  var widthButton = document.querySelector(".width-toggle");
  if (widthButton) {
    var syncWidth = function () {
      var wide = root.classList.contains("wide");
      widthButton.setAttribute("aria-pressed", String(wide));
      label(widthButton, wide ? "Narrow width" : "Full width");
    };
    widthButton.addEventListener("click", function () {
      store("layout", root.classList.toggle("wide") ? "wide" : "narrow");
      syncWidth();
    });
    syncWidth();
    widthButton.hidden = false;
  }

  var themeButton = document.querySelector(".theme-toggle");
  if (themeButton) {
    var darkQuery = window.matchMedia("(prefers-color-scheme: dark)");
    var currentTheme = function () {
      return root.getAttribute("data-theme") || (darkQuery.matches ? "dark" : "light");
    };
    var syncTheme = function () {
      label(themeButton, currentTheme() === "dark" ? "Switch to day mode" : "Switch to night mode");
    };
    themeButton.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      store("theme", next);
      syncTheme();
      document.dispatchEvent(new CustomEvent("themechange", { detail: { theme: next } }));
    });
    darkQuery.addEventListener("change", syncTheme);
    syncTheme();
    themeButton.hidden = false;
  }
})();
