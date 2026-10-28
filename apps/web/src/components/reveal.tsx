"use client";

import { useEffect } from "react";

/**
 * Landing entrance: each [data-reveal] rises in as it scrolls into view, staggered by --d.
 * An element is held back only as it approaches from below, and any scroll that brings it near shows it,
 * so a failed script, a screenshot or a reader who jumps straight to a section always sees the content.
 */
export function Reveal() {
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const held = new Set<HTMLElement>();
    const showNear = () => {
      for (const el of held) {
        if (el.getBoundingClientRect().top < window.innerHeight * 0.9) { el.dataset.reveal = "show"; held.delete(el); }
      }
    };
    const near = new IntersectionObserver((entries) => {
      for (const e of entries) {
        const el = e.target as HTMLElement;
        if (e.isIntersecting && el.dataset.reveal !== "show" && el.getBoundingClientRect().top > window.innerHeight) {
          el.dataset.reveal = "hold"; held.add(el);
        }
        near.unobserve(el);
      }
    }, { rootMargin: "0px 0px 60% 0px" });
    document.querySelectorAll<HTMLElement>("[data-reveal]").forEach((el) => {
      if (el.getBoundingClientRect().top > window.innerHeight) near.observe(el);
    });
    let raf = 0;
    const onScroll = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(showNear); };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => { near.disconnect(); window.removeEventListener("scroll", onScroll); cancelAnimationFrame(raf); };
  }, []);
  return null;
}
