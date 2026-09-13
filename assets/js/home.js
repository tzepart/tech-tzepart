(function () {
  function cardHtml(entry) {
    return (
      '<article class="post-card">' +
      '<span class="tag">' + entry.tag + "</span>" +
      '<h3><a href="posts/' + entry.slug + '/">' + entry.title + "</a></h3>" +
      "<p>" + entry.excerpt + "</p>" +
      '<div class="meta"><span>' + entry.dateLabel + "</span><span>·</span><span>" + entry.readTime + "</span></div>" +
      "</article>"
    );
  }

  fetch("posts/posts.json")
    .then(function (res) {
      if (!res.ok) throw new Error("Failed to fetch posts.json: " + res.status);
      return res.json();
    })
    .then(function (posts) {
      var sorted = posts.slice().sort(function (a, b) {
        return new Date(b.date) - new Date(a.date);
      });

      var featured = sorted.find(function (p) {
        return p.featured;
      }) || sorted[0];

      var rest = sorted.filter(function (p) {
        return !featured || p.slug !== featured.slug;
      });

      var featuredEl = document.getElementById("featuredPost");
      if (featuredEl && featured) {
        featuredEl.innerHTML =
          '<span class="tag">Featured</span>' +
          '<h2><a href="posts/' + featured.slug + '/">' + featured.title + "</a></h2>" +
          "<p>" + featured.excerpt + "</p>" +
          '<div class="meta"><span>' + featured.dateLabel + "</span><span>·</span><span>" + featured.readTime + " read</span></div>";
      }

      var gridEl = document.getElementById("postGrid");
      if (gridEl) {
        gridEl.innerHTML = rest.map(cardHtml).join("");
      }

      var pillsEl = document.getElementById("topicPills");
      if (pillsEl) {
        var tags = Array.from(new Set(posts.map(function (p) { return p.tag; }))).sort();
        pillsEl.innerHTML = tags.map(function (t) { return '<span class="pill">' + t + "</span>"; }).join("");
      }
    })
    .catch(function (err) {
      console.error("Failed to load posts.json", err);
    });
})();
