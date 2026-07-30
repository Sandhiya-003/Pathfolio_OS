import { useEffect, useRef } from "react";

/**
 * Lightweight canvas particle field -- small drifting motes in the
 * existing gold/teal palette. Deliberately not a dependency (no
 * tsparticles/etc): a couple dozen circles animated with requestAnimationFrame
 * is plenty for a background accent and keeps bundle size down.
 *
 * Respects prefers-reduced-motion by rendering a static frame instead of animating.
 * Pass `fixed` to cover the whole viewport (for an app-wide ambient layer)
 * instead of sizing against its parent element.
 */
export default function ParticleField({
  count = 36,
  className = "",
  colors = ["#C9A24E", "#4FD1C5", "#9B8AFB"],
  fixed = false,
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let raf;
    let width, height;
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const particles = Array.from({ length: count }, () => ({
      x: Math.random(),
      y: Math.random(),
      r: Math.random() * 1.6 + 0.6,
      speed: Math.random() * 0.06 + 0.02,
      drift: (Math.random() - 0.5) * 0.02,
      color: colors[Math.floor(Math.random() * colors.length)],
      opacity: Math.random() * 0.5 + 0.2,
      twinkle: Math.random() * Math.PI * 2,
    }));

    function resize() {
      const rect = fixed
        ? { width: window.innerWidth, height: window.innerHeight }
        : canvas.parentElement.getBoundingClientRect();
      width = canvas.width = rect.width * devicePixelRatio;
      height = canvas.height = rect.height * devicePixelRatio;
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
      ctx.scale(devicePixelRatio, devicePixelRatio);
    }
    resize();
    window.addEventListener("resize", resize);

    function draw() {
      const w = canvas.width / devicePixelRatio;
      const h = canvas.height / devicePixelRatio;
      ctx.clearRect(0, 0, w, h);

      particles.forEach((p) => {
        p.twinkle += 0.02;
        const twinkleOpacity = p.opacity * (0.6 + 0.4 * Math.sin(p.twinkle));

        ctx.beginPath();
        ctx.arc(p.x * w, p.y * h, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = twinkleOpacity;
        ctx.fill();

        if (!prefersReducedMotion) {
          p.y -= p.speed * 0.01;
          p.x += p.drift * 0.01;
          if (p.y < -0.02) p.y = 1.02;
          if (p.x < -0.02) p.x = 1.02;
          if (p.x > 1.02) p.x = -0.02;
        }
      });
      ctx.globalAlpha = 1;

      if (!prefersReducedMotion) {
        raf = requestAnimationFrame(draw);
      }
    }
    draw();

    return () => {
      window.removeEventListener("resize", resize);
      if (raf) cancelAnimationFrame(raf);
    };
  }, [count, colors, fixed]);

  return (
    <canvas
      ref={canvasRef}
      className={`${fixed ? "fixed" : "absolute"} inset-0 pointer-events-none ${className}`}
      aria-hidden="true"
    />
  );
}