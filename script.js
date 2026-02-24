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
