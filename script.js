/* =============================================
   ANDY ZHANG — Personal Website
   script.js
   ============================================= */

// ── TYPING ANIMATION ──
const roles = [
  'Data Scientist',
  'ML Engineer',
  'Quantitative Researcher',
  'Statistics @ UC Berkeley',
  'Psyduck 🐥'
];

let roleIdx = 0, charIdx = 0, deleting = false;
const target = document.getElementById('typingTarget');

function type() {
  const current = roles[roleIdx];
  if (deleting) {
    target.textContent = current.slice(0, --charIdx);
    if (charIdx === 0) {
      deleting = false;
      roleIdx = (roleIdx + 1) % roles.length;
      setTimeout(type, 400);
      return;
    }
    setTimeout(type, 50);
  } else {
    target.textContent = current.slice(0, ++charIdx);
    if (charIdx === current.length) {
      deleting = true;
      setTimeout(type, 1800);
      return;
    }
    setTimeout(type, 80);
  }
}
setTimeout(type, 600);

// ── NAVBAR SCROLL EFFECT ──
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 20);
}, { passive: true });

// ── ACTIVE NAV LINK ──
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link');

function updateActiveLink() {
  let current = '';
  sections.forEach(section => {
    const sectionTop = section.offsetTop - 100;
    if (window.scrollY >= sectionTop) current = section.getAttribute('id');
  });
  navLinks.forEach(link => {
    link.classList.toggle('active', link.getAttribute('href') === `#${current}`);
  });
}
window.addEventListener('scroll', updateActiveLink, { passive: true });

// ── HAMBURGER MENU ──
const menuToggle = document.getElementById('menuToggle');
const navLinksList = document.querySelector('.nav-links');
menuToggle.addEventListener('click', () => {
  navLinksList.classList.toggle('open');
});
// Close on link click
navLinksList.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => navLinksList.classList.remove('open'));
});

// ── INTERSECTION OBSERVER — fade-in & skill bars ──
const fadeEls = document.querySelectorAll('.fade-in');
const skillBars = document.querySelectorAll('.skill-bar-fill');

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

fadeEls.forEach(el => observer.observe(el));

const barObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const bar = entry.target;
      const width = bar.dataset.width || '0';
      bar.style.width = width + '%';
      barObserver.unobserve(bar);
    }
  });
}, { threshold: 0.2 });

skillBars.forEach(bar => barObserver.observe(bar));

// ── SMOOTH SCROLL for anchor links ──
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const href = a.getAttribute('href');
    if (href === '#') return;
    const target = document.querySelector(href);
    if (target) {
      e.preventDefault();
      const top = target.getBoundingClientRect().top + window.scrollY - 64;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});

// ── RENDERERS (data driven from data.js) ──────────────────────────────────────

function renderExperience() {
  const container = document.getElementById('experience-list');
  if (!container) return;
  container.innerHTML = EXPERIENCE.map(job => `
    <div class="timeline-item fade-in">
      <div class="timeline-dot${job.alt ? ' timeline-dot-alt' : ''}"></div>
      ${job.alt ? '' : '<div class="timeline-connector"></div>'}
      <div class="timeline-content glass-card">
        <div class="timeline-header">
          <div>
            <h3 class="timeline-role">${job.role}</h3>
            <p class="timeline-company">${job.company}</p>
          </div>
          <span class="timeline-date mono">${job.date}</span>
        </div>
        <ul class="timeline-bullets">
          ${job.bullets.map(b => `<li>${b}</li>`).join('')}
        </ul>
        <div class="timeline-tags">${job.tags.map(t => `<span class="tl-tag">${t}</span>`).join('')}</div>
      </div>
    </div>`).join('');
  reobserve();
}

