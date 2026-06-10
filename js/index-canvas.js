/* ── Réseau neuronal (identique à index.html) ── */
  (function () {
    var canvas = document.getElementById('neural-canvas');
    var ctx    = canvas.getContext('2d');
    var NODE_COUNT = 80, CONNECT_DIST = 150, MOUSE_RADIUS = 160, BASE_SPEED = 0.45;
    var nodes = [], mouse = { x: -9999, y: -9999 }, w = 0, h = 0, raf;

    function colors() {
      var light = document.documentElement.classList.contains('light-mode');
      return { node: light ? 'rgba(37,99,235,' : 'rgba(125,211,252,', line: light ? 'rgba(37,99,235,' : 'rgba(125,211,252,' };
    }
    function resize() { w = canvas.width = canvas.offsetWidth; h = canvas.height = canvas.offsetHeight; }
    function initNodes() {
      nodes = [];
      for (var i = 0; i < NODE_COUNT; i++) {
        var angle = Math.random() * Math.PI * 2, speed = BASE_SPEED * (0.5 + Math.random());
        nodes.push({ x: Math.random()*w, y: Math.random()*h, vx: Math.cos(angle)*speed, vy: Math.sin(angle)*speed, r: Math.random()*1.6+1.2 });
      }
    }
    function update() {
      nodes.forEach(function(n) {
        var dx = mouse.x-n.x, dy = mouse.y-n.y, dist = Math.sqrt(dx*dx+dy*dy);
        if (dist < MOUSE_RADIUS && dist > 1) { var f = ((MOUSE_RADIUS-dist)/MOUSE_RADIUS)*0.09; n.vx -= (dx/dist)*f; n.vy -= (dy/dist)*f; }
        n.vx *= 0.98; n.vy *= 0.98;
        var spd = Math.sqrt(n.vx*n.vx+n.vy*n.vy);
        if (spd > BASE_SPEED*5)   { n.vx=(n.vx/spd)*BASE_SPEED*5;  n.vy=(n.vy/spd)*BASE_SPEED*5; }
        if (spd < BASE_SPEED*0.3) { n.vx=(n.vx/Math.max(spd,.001))*BASE_SPEED*.3; n.vy=(n.vy/Math.max(spd,.001))*BASE_SPEED*.3; }
        n.x += n.vx; n.y += n.vy;
        if (n.x < n.r) { n.x=n.r; n.vx=Math.abs(n.vx); } if (n.x > w-n.r) { n.x=w-n.r; n.vx=-Math.abs(n.vx); }
        if (n.y < n.r) { n.y=n.r; n.vy=Math.abs(n.vy); } if (n.y > h-n.r) { n.y=h-n.r; n.vy=-Math.abs(n.vy); }
      });
    }
    function draw() {
      ctx.clearRect(0,0,w,h); var c = colors();
      for (var i=0;i<nodes.length;i++) for (var j=i+1;j<nodes.length;j++) {
        var dx=nodes[i].x-nodes[j].x, dy=nodes[i].y-nodes[j].y, dist=Math.sqrt(dx*dx+dy*dy);
        if (dist < CONNECT_DIST) { ctx.beginPath(); ctx.strokeStyle=c.line+(1-dist/CONNECT_DIST)*0.22+')'; ctx.lineWidth=0.9; ctx.moveTo(nodes[i].x,nodes[i].y); ctx.lineTo(nodes[j].x,nodes[j].y); ctx.stroke(); }
      }
      nodes.forEach(function(n) {
        var dx=mouse.x-n.x, dy=mouse.y-n.y, dist=Math.sqrt(dx*dx+dy*dy);
        ctx.beginPath(); ctx.fillStyle=c.node+(dist<MOUSE_RADIUS?0.95:0.6)+')'; ctx.arc(n.x,n.y,n.r,0,Math.PI*2); ctx.fill();
      });
    }
    function loop() { update(); draw(); raf = requestAnimationFrame(loop); }
    function init() {
      resize(); initNodes();
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { draw(); return; }
      cancelAnimationFrame(raf); loop();
    }
    var hero = canvas.closest('.hero') || canvas.parentElement;
    hero.addEventListener('mousemove', function(e) { var r=canvas.getBoundingClientRect(); mouse.x=e.clientX-r.left; mouse.y=e.clientY-r.top; });
    hero.addEventListener('mouseleave', function() { mouse.x=-9999; mouse.y=-9999; });
    hero.addEventListener('touchmove', function(e) { var r=canvas.getBoundingClientRect(),t=e.touches[0]; mouse.x=t.clientX-r.left; mouse.y=t.clientY-r.top; e.preventDefault(); }, { passive: false });
    hero.addEventListener('touchend', function() { mouse.x=-9999; mouse.y=-9999; });
    window.addEventListener('resize', function() { clearTimeout(window._rt); window._rt=setTimeout(init,150); });
    new MutationObserver(function() { draw(); }).observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    init();
  })();

  /* ── Scroll smooth vers #portfolio-content ── */
  document.querySelector('.scroll-arrow').addEventListener('click', function(e) {
    e.preventDefault();
    document.getElementById('portfolio-content').scrollIntoView({ behavior: 'smooth' });
  });

  /* ── Animations au scroll ── */
  var io = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) { if (e.isIntersecting) { e.target.style.animationPlayState='running'; io.unobserve(e.target); } });
  }, { threshold: 0.12 });
  document.querySelectorAll('.acc-section-header,.acc-project-card,.acc-exp-item,.acc-contact-section,.acc-stats-section').forEach(function(el) {
    el.style.animationPlayState='paused'; io.observe(el);
  });
