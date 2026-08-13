(() => {
  const NAV_SCROLL_KEY = "site.nav.scrollTop";
  const NAV_ACTIVE_KEY = "site.nav.activePage";
  const nav = document.querySelector(".nav-rail");
  const links = Array.from(document.querySelectorAll(".nav-rail a"));
  const frame = document.getElementById("content-frame");
  const home = document.getElementById("home-content");
  const meta = document.getElementById("content-meta");
  const contentShell = document.querySelector(".content-shell");
  let currentPageKey = "home";
  let currentPageLabel = "Home";
  let currentSlideTitle = "";

  const normalizeText = (value) => value.replace(/\s+/g, " ").trim();

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
    overlay.setAttribute("aria-hidden", "true");

    const fullImage = rootDocument.createElement("img");
    fullImage.className = "image-lightbox__image";
    fullImage.alt = "Expanded image preview";
    overlay.append(fullImage);

    const closeOverlay = () => {
      overlay.classList.remove("is-open");
      overlay.setAttribute("aria-hidden", "true");
      fullImage.removeAttribute("src");
    };

    const openOverlay = (src) => {
      if (!src) return;
      fullImage.src = src;
      overlay.classList.add("is-open");
      overlay.setAttribute("aria-hidden", "false");
    };

    overlay.addEventListener("click", closeOverlay);

    rootDocument.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeOverlay();
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

      openOverlay(image.currentSrc || image.src);
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
        line.innerHTML = node.innerHTML;
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

  const normalizePageKey = (value) => {
    if (!value) return "";
    const noPrefix = value.replace(/^[.][/]/, "");
    return noPrefix.split("?")[0].split("#")[0];
  };

  const isLecturePageKey = (pageKey) => /^pages\/lect-[^/]+\.html$/i.test(normalizePageKey(pageKey || ""));

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
    contentShell.classList.remove("content-shell--immersive");
    if (lectureMode) {
      contentShell.classList.add("content-shell--lecture");
    } else {
      contentShell.classList.remove("content-shell--lecture");
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
    if (!meta || !currentPageKey.startsWith("pages/lect-")) return;

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
    if (!meta || !currentPageKey.startsWith("pages/lect-")) return;
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
    setContentShellMode("home");
    setLectureDocumentMode("home");
    meta?.classList.remove("content-meta--lecture");
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
    setContentShellMode(pageKey);
    if (!isLecturePageKey(pageKey)) {
      meta?.classList.remove("content-meta--lecture");
      setMeta(label);
    } else {
      meta?.classList.add("content-meta--lecture");
      renderLectureMeta();
    }
    frame.src = pageKey;
    frame.style.display = "block";
    home.hidden = true;
    document.title = `3DIMD | ${label}`;
    setActiveLink(pageKey);
    saveNavState(pageKey);
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
      try {
        setContentShellMode(currentPageKey);
        setLectureDocumentMode(currentPageKey);
        enhancePseudoPanels(frame.contentDocument);
        enableVideoPlaceholders(frame.contentDocument);
        enableImageExpand(frame.contentDocument);

        const syncLectureTitle = () => {
          const activeTitle = getActiveLectureSlideTitle(frame.contentDocument);
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
      } catch {
        // Ignore cross-document access issues.
      }
    });
  }

  restoreNavScroll();
  enhancePseudoPanels(document);
  enableVideoPlaceholders(document);
  enableImageExpand(document);
  if (frame && home) {
    restoreActiveState();
  }
})();
