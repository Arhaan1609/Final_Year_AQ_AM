/**
 * Intelligence Designed To Evolve — Vanilla JavaScript Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  /* ─────────────────────────────────────────────────────────────
     1. MOBILE NAVIGATION & HAMBURGER DRAWER
     ───────────────────────────────────────────────────────────── */
  const burgerBtn = document.querySelector(".burger-btn");
  const mobileOverlay = document.querySelector(".mobile-overlay");
  const mobileLinks = document.querySelectorAll(".mobile-link, .mobile-signin");

  function openMenu() {
    if (!mobileOverlay || !burgerBtn) return;
    mobileOverlay.removeAttribute("hidden");
    burgerBtn.classList.add("active");
    burgerBtn.setAttribute("aria-expanded", "true");
    document.body.classList.add("menu-open");
  }

  function closeMenu() {
    if (!mobileOverlay || !burgerBtn) return;
    mobileOverlay.setAttribute("hidden", "");
    burgerBtn.classList.remove("active");
    burgerBtn.setAttribute("aria-expanded", "false");
    document.body.classList.remove("menu-open");
  }

  if (burgerBtn && mobileOverlay) {
    burgerBtn.addEventListener("click", () => {
      const isExpanded = burgerBtn.getAttribute("aria-expanded") === "true";
      if (isExpanded) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    // Close on overlay backdrop click (outside mobile-sheet)
    mobileOverlay.addEventListener("click", (e) => {
      if (e.target === mobileOverlay) {
        closeMenu();
      }
    });

    // Close on Escape key press
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && burgerBtn.getAttribute("aria-expanded") === "true") {
        closeMenu();
      }
    });

    // Close when clicking any navigation link
    mobileLinks.forEach((link) => {
      link.addEventListener("click", () => {
        closeMenu();
      });
    });

    // Close when viewport resized beyond mobile breakpoint (720px)
    window.addEventListener("resize", () => {
      if (window.innerWidth > 720 && burgerBtn.getAttribute("aria-expanded") === "true") {
        closeMenu();
      }
    });
  }

  /* ─────────────────────────────────────────────────────────────
     2. NAVIGATION ACTIVE LINK STATE SWITCHING
     ───────────────────────────────────────────────────────────── */
  const navLinks = document.querySelectorAll(".nav-link");
  navLinks.forEach((link) => {
    link.addEventListener("click", function () {
      navLinks.forEach((l) => l.classList.remove("active"));
      this.classList.add("active");
    });
  });

  const mobNavLinks = document.querySelectorAll(".mobile-link");
  mobNavLinks.forEach((link) => {
    link.addEventListener("click", function () {
      mobNavLinks.forEach((l) => l.classList.remove("active"));
      this.classList.add("active");
    });
  });

  /* ─────────────────────────────────────────────────────────────
     3. STATS COUNT-UP ANIMATION (easeOutCubic)
     ───────────────────────────────────────────────────────────── */
  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  const statItems = document.querySelectorAll(".stat-val");
  let hasAnimated = false;

  function animateCounters() {
    if (hasAnimated) return;
    hasAnimated = true;

    statItems.forEach((el, index) => {
      const target = parseFloat(el.getAttribute("data-target") || "0");
      const decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
      const duration = 1500 + index * 80;
      const startOffset = 480 + index * 90;

      setTimeout(() => {
        const startTime = performance.now();

        function updateCount(now) {
          const elapsed = now - startTime;
          const progress = Math.min(1, elapsed / duration);
          const easedProgress = easeOutCubic(progress);
          const currentVal = easedProgress * target;

          el.textContent = currentVal.toFixed(decimals);

          if (progress < 1) {
            requestAnimationFrame(updateCount);
          } else {
            el.textContent = target.toFixed(decimals);
          }
        }

        requestAnimationFrame(updateCount);
      }, startOffset);
    });
  }

  // Trigger once on view entrance
  const statsFooter = document.querySelector(".stats");
  if (statsFooter && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateCounters();
            observer.disconnect();
          }
        });
      },
      { threshold: 0.25 }
    );
    observer.observe(statsFooter);
  } else {
    // Fallback if IntersectionObserver is not available
    setTimeout(animateCounters, 200);
  }
});