function buildLinks(links) {
  return links.map(l => {
    if (l.type === 'github') {
      return `<a href="${l.url}" target="_blank" rel="noopener" title="GitHub" class="project-link" aria-label="GitHub">${SVG.github}</a>`;
    }
    if (l.type === 'demo') {
      return `<a href="${l.url}" target="_blank" rel="noopener" title="Live Demo" class="project-link" aria-label="Live Demo" style="color:var(--gold)">${SVG.play}</a>`;
    }
    if (l.type === 'report') {
      return `<a href="${l.url}" target="_blank" rel="noopener" title="View Report" class="project-link" aria-label="View Report" style="color:var(--gold)">${SVG.report}</a>`;
    }
    return '';
  }).join('');
}

function buildDiagram(d) {
  const colorMap = { blue: '#4a9eff', gold: '#f5b642', purple: '#c084fc' };
  const borderMap = { blue: '#1e3a5f', gold: '#f5b64260', purple: '#a855f7' };
  const nodes = d.flow.map((n, i) => `
    ${i > 0 ? `<div style="display:flex;align-items:center;color:#f5b642;font-size:14px;">⟶</div>` : ''}
    <div style="background:#0d1a2e;border:1px solid ${borderMap[n.color]};border-radius:6px;padding:8px 12px;min-width:90px;text-align:center;">
      <div style="color:${colorMap[n.color]};font-size:10px;margin-bottom:4px;">${n.label}</div>
      ${n.lines.map(l => `<div style="color:#c8cdd8;font-size:9px;">${l}</div>`).join('')}
    </div>`).join('');
  const tools = d.docker.tools.map(t =>
    `<div style="background:#0a1a0a;border:1px solid #2a4a2a;border-radius:4px;padding:4px 8px;color:#c8cdd8;font-size:9px;">${t}</div>`
  ).join('');
  return `
    <div style="margin:12px 0;font-family:'JetBrains Mono',monospace;font-size:11px;line-height:1.7;color:var(--text-secondary);">
      <div style="display:flex;align-items:stretch;gap:6px;flex-wrap:wrap;">${nodes}</div>
      <div style="margin-top:8px;border:1px dashed #2a4a2a;border-radius:6px;padding:8px 12px;">
        <div style="color:#4ade80;font-size:9px;margin-bottom:6px;">${d.docker.label}</div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;">${tools}</div>
      </div>
    </div>`;
}

function buildCarousel(slides) {
  const imgs = slides.map((s, i) =>
    `<img src="${s.src}" alt="${s.alt}" loading="lazy" class="carousel-slide${i === 0 ? ' active' : ''}" />`
  ).join('');
  const dots = slides.map((_, i) =>
    `<button class="carousel-dot${i === 0 ? ' active' : ''}" aria-label="Slide ${i + 1}"></button>`
  ).join('');
  return `
    <div class="carousel">
      <div class="carousel-track">${imgs}</div>
      <button class="carousel-btn carousel-prev" aria-label="Previous">&#8249;</button>
      <button class="carousel-btn carousel-next" aria-label="Next">&#8250;</button>
      <div class="carousel-label"></div>
      <div class="carousel-dots">${dots}</div>
    </div>`;
}

function initCarousels() {
  document.querySelectorAll('.carousel').forEach(carousel => {
    const slides = carousel.querySelectorAll('.carousel-slide');
    const dots   = carousel.querySelectorAll('.carousel-dot');
    const label  = carousel.querySelector('.carousel-label');
    let idx = 0;

    function go(n) {
      slides[idx].classList.remove('active');
      dots[idx].classList.remove('active');
      idx = (n + slides.length) % slides.length;
      slides[idx].classList.add('active');
      dots[idx].classList.add('active');
      label.textContent = slides[idx].alt;
    }

    label.textContent = slides[0].alt;
    carousel.querySelector('.carousel-prev').addEventListener('click', () => go(idx - 1));
    carousel.querySelector('.carousel-next').addEventListener('click', () => go(idx + 1));
    dots.forEach((dot, i) => dot.addEventListener('click', () => go(i)));
  });
}

