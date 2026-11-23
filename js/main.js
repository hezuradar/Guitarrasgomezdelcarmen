/* Guitarras Gómez del Carmen — interacciones */
(function () {
  'use strict';

  /* --- Cabecera: estado al desplazarse ---------------------------------- */
  const header = document.querySelector('.site-header');
  const onScroll = () => {
    if (!header) return;
    header.classList.toggle('is-scrolled', window.scrollY > 30);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* --- Menú móvil ------------------------------------------------------- */
  const toggle = document.querySelector('.nav-toggle');
  const mobileNav = document.querySelector('.nav-mobile');
  if (toggle && mobileNav) {
    toggle.addEventListener('click', () => {
      const open = document.body.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    });
    mobileNav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        document.body.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.body.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* --- Aparición suave de bloques --------------------------------------- */
  const reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && reveals.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('is-visible'));
  }

  /* --- Filtro de productos ---------------------------------------------- */
  const filterButtons = document.querySelectorAll('.filter-btn');
  const products = document.querySelectorAll('[data-category]');
  if (filterButtons.length && products.length) {
    filterButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const filter = btn.dataset.filter;
        filterButtons.forEach((b) => b.classList.toggle('is-active', b === btn));
        products.forEach((product) => {
          const show = filter === 'all' || product.dataset.category === filter;
          product.style.display = show ? '' : 'none';
        });
      });
    });
  }

  /* --- Lightbox de galerías (una galería = una sola secuencia) ---------- */
  const lightbox = document.querySelector('.lightbox');
  if (lightbox) {
    const img = lightbox.querySelector('.lightbox-image');
    const closeBtn = lightbox.querySelector('.lightbox-close');
    const prevBtn = lightbox.querySelector('.lightbox-prev');
    const nextBtn = lightbox.querySelector('.lightbox-next');
    let current = 0;
    let sources = [];
    let opener = null;

    const render = () => {
      img.src = sources[current];
      img.alt = 'Imagen ' + (current + 1) + ' de ' + sources.length;
    };
    const open = (index, link) => {
      sources = Array.from(link.closest('.gallery').querySelectorAll('a[href]')).map((a) => a.href);
      current = index;
      opener = link;
      render();
      lightbox.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      closeBtn.focus();
    };
    const close = () => {
      lightbox.classList.remove('is-open');
      document.body.style.overflow = '';
      if (opener) opener.focus();
    };
    const step = (dir) => {
      current = (current + dir + sources.length) % sources.length;
      render();
    };

    document.querySelectorAll('.gallery a[href]').forEach((link) => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const siblings = Array.from(link.closest('.gallery').querySelectorAll('a[href]'));
        open(siblings.indexOf(link), link);
      });
    });
    closeBtn.addEventListener('click', close);
    prevBtn.addEventListener('click', () => step(-1));
    nextBtn.addEventListener('click', () => step(1));
    lightbox.addEventListener('click', (e) => { if (e.target === lightbox) close(); });
    document.addEventListener('keydown', (e) => {
      if (!lightbox.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') step(-1);
      if (e.key === 'ArrowRight') step(1);
    });
  }

  /* --- Formulario de contacto: abre el correo con los datos ------------- */
  const form = document.querySelector('#contact-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }
      const hp = form.querySelector('.hp-field input');
      if (hp && hp.value) return;

      const data = new FormData(form);
      const name = (data.get('nombre') || '').toString().trim();
      const email = (data.get('email') || '').toString().trim();
      const message = (data.get('mensaje') || '').toString().trim();
      const subject = 'Consulta desde la web — ' + name;
      const body = 'Nombre: ' + name + '\nEmail: ' + email + '\n\n' + message;
      const status = form.querySelector('.form-status');

      window.location.href = 'mailto:macose_to@yahoo.es?subject=' +
        encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);

      if (status) {
        status.textContent = 'Se ha abierto tu aplicación de correo con el mensaje preparado. Si no se abre, escríbenos directamente a macose_to@yahoo.es o por WhatsApp.';
        status.classList.add('is-visible');
      }
    });
  }

  /* --- Año actual -------------------------------------------------------- */
  const year = document.querySelector('#current-year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
