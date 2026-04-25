(function () {
  'use strict';

  var navToggle = document.getElementById('navToggle');
  var navLinks = document.getElementById('navLinks');

  if (navToggle && navLinks) {
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-controls', 'navLinks');

    navToggle.addEventListener('click', function () {
      var open = navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navLinks.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  var fadeEls = document.querySelectorAll('.fade-in');
  var prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!fadeEls.length) return;

  if (prefersReducedMotion || typeof IntersectionObserver === 'undefined') {
    fadeEls.forEach(function (el) { el.classList.add('visible'); });
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  fadeEls.forEach(function (el) { observer.observe(el); });

  var contactForm = document.getElementById('contactForm');
  var formStatus = document.getElementById('formStatus');
  if (contactForm && formStatus) {
    contactForm.addEventListener('submit', function (e) {
      formStatus.hidden = true;
      formStatus.removeAttribute('data-status');

      if (!contactForm.checkValidity()) {
        e.preventDefault();
        formStatus.textContent = 'Please complete the required fields with a valid email.';
        formStatus.setAttribute('data-status', 'error');
        formStatus.hidden = false;
        var firstInvalid = contactForm.querySelector(':invalid');
        if (firstInvalid && typeof firstInvalid.focus === 'function') firstInvalid.focus();
        return;
      }

      formStatus.textContent = 'Opening your email client. Send the draft to complete the message.';
      formStatus.setAttribute('data-status', 'success');
      formStatus.hidden = false;
    });
  }
})();
