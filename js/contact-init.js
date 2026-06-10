(function () {
        var c = window.CONTACT;
        if (!c) return;

        function setLink(id, href, label) {
          var el = document.getElementById(id);
          if (!el) return;
          el.href = href;
          if (label) el.setAttribute('aria-label', label);
        }
        function setText(id, text) {
          var el = document.getElementById(id);
          if (el) el.textContent = text;
        }

        // ── Pill cards (section principale) ──────────────────────────────
        setLink('contact-hero',  'mailto:' + c.email);
        setLink('contact-tel',   'tel:' + c.phone, 'Appeler le ' + c.phoneDisplay);
        setLink('contact-email', 'mailto:' + c.email, 'Envoyer un email à ' + c.email);
        setText('contact-tel-display',   c.phoneDisplay);
        setText('contact-email-display', c.email);

        // ── Contact grid (section bas de page) ───────────────────────────
        setLink('contact-quick-tel',  'tel:' + c.phone, 'Appeler le ' + c.phoneDisplay);
        setLink('contact-grid-tel',   'tel:' + c.phone, 'Appeler le ' + c.phoneDisplay);
        setLink('contact-grid-email', 'mailto:' + c.email, 'Envoyer un email à ' + c.email);
        setLink('contact-cta',        'mailto:' + c.email);
        setText('contact-grid-tel-display',   c.phoneDisplay);
        setText('contact-grid-email-display', c.email);
      })();