function buildProjectCard(p) {
  const links = buildLinks(p.links || []);
  const partner = p.partner ? `<div class="project-partner mono">${p.partner}</div>` : '';
  const extra = p.diagram ? buildDiagram(p.diagram) : (p.extra || '');
  const tags = `<div class="project-tags">${p.tags.map(t => `<span class="p-tag">${t}</span>`).join('')}</div>`;

  if (p.featured) {
    let media;
    if (p.slides) {
      media = buildCarousel(p.slides);
    } else if (p.demo.type === 'video') {
      media = `<video src="${p.demo.src}" autoplay muted loop playsinline style="width:100%;border-radius:8px;display:block;"></video>`;
    } else {
      media = `<img src="${p.demo.src}" alt="${p.demo.alt || ''}" loading="lazy" style="width:100%;border-radius:8px;display:block;object-fit:cover;" />`;
    }
    return `
      <div class="project-card project-card-featured glass-card fade-in">
        <div class="project-demo">${media}</div>
        <div class="project-info">
          <div class="project-header">
            <div class="project-icon">${p.icon || ''}</div>
            <div class="project-links">${links}</div>
          </div>
          ${partner}
          <h3 class="project-title">${p.title}</h3>
          <p class="project-desc">${p.desc}</p>
          ${extra}${tags}
        </div>
      </div>`;
  }

  return `
    <div class="project-card glass-card fade-in">
      <div class="project-header">
        <div class="project-icon">${p.icon || ''}</div>
        <div class="project-links">${links}</div>
      </div>
      ${partner}
      <h3 class="project-title">${p.title}</h3>
      <p class="project-desc">${p.desc}</p>
      ${extra}${tags}
    </div>`;
}

function renderProjects() {
  const container = document.getElementById('projects-grid');
  if (!container) return;
  container.innerHTML = PROJECTS.map(buildProjectCard).join('');
  reobserve();
}

function renderEducation() {
  const container = document.getElementById('education-grid');
  if (!container) return;
  container.innerHTML = EDUCATION.map(e => `
    <div class="edu-card glass-card fade-in">
      <div class="edu-logo ${e.logoClass}">${e.logo}</div>
      <div class="edu-body">
        <div class="edu-header">
          <div>
            <h3 class="edu-degree">${e.degree}</h3>
            <p class="edu-school">${e.school}</p>
          </div>
          <span class="edu-date mono">${e.date}</span>
        </div>
        <div class="edu-gpa"><span class="gpa-label mono">GPA</span><span class="gpa-value gradient-text">${e.gpa}</span></div>
        <p class="edu-desc">${e.desc}</p>
        ${e.honors.length ? `<div class="edu-honors">${e.honors.map(h => `<div class="honor-badge"><span>${h}</span></div>`).join('')}</div>` : ''}
        ${e.tags.length ? `<div class="edu-tags">${e.tags.map(t => `<span class="e-tag">${t}</span>`).join('')}</div>` : ''}
      </div>
    </div>`).join('');
  reobserve();
}

function renderBlogs() {
  const container = document.getElementById('blogs-grid');
  if (!container) return;
  container.innerHTML = BLOGS.map(b => `
    <div class="blog-card glass-card fade-in">
      <div class="blog-date mono">${b.date}</div>
      <h3 class="blog-title"><a href="${b.href}">${b.title}</a></h3>
      <p class="blog-desc">${b.desc}</p>
      <div class="blog-footer">
        <span class="blog-tag p-tag">${b.tag}</span>
        <a href="${b.href}" class="blog-more">Read More &rarr;</a>
      </div>
    </div>`).join('');
  reobserve();
}

// Re-attach intersection observers after dynamic render
function reobserve() {
  document.querySelectorAll('.fade-in:not(.observed)').forEach(el => {
    el.classList.add('observed');
    observer.observe(el);
  });
  document.querySelectorAll('.skill-bar-fill:not(.observed)').forEach(bar => {
    bar.classList.add('observed');
    barObserver.observe(bar);
  });
}

// ── INIT ──────────────────────────────────────────────────────────────────────
renderExperience();
renderProjects();
initCarousels();
renderEducation();
renderBlogs();
