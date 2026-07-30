import { useEffect, useRef } from "react";
import { useMotionValue, useTransform, animate } from "framer-motion";

/**
 * Counts up from 0 to `value` whenever `value` changes (e.g. once data loads).
 * Renders a plain number if `value` isn't a finite number (keeps "—" / text as-is).
 * Pass as="tspan" when rendering inside an SVG <text> element.
 */
export default function AnimatedCounter({ value, duration = 1, format, as = "span" }) {
  const isNumeric = typeof value === "number" && Number.isFinite(value);
  const motionValue = useMotionValue(0);
  const rendered = useTransform(motionValue, (v) =>
    format ? format(Math.round(v)) : Math.round(v).toLocaleString()
  );
  const ref = useRef(null);

  useEffect(() => {
    if (!isNumeric) return;
    const controls = animate(motionValue, value, {
      duration,
      ease: [0.16, 1, 0.3, 1],
    });
    const unsub = rendered.on("change", (v) => {
      if (ref.current) ref.current.textContent = v;
    });
    return () => {
      controls.stop();
      unsub();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value, isNumeric]);

  if (!isNumeric) return <>{value}</>;

  const Tag = as;
  return <Tag ref={ref}>0</Tag>;
}