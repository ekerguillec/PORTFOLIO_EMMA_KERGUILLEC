const URL = "https://audiosensible.netlify.app";

    function drawQR(canvasId, size) {
      const canvas = document.getElementById(canvasId);
      if (!canvas) return;
      try {
        QRCode.toCanvas(canvas, URL, {
          width: size,
          margin: 1,
          color: { dark: "#0f172a", light: "#ffffff" }
        });
      } catch (e) {
        canvas.style.display = "none";
      }
    }

    if (typeof QRCode !== "undefined" && QRCode.toCanvas) {
      drawQR("qr-canvas", 160);
      drawQR("qr-canvas-2", 180);
    } else {
      document.querySelectorAll("script").forEach(function(s) {
        if (s.src && s.src.includes("qrcode")) {
          s.addEventListener("load", function() {
            drawQR("qr-canvas", 160);
            drawQR("qr-canvas-2", 180);
          });
        }
      });
    }
