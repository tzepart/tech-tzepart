(function () {
  function slugify(text) {
    return text
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-");
  }

  function getSlugFromPath() {
    var parts = location.pathname.split("/").filter(Boolean);
    if (parts[parts.length - 1] === "index.html") parts.pop();
    return parts[parts.length - 1] || "";
  }

  function normalizeMermaidBlocks(container) {
    container.querySelectorAll("pre code.language-mermaid").forEach(function (block) {
      var div = document.createElement("div");
      div.className = "mermaid";
      div.textContent = block.textContent;
      block.parentElement.replaceWith(div);
    });
    container.querySelectorAll("pre.mermaid").forEach(function (pre) {
      var div = document.createElement("div");
      div.className = "mermaid";
      div.textContent = pre.textContent;
      pre.replaceWith(div);
    });
  }

  function runMermaid(container) {
    var nodes = container.querySelectorAll(".mermaid");
    if (!nodes.length || typeof mermaid === "undefined") return;
    var isDark =
      document.documentElement.getAttribute("data-theme") === "dark" ||
      (!document.documentElement.getAttribute("data-theme") &&
        window.matchMedia("(prefers-color-scheme: dark)").matches);
    mermaid.initialize({ startOnLoad: false, theme: isDark ? "dark" : "default" });
    mermaid.run({ nodes: nodes });
  }

  function buildToc(container) {
    var tocList = document.getElementById("tocList");
    if (!tocList) return;
    container.querySelectorAll("h2").forEach(function (heading) {
      var id = heading.id || slugify(heading.textContent);
      heading.id = id;

      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = "#" + id;
      a.textContent = heading.textContent;
      li.appendChild(a);
      tocList.appendChild(li);
    });
  }

  var slug = getSlugFromPath();
  var contentEl = document.getElementById("postContent");

  fetch("../posts.json")
    .then(function (res) {
      if (!res.ok) throw new Error("Failed to fetch posts.json: " + res.status);
      return res.json();
    })
    .then(function (posts) {
      var entry = posts.find(function (p) {
        return p.slug === slug;
      });
      if (!entry) throw new Error("No posts.json entry for slug: " + slug);

      document.title = entry.title + " — tech.tzepart";
      document.getElementById("postTag").textContent = entry.tag;
      document.getElementById("postTitle").textContent = entry.title;
      document.getElementById("postDate").textContent = entry.dateLabel;
      document.getElementById("postReadTime").textContent = entry.readTime + " read";

      var heroPromise = fetch("hero.html")
        .then(function (res) {
          return res.ok ? res.text() : null;
        })
        .catch(function () {
          return null;
        });

      var contentFile = entry.format === "md" ? "content.md" : "content.html";
      var contentPromise = fetch(contentFile).then(function (res) {
        if (!res.ok) throw new Error("Failed to fetch " + contentFile + ": " + res.status);
        return res.text();
      });

      return Promise.all([heroPromise, contentPromise]).then(function (results) {
        return { hero: results[0], raw: results[1], entry: entry };
      });
    })
    .then(function (data) {
      if (data.hero) {
        document.getElementById("heroSlot").innerHTML = data.hero;
      }

      contentEl.innerHTML = data.entry.format === "md" ? marked.parse(data.raw) : data.raw;

      buildToc(contentEl);
      normalizeMermaidBlocks(contentEl);
      runMermaid(contentEl);
    })
    .catch(function (err) {
      contentEl.innerHTML = '<p class="markdown-loading">Could not load this post.</p>';
      console.error(err);
    });
})();
