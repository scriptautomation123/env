/**
 * Principal Engineer Blog — Main JavaScript
 * Handles theme toggle, reading progress, copy code, TOC, and animations
 */

(function () {
  'use strict';

  // ---- Theme Toggle ----
  const themeToggle = document.getElementById('themeToggle');
  const html = document.documentElement;

  function getPreferredTheme() {
    const stored = localStorage.getItem('theme');
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }

  function setTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }

  setTheme(getPreferredTheme());

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      const current = html.getAttribute('data-theme');
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  // ---- Mobile Navigation Toggle ----
  const navToggle = document.getElementById('navMobileToggle');
  const navLinks = document.querySelector('.nav-links');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      navLinks.classList.toggle('open');
    });

    navLinks.querySelectorAll('.nav-link').forEach(function (link) {
      link.addEventListener('click', function () {
        navLinks.classList.remove('open');
      });
    });
  }

  // ---- Scrolled Nav Shadow ----
  const siteNav = document.getElementById('siteNav');
  if (siteNav) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 10) {
        siteNav.classList.add('scrolled');
      } else {
        siteNav.classList.remove('scrolled');
      }
    }, { passive: true });
  }

  // ---- Reading Progress Bar ----
  const progressBar = document.getElementById('readingProgress');
  if (progressBar) {
    window.addEventListener('scroll', function () {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      progressBar.style.width = Math.min(progress, 100) + '%';
    }, { passive: true });
  }

  // ---- Reading Time Estimate ----
  const readingTimeEl = document.getElementById('readingTime');
  const postContent = document.getElementById('postContent');
  if (readingTimeEl && postContent) {
    const text = postContent.textContent || '';
    const wordCount = text.trim().split(/\s+/).length;
    const minutes = Math.max(1, Math.ceil(wordCount / 230));
    readingTimeEl.textContent = minutes + ' min read';
  }

  // ---- Copy Code Buttons ----
  document.querySelectorAll('.post-content pre').forEach(function (pre) {
    const codeEl = pre.querySelector('code');
    let langClass = '';
    if (codeEl) {
      const classes = codeEl.className.split(' ');
      for (let i = 0; i < classes.length; i++) {
        if (classes[i].indexOf('language-') === 0) {
          langClass = classes[i].replace('language-', '');
          break;
        }
      }
    }
    if (!langClass) {
      const highlightDiv = pre.closest('.highlight');
      if (highlightDiv) {
        const hlClasses = highlightDiv.className.split(' ');
        for (let j = 0; j < hlClasses.length; j++) {
          if (hlClasses[j] !== 'highlight') {
            langClass = hlClasses[j];
            break;
          }
        }
      }
    }

    if (langClass) {
      const langLabel = document.createElement('span');
      langLabel.className = 'code-lang-label';
      langLabel.textContent = langClass;
      pre.style.position = 'relative';
      pre.appendChild(langLabel);
    }

    const btn = document.createElement('button');
    btn.className = 'code-copy-btn';
    btn.textContent = 'Copy';
    btn.setAttribute('aria-label', 'Copy code to clipboard');
    pre.style.position = 'relative';
    pre.appendChild(btn);

    btn.addEventListener('click', function () {
      const code = pre.querySelector('code');
      const codeText = code ? code.textContent : pre.textContent;
      navigator.clipboard.writeText(codeText).then(function () {
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(function () {
          btn.textContent = 'Copy';
          btn.classList.remove('copied');
        }, 2000);
      });
    });
  });

  // ---- Table of Contents Generation ----
  const tocNav = document.getElementById('tocNav');
  if (tocNav && postContent) {
    const headings = postContent.querySelectorAll('h2, h3');
    if (headings.length > 0) {
      headings.forEach(function (heading, idx) {
        if (!heading.id) {
          heading.id = 'heading-' + idx;
        }

        const link = document.createElement('a');
        link.href = '#' + heading.id;
        link.textContent = heading.textContent;
        if (heading.tagName === 'H3') {
          link.className = 'toc-h3';
        }
        tocNav.appendChild(link);
      });

      const tocLinks = tocNav.querySelectorAll('a');

      function updateActiveToc() {
        const scrollPos = window.scrollY + 120;
        let activeIdx = -1;

        for (let i = 0; i < headings.length; i++) {
          if (headings[i].offsetTop <= scrollPos) {
            activeIdx = i;
          }
        }

        tocLinks.forEach(function (link, linkIdx) {
          if (linkIdx === activeIdx) {
            link.classList.add('active');
          } else {
            link.classList.remove('active');
          }
        });
      }

      window.addEventListener('scroll', updateActiveToc, { passive: true });
      updateActiveToc();
    } else {
      const postToc = document.getElementById('postToc');
      if (postToc) postToc.style.display = 'none';
    }
  }

  // ---- Scroll Animations ----
  const animateElements = document.querySelectorAll('.animate-on-scroll');
  if (animateElements.length > 0) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -40px 0px'
    });

    animateElements.forEach(function (el) {
      observer.observe(el);
    });
  }

  // ---- Blog Filters ----
  const filterBtns = document.querySelectorAll('.filter-btn');
  const filterableCards = document.querySelectorAll('.post-card[data-categories]');

  if (filterBtns.length > 0 && filterableCards.length > 0) {
    filterBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        filterBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');

        const filter = btn.getAttribute('data-filter');

        filterableCards.forEach(function (card) {
          if (filter === 'all' || card.getAttribute('data-categories').indexOf(filter) !== -1) {
            card.style.display = '';
            card.classList.remove('visible');
            void card.offsetWidth;
            card.classList.add('visible');
          } else {
            card.style.display = 'none';
          }
        });
      });
    });
  }
})();
