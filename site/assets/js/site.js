(() => {
  const NAV_SCROLL_KEY = "site.nav.scrollTop";
  const NAV_ACTIVE_KEY = "site.nav.activePage";
  const NAV_GROUPS_KEY = "site.nav.groups";
  const nav = document.querySelector(".nav-rail");
  const links = Array.from(document.querySelectorAll(".nav-rail a"));
  const navToggles = Array.from(document.querySelectorAll(".nav-toggle"));
  const frame = document.getElementById("content-frame");
  const home = document.getElementById("home-content");
  const meta = document.getElementById("content-meta");
  const contentShell = document.querySelector(".content-shell");
  let currentPageKey = "home";
  let currentPageLabel = "Home";
  let currentSlideTitle = "";
  let currentTutorialTitle = "";
  let currentSourcePageKey = "home";
  let currentOverviewTarget = "";
  let tutorialTitlePollToken = 0;
  const tutorialTitleFallbackByPageKey = {
    "pages/tut-00-01-lecturer-version.html": "#/|AC",
    "pages/tut-00-01-student-version.html": "Unity Intro - Core Principles and Setup",
    "pages/tut-02-03-lecturer.html": "Unity Intro – Interaction Scripting",
    "pages/tut-02-03-students.html": "Unity Intro – Interaction Scripting",
    "pages/tut-04-lecturers.html": "Unity Animation and Animation Import Overview",
    "pages/tut-04-students.html": "Unity Animation and Animation Import Overview",
    "pages/tut-05.html": "Unity Animation and UI Buttons Overview",
    "pages/tut-07-ui-overview.html": "Week 07 Tutorial – Unity Animation and UI Buttons Overview",
    "pages/tut-08-character-troubleshooting-bb.html": "Unity – 3 types of character controllers:",
    "pages/tut-08-physics-quiz-rbct.html": "Unity3D Physics Quiz: Rigidbody, Collider & Trigger Matrix (Basic)",
    "pages/tut-09-10-0-blender-origins-and-pivots-cheatsheet.html": "Blender - Origins & Pivot Points",
    "pages/tut-09-10-00-blender-ui-overview.html": "Blender UI Overview",
    "pages/tut-09-10-01-blender-ui-cheatsheet.html": "Blender UI CheatSheet",
    "pages/tut-09-10-02-blender-lego-minifig-tutorial-startup-and-reference-images.html": "Setup Reference Images in Blender:",
    "pages/tut-09-10-03-blender-lego-minifig-tutorial-torso-and-head.html": "Blender Lego Minifig Tutorial - Torso and Head",
    "pages/tut-09-10-04-blender-lego-minifig-tutorial-hips-and-legs-2.html": "Blender Lego Minifig Tutorial – Hips and Legs",
    "pages/tut-09-10-04-blender-lego-minifig-tutorial-hips-and-legs.html": "Blender Lego Minifig Tutorial – Hips and Legs",
    "pages/tut-09-10-05-blender-lego-minifig-tutorial-arms-and-hands-2.html": "Blender Lego Minifig Tutorial – Arms and Hands",
    "pages/tut-09-10-05-blender-lego-minifig-tutorial-arms-and-hands.html": "Blender Lego Minifig Tutorial – Arms and Hands",
    "pages/tut-11-01-blender-materials-and-texturing.html": "Face as UV Mapped Texture with Alpha Channel (see through background)",
    "pages/tut-11-02-blender-pivots-and-animation-sheet.html": "Prepare & Animate a LEGO Minifigure in Blender",
    "pages/tut-12-urp-lighting-2026.html": "URP Lighting with Café Model"
  };

  const normalizeText = (value) => value.replace(/\s+/g, " ").trim();

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;

    const button = target.closest("button[data-slide-step]");
    if (!(button instanceof HTMLButtonElement) || button.disabled) return;

    const step = Number(button.dataset.slideStep);
    if (!Number.isFinite(step) || typeof window.changeSlide !== "function") return;

    window.changeSlide(step);
  });

  const isPseudoStart = (node) => {
    if (!(node instanceof HTMLElement)) return false;
    const text = normalizeText(node.textContent || "");
    return /^(pseudo\s*code:?|\/\/\s*pseudo\s*code:?)/i.test(text);
  };

  const isPseudoEligible = (node) => {
    if (!(node instanceof HTMLElement)) return false;
    return node.matches("h3, p");
  };

  const getExplicitIndentLevel = (node) => {
    if (!(node instanceof HTMLElement)) return null;
    const match = Array.from(node.classList)
      .map((className) => className.match(/^indent-level-(\d+)$/))
      .find(Boolean);
    if (!match) return null;
    return Number.parseInt(match[1], 10);
  };

  const clampIndentLevel = (value) => Math.max(0, Math.min(6, value));

  const enableVideoPlaceholders = (rootDocument) => {
    if (!rootDocument?.querySelectorAll) return;

    rootDocument
      .querySelectorAll("iframe.panopto-embed, iframe.video-embed")
      .forEach((frame) => {
        if (!(frame instanceof HTMLIFrameElement)) return;
        if (frame.closest(".video-frame-wrap")) return;
        const parent = frame.parentElement;
        if (!parent) return;

        const wrapper = rootDocument.createElement("div");
        wrapper.className = "video-frame-wrap";

        parent.insertBefore(wrapper, frame);
        wrapper.append(frame);

        frame.addEventListener(
          "load",
          () => {
            wrapper.classList.add("is-loaded");
          },
          { once: true }
        );
      });
  };

  const enableImageExpand = (rootDocument) => {
    if (!rootDocument?.querySelectorAll || !rootDocument.body) return;
    if (rootDocument.body.dataset.imageExpandInitialized === "true") return;

    rootDocument.body.dataset.imageExpandInitialized = "true";

    const overlay = rootDocument.createElement("div");
    overlay.className = "image-lightbox";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "Expanded image preview");
    overlay.setAttribute("aria-hidden", "true");

    const closeButton = rootDocument.createElement("button");
    closeButton.className = "image-lightbox__close";
    closeButton.type = "button";
    closeButton.setAttribute("aria-label", "Close expanded image");
    closeButton.textContent = "Close";

    const fullImage = rootDocument.createElement("img");
    fullImage.className = "image-lightbox__image";
    fullImage.alt = "Expanded image preview";
    overlay.append(closeButton, fullImage);

    let triggerImage = null;

    const closeOverlay = () => {
      overlay.classList.remove("is-open");
      overlay.setAttribute("aria-hidden", "true");
      fullImage.removeAttribute("src");
      triggerImage?.focus({ preventScroll: true });
      triggerImage = null;
    };

    const openOverlay = (src, image) => {
      if (!src) return;
      triggerImage = image;
      fullImage.src = src;
      overlay.classList.add("is-open");
      overlay.setAttribute("aria-hidden", "false");
      closeButton.focus({ preventScroll: true });
    };

    closeButton.addEventListener("click", closeOverlay);
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) closeOverlay();
    });

    rootDocument.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        if (overlay.classList.contains("is-open")) closeOverlay();
      }
    });

    rootDocument
      .querySelectorAll(".content-page-area img, .home-content img")
      .forEach((img) => img.classList.add("image-expandable"));

    rootDocument.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof Element)) return;

      const image = target.closest(".content-page-area img, .home-content img");
      if (!(image instanceof HTMLImageElement)) return;
      if (image.closest(".image-lightbox")) return;

      const link = image.closest("a[href]");
      if (link) {
        event.preventDefault();
      }

      openOverlay(image.currentSrc || image.src, image);
    });

    rootDocument.body.append(overlay);
  };

  const enhancePseudoPanels = (rootDocument) => {
    if (!rootDocument?.querySelectorAll) return;

    const pseudoStarts = Array.from(rootDocument.querySelectorAll("h2, h3, p"))
      .filter((node) => isPseudoStart(node) && !node.closest(".pseudo-panel"));

    pseudoStarts.forEach((startNode) => {
      const parent = startNode.parentElement;
      if (!parent) return;

      const contentNodes = [];
      let cursor = startNode.nextElementSibling;

      while (cursor && cursor.parentElement === parent) {
        if (!isPseudoEligible(cursor)) break;
        if (cursor.matches("h2") || cursor.matches(".page-title")) break;
        contentNodes.push(cursor);
        cursor = cursor.nextElementSibling;
      }

      if (!contentNodes.length) return;

      const panel = rootDocument.createElement("section");
      panel.className = "pseudo-panel";

      const chrome = rootDocument.createElement("div");
      chrome.className = "pseudo-panel__chrome";

      const dots = rootDocument.createElement("div");
      dots.className = "pseudo-panel__dots";
      for (let index = 0; index < 3; index += 1) {
        const dot = rootDocument.createElement("span");
        dot.className = "pseudo-panel__dot";
        dots.append(dot);
      }

      const title = rootDocument.createElement("div");
      title.className = "pseudo-panel__title";
      title.textContent = normalizeText(startNode.textContent || "Pseudocode");

      chrome.append(dots, title);

      const body = rootDocument.createElement("div");
      body.className = "pseudo-panel__body";
      body.setAttribute("role", "region");
      body.setAttribute("aria-label", title.textContent);

      let inferredIndentLevel = 0;

      contentNodes.forEach((node) => {
        const line = rootDocument.createElement("div");
        const text = normalizeText(node.textContent || "");
        const rawText = (node.textContent || "").trim();
        let tone = "code";
        const explicitIndentLevel = getExplicitIndentLevel(node);

        if (/^}/.test(rawText)) {
          inferredIndentLevel = Math.max(0, inferredIndentLevel - 1);
        }

        const indentLevel = clampIndentLevel(
          explicitIndentLevel ?? inferredIndentLevel
        );

        if (/^\/\//.test(text)) {
          tone = "comment";
        } else if (/^[{}]+$/.test(text)) {
          tone = "brace";
        } else if (/^(using |public |private |protected |internal |class |void |if\b|else\b|for\b|while\b|return\b)/i.test(text)) {
          tone = "statement";
        }

        line.className = `pseudo-panel__line pseudo-panel__line--${tone}`;
        line.style.setProperty("--pseudo-indent-level", String(indentLevel));
        node.childNodes.forEach((child) => {
          line.append(child.cloneNode(true));
        });
        body.append(line);

        if (/{\s*$/.test(rawText)) {
          inferredIndentLevel += 1;
        }
      });

      panel.append(chrome, body);
      startNode.replaceWith(panel);
      contentNodes.forEach((node) => node.remove());
    });
  };

  const normalizeTutorialPage = (rootDocument) => {
    const main = rootDocument?.querySelector(".content-page-area");
    if (!main) return;

    let footer = main.querySelector(".tutorial-page-footer");
    if (!footer) {
      footer = rootDocument.createElement("div");
      footer.className = "tutorial-page-footer";

      const logo = rootDocument.createElement("img");
      logo.className = "tutorial-page-footer__logo";
      logo.src = "../images/UOW_Logo_Length_Alpha.png";
      logo.alt = "University of Westminster";

      footer.append(logo);
      main.append(footer);
    }

    let scrollRegion = main.querySelector(":scope > .tutorial-page-scroll");
    if (!scrollRegion || scrollRegion.nodeType !== 1) {
      scrollRegion = rootDocument.createElement("div");
      scrollRegion.className = "tutorial-page-scroll";
      main.insertBefore(scrollRegion, footer);
    }

    Array.from(main.childNodes).forEach((node) => {
      if (node === scrollRegion || node === footer) return;
      scrollRegion.append(node);
    });

    if (scrollRegion.dataset.tutorialAccordionScrollInitialized === "true") return;
    scrollRegion.dataset.tutorialAccordionScrollInitialized = "true";

    scrollRegion.querySelectorAll("details > summary").forEach((summary) => {
      summary.addEventListener("click", () => {
        const details = summary.parentElement;
        window.setTimeout(() => {
          if (!(details instanceof HTMLDetailsElement) || !details.open) return;

          const regionRect = scrollRegion.getBoundingClientRect();
          const detailsRect = details.getBoundingClientRect();
          const nextTop = scrollRegion.scrollTop + (detailsRect.top - regionRect.top) - 12;

          if (nextTop > scrollRegion.scrollTop) {
            scrollRegion.scrollTop = nextTop;
          }
        }, 120);
      });
    });
  };

  const normalizePageKey = (value) => {
    if (!value) return "";
    const noPrefix = value.replace(/^[.][/]/, "");
    return noPrefix.split("?")[0].split("#")[0];
  };

  const isLecturePageKey = (pageKey) => /^pages\/lect-[^/]+\.html$/i.test(normalizePageKey(pageKey || ""));
  const isTutorialPageKey = (pageKey) => /^pages\/tut-[^/]+\.html$/i.test(normalizePageKey(pageKey || ""));

  const getNavGroupForPageKey = (pageKey) => {
    if (isLecturePageKey(pageKey)) return "lectures";
    if (isTutorialPageKey(pageKey)) return "tutorials";
    return null;
  };

  const loadNavGroupState = () => {
    try {
      return JSON.parse(sessionStorage.getItem(NAV_GROUPS_KEY) || "{}");
    } catch {
      return {};
    }
  };

  const navGroupState = loadNavGroupState();

  const saveNavGroupState = () => {
    try {
      sessionStorage.setItem(NAV_GROUPS_KEY, JSON.stringify(navGroupState));
    } catch {
      // Ignore storage issues in restricted contexts.
    }
  };

  const setNavGroupExpanded = (groupName, expanded) => {
    const toggle = navToggles.find((item) => item.dataset.navToggle === groupName);
    const group = nav?.querySelector(`.nav-group[data-nav-group="${groupName}"]`);
    if (!toggle || !group) return;
    toggle.setAttribute("aria-expanded", String(expanded));
    toggle.classList.toggle("is-expanded", expanded);
    group.hidden = !expanded;
    navGroupState[groupName] = expanded;
    saveNavGroupState();
  };

  navToggles.forEach((toggle) => {
    const groupName = toggle.dataset.navToggle;
    setNavGroupExpanded(groupName, navGroupState[groupName] === true);
    toggle.addEventListener("click", () => {
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      setNavGroupExpanded(groupName, !expanded);
    });
  });

  const getLinkKey = (link) => normalizePageKey(
    link.getAttribute("data-page") || link.getAttribute("href")
  );

  const getSidebarLabelForPageKey = (pageKey) => {
    const normalizedKey = normalizePageKey(pageKey || "");
    const sidebarLink = links.find((item) => getLinkKey(item) === normalizedKey);
    if (!sidebarLink) return "";
    return getLinkLabel(sidebarLink);
  };

  const setContentShellMode = (pageKey) => {
    if (!contentShell) return;
    const lectureMode = isLecturePageKey(pageKey);
    const tutorialMode = isTutorialPageKey(pageKey);
    contentShell.classList.remove("content-shell--immersive");
    if (lectureMode) {
      contentShell.classList.add("content-shell--lecture");
    } else {
      contentShell.classList.remove("content-shell--lecture");
    }
    if (tutorialMode) {
      contentShell.classList.add("content-shell--tutorial");
    } else {
      contentShell.classList.remove("content-shell--tutorial");
    }
  };

  const setLectureDocumentMode = (pageKey) => {
    if (!frame?.contentDocument?.body) return;
    frame.contentDocument.body.classList.toggle("lecture-fullbleed", isLecturePageKey(pageKey));
  };

  const getLinkLabel = (link) => {
    const explicit = link.getAttribute("data-label");
    return explicit || link.textContent.trim() || "Tutorial";
  };

  const setActiveLink = (activeKey) => {
    links.forEach((link) => {
      if (getLinkKey(link) === activeKey) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    });

    if (window.matchMedia("(max-width: 960px)").matches) {
      const active = nav?.querySelector('a[aria-current="page"]');
      if (active instanceof HTMLElement) {
        requestAnimationFrame(() => {
          active.scrollIntoView({
            block: "nearest",
            inline: "center",
            behavior: "smooth"
          });
        });
      }
    }
  };

  const setMeta = (label) => {
    if (meta) {
      meta.textContent = label;
    }
  };

  const renderLectureMeta = () => {
    if (!meta || !isLecturePageKey(currentPageKey)) return;

    meta.textContent = "";

    const prefix = document.createElement("span");
    prefix.className = "content-meta-prefix";
    prefix.textContent = `${currentPageLabel}:`;
    meta.append(prefix);

    const slideTitle = normalizeText(currentSlideTitle || "");
    if (!slideTitle) return;

    const spacer = document.createTextNode(" ");
    const suffix = document.createElement("span");
    suffix.className = "content-meta-slide";
    suffix.textContent = slideTitle;
    meta.append(spacer, suffix);
  };

  const setLectureMeta = (slideTitle) => {
    if (!meta || !isLecturePageKey(currentPageKey)) return;
    meta.classList.add("content-meta--lecture");
    const normalizedTitle = normalizeText(slideTitle || "");
    if (normalizedTitle) {
      currentSlideTitle = normalizedTitle;
    }
    renderLectureMeta();
  };

  const getActiveLectureSlideTitle = (rootDocument) => {
    const activeSlide = rootDocument?.querySelector(".slide.active");
    if (!activeSlide) return "";

    const titleNode = activeSlide.querySelector(".slide-title");
    return normalizeText(titleNode?.textContent || "");
  };

  const getTutorialPageTitle = (rootDocument) => {
    if (!rootDocument) return "";

    const titleNode = rootDocument.querySelector(
      ".page-title, main h1, .content-page-area h2, h2"
    );
    const headingTitle = normalizeText(titleNode?.textContent || "");
    if (headingTitle) return headingTitle;

    const docTitle = normalizeText(rootDocument.title || "");
    return docTitle.replace(/^3DIMD\s*\|\s*/i, "");
  };

  const renderTutorialMeta = () => {
    if (!meta || !isTutorialPageKey(currentPageKey)) return;

    meta.textContent = "";

    const prefix = document.createElement("span");
    prefix.className = "content-meta-prefix";
    prefix.textContent = `${currentPageLabel}:`;
    meta.append(prefix);

    const tutorialTitle = normalizeText(currentTutorialTitle || "");
    if (!tutorialTitle) return;

    const spacer = document.createTextNode(" ");
    const suffix = document.createElement("span");
    suffix.className = "content-meta-slide";
    suffix.textContent = tutorialTitle;
    meta.append(spacer, suffix);
  };

  const setTutorialMeta = (tutorialTitle) => {
    if (!meta || !isTutorialPageKey(currentPageKey)) return;
    meta.classList.add("content-meta--tutorial");
    const normalizedTitle = normalizeText(tutorialTitle || "");
    if (normalizedTitle) {
      currentTutorialTitle = normalizedTitle;
    }
    renderTutorialMeta();
  };

  const pollTutorialMetaFromFrame = () => {
    if (!isTutorialPageKey(currentPageKey) || !frame) return;

    const token = ++tutorialTitlePollToken;
    const maxAttempts = 40;
    let attempts = 0;

    const tick = () => {
      if (token !== tutorialTitlePollToken) return;
      if (!isTutorialPageKey(currentPageKey) || !frame.contentDocument) return;

      const tutorialTitle = getTutorialPageTitle(frame.contentDocument);
      if (tutorialTitle) {
        setTutorialMeta(tutorialTitle);
        return;
      }

      attempts += 1;
      if (attempts >= maxAttempts) return;
      requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);
  };

  const saveNavState = (activeKey) => {
    if (!nav) return;
    try {
      sessionStorage.setItem(NAV_SCROLL_KEY, String(nav.scrollTop));
      if (activeKey) {
        sessionStorage.setItem(NAV_ACTIVE_KEY, normalizePageKey(activeKey));
      }
    } catch {
      // Ignore storage issues in restricted contexts.
    }
  };

  const restoreNavScroll = () => {
    if (!nav) return;
    try {
      const saved = sessionStorage.getItem(NAV_SCROLL_KEY);
      if (saved === null) return;
      const top = Number.parseInt(saved, 10);
      if (!Number.isNaN(top)) {
        nav.scrollTop = top;
      }
    } catch {
      // Ignore storage issues in restricted contexts.
    }
  };

  const loadHome = () => {
    if (!frame || !home) return;
    currentPageKey = "home";
    currentPageLabel = "Home";
    currentSlideTitle = "";
    currentTutorialTitle = "";
    currentSourcePageKey = "home";
    currentOverviewTarget = "";
    setContentShellMode("home");
    setLectureDocumentMode("home");
    meta?.classList.remove("content-meta--lecture");
    meta?.classList.remove("content-meta--tutorial");
    frame.style.display = "none";
    frame.removeAttribute("src");
    home.hidden = false;
    setMeta("Home");
    document.title = "3DIMD Course Site";
    setActiveLink("home");
    saveNavState("home");
  };

  const loadPage = (link) => {
    if (!frame || !home || !link) return;
    const pageKey = getLinkKey(link);
    if (!pageKey || pageKey === "home") {
      loadHome();
      return;
    }

    const label = getLinkLabel(link);
    currentPageKey = pageKey;
    currentPageLabel = getSidebarLabelForPageKey(pageKey) || label;
    currentSlideTitle = "";
    currentTutorialTitle = "";
    currentSourcePageKey = link.dataset.sourcePage || pageKey;
    currentOverviewTarget = link.dataset.overviewTarget || "";
    setContentShellMode(currentSourcePageKey);
    if (isLecturePageKey(currentSourcePageKey)) {
      meta?.classList.remove("content-meta--tutorial");
      meta?.classList.add("content-meta--lecture");
      renderLectureMeta();
    } else if (isTutorialPageKey(currentSourcePageKey)) {
      meta?.classList.remove("content-meta--lecture");
      meta?.classList.add("content-meta--tutorial");
      const fallbackTitle = tutorialTitleFallbackByPageKey[pageKey];
      if (fallbackTitle) {
        currentTutorialTitle = fallbackTitle;
      }
      renderTutorialMeta();
    } else {
      meta?.classList.remove("content-meta--lecture");
      meta?.classList.remove("content-meta--tutorial");
      setMeta(label);
    }
    frame.src = currentSourcePageKey;
    frame.style.display = "block";
    home.hidden = true;

    if (isTutorialPageKey(currentSourcePageKey)) {
      pollTutorialMetaFromFrame();
    }

    document.title = `3DIMD | ${label}`;
    setActiveLink(pageKey);
    saveNavState(pageKey);
    const navGroup = link.closest(".nav-group")?.dataset.navGroup || getNavGroupForPageKey(pageKey);
    if (navGroup) {
      setNavGroupExpanded(navGroup, true);
    }
    link.focus({ preventScroll: true });
  };

  const restoreActiveState = () => {
    try {
      const activeKey = normalizePageKey(sessionStorage.getItem(NAV_ACTIVE_KEY) || "home");
      if (!activeKey || activeKey === "home") {
        loadHome();
        return;
      }

      const activeLink = links.find((link) => getLinkKey(link) === activeKey);
      if (!activeLink) {
        loadHome();
        return;
      }

      loadPage(activeLink);
    } catch {
      loadHome();
    }
  };

  links.forEach((link) => {
    link.addEventListener("click", (event) => {
      if (!frame || !home) return;
      event.preventDefault();
      loadPage(link);
    });
  });

  if (home) {
    home.addEventListener("click", (event) => {
      if (!frame) return;
      const target = event.target;
      if (!(target instanceof Element)) return;
      const link = target.closest("a");
      if (!link) return;

      const pageKey = getLinkKey(link);
      if (!pageKey || !pageKey.startsWith("pages/")) return;

      event.preventDefault();
      loadPage(link);
    });
  }

  if (nav) {
    nav.addEventListener("scroll", () => {
      saveNavState();
    }, { passive: true });

    window.addEventListener("resize", () => {
      if (!window.matchMedia("(max-width: 960px)").matches) return;
      const active = nav.querySelector('a[aria-current="page"]');
      if (active instanceof HTMLElement) {
        active.scrollIntoView({
          block: "nearest",
          inline: "center",
          behavior: "auto"
        });
      }
    });

    window.addEventListener("beforeunload", () => {
      saveNavState();
    });
  }

  if (frame) {
    window.addEventListener("message", (event) => {
      const data = event.data;
      if (!data || data.type !== "lecture-slide-title") return;
      if (event.source !== frame.contentWindow) return;
      setLectureMeta(data.title);
    });

    frame.addEventListener("load", () => {
      const rootDocument = frame.contentDocument;
      if (!rootDocument) return;

      setContentShellMode(currentSourcePageKey);
      setLectureDocumentMode(currentSourcePageKey);

      if (currentOverviewTarget) {
        const targetText = normalizeText(currentOverviewTarget).toLowerCase();
        const targetSummary = Array.from(rootDocument.querySelectorAll("details > summary"))
          .find((summary) => normalizeText(summary.textContent || "").toLowerCase() === targetText);
        const targetHeading = Array.from(rootDocument.querySelectorAll("h2, h3"))
          .find((heading) => normalizeText(heading.textContent || "").toLowerCase() === targetText);
        const target = targetSummary || targetHeading;
        if (target) {
          const details = target.closest("details");
          if (details) details.open = true;
          target.scrollIntoView({ block: "start" });
        }
      }

      try {
        enhancePseudoPanels(rootDocument);
      } catch {
        // Continue even if an enhancement fails.
      }

      try {
        enableVideoPlaceholders(rootDocument);
      } catch {
        // Continue even if an enhancement fails.
      }

      try {
        enableImageExpand(rootDocument);
      } catch {
        // Continue even if an enhancement fails.
      }

      try {
        normalizeTutorialPage(rootDocument);
      } catch {
        // Continue even if tutorial layout normalization fails.
      }

      if (isLecturePageKey(currentPageKey)) {
        const syncLectureTitle = () => {
          const activeTitle = getActiveLectureSlideTitle(rootDocument);
          if (activeTitle) {
            setLectureMeta(activeTitle);
            return true;
          }
          return false;
        };

        if (!syncLectureTitle()) {
          requestAnimationFrame(() => {
            syncLectureTitle();
          });
        }
      }

      if (isTutorialPageKey(currentPageKey)) {
        const syncTutorialTitle = () => {
          const tutorialTitle = getTutorialPageTitle(rootDocument);
          if (tutorialTitle) {
            setTutorialMeta(tutorialTitle);
            return true;
          }
          return false;
        };

        if (!syncTutorialTitle()) {
          requestAnimationFrame(() => {
            if (!syncTutorialTitle()) {
              setTimeout(() => {
                if (syncTutorialTitle()) return;

                const observerTarget = rootDocument.documentElement || rootDocument.body;
                if (!observerTarget) return;

                const observer = new MutationObserver(() => {
                  if (syncTutorialTitle()) {
                    observer.disconnect();
                  }
                });

                observer.observe(observerTarget, {
                  childList: true,
                  subtree: true,
                  characterData: true
                });

                setTimeout(() => {
                  observer.disconnect();
                }, 3000);
              }, 120);
            }
          });
        }

        pollTutorialMetaFromFrame();
      }
    });
  }

  restoreNavScroll();
  enhancePseudoPanels(document);
  enableVideoPlaceholders(document);
  enableImageExpand(document);
  normalizeTutorialPage(document);
  if (frame && home) {
    restoreActiveState();
  }
})();
