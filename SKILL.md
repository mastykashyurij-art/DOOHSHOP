---
name: animated-website
description: "This skill should be used when the user asks to 'create an animated website', 'build an animated landing page', 'add animations to a site', 'make a page with scroll animations', 'create motion effects', 'build a parallax site', 'add GSAP animations', 'use Framer Motion', 'animate with Three.js', 'create a loading animation', 'add micro-interactions', 'build a website with particle background', 'create text reveal animations', 'make scroll-triggered effects', 'add page transitions', or asks for any website, landing page, portfolio, or web experience with motion, animation, or interactive visual effects — even if they don't say the word 'animation' explicitly."
argument-hint: "[style] [framework] [animation-type]"
license: MIT
metadata:
  author: custom
  version: "1.0.0"
---

# Animated Website Builder

This skill guides the creation of performant, accessible, visually compelling animated web experiences. Apply it for any website or web component that involves motion, transitions, scroll behavior, micro-interactions, or ambient visual effects.

## Step 1 — Choose the Right Animation Stack

Before writing a single line, select the right tool. The wrong library creates unnecessary bundle weight and runtime cost.

### Library Selection Matrix

| Library | Best For | Bundle | When to Avoid |
|---|---|---|---|
| **CSS-only** | Hover states, reveals, loaders, simple transitions | 0 KB | Complex timelines, JS-driven sequences |
| **Web Animations API** | Programmatic CSS animation, no dependencies | 0 KB | IE11, complex easing, stagger |
| **Anime.js** | Lightweight JS animation, SVG, stagger sequences | ~17 KB | React declarative flows, 3D |
| **GSAP** | Complex timelines, ScrollTrigger, SVG morphing | ~30 KB | Simple hover/reveal (overkill) |
| **Framer Motion** | React apps, layout animation, page transitions | ~50 KB | Vanilla HTML/CSS, perf-critical mobile |
| **Three.js / R3F** | 3D scenes, WebGL backgrounds, product viz | ~600 KB | 2D-only needs, mobile-first low-end |
| **Lottie** | After Effects exports, complex illustration | ~60 KB | When AE JSON files are unavailable |

**Decision rules:**
- Static marketing page with subtle reveals → CSS keyframes + Intersection Observer
- React app with route changes and layout shifts → Framer Motion
- Narrative scroll experience with pinning, scrubbing, parallax → GSAP + ScrollTrigger
- Lightweight interactive SVG or staggered list → Anime.js
- 3D hero, product demo, or WebGL canvas → Three.js or React Three Fiber
- Designer-supplied Lottie JSON → `@lottiefiles/dotlottie-web`

---

## Step 2 — Plan the Choreography

Map out the animation timeline before coding:
1. What animates first (page load)
2. What triggers on scroll (reveal order, stagger delay)
3. What responds to interaction (hover, click, focus)
4. What plays ambient/looping (background, particles)

Stagger delays create narrative. Establish a rhythm: hero at 0ms, headline at 200ms, subtext at 400ms, CTA at 600ms. Never animate everything simultaneously.

---

## Step 3 — Implement

### Page Enter / Exit Transitions

**CSS-only page reveal:**
```css
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}

.page-enter {
  animation: fadeUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
}
```

**Framer Motion route transition (Next.js App Router):**
```tsx
'use client';
import { motion, AnimatePresence } from 'framer-motion';

const variants = {
  hidden: { opacity: 0, y: 20 },
  enter:  { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
  exit:   { opacity: 0, y: -10, transition: { duration: 0.2 } },
};

export default function PageWrapper({ children }: { children: React.ReactNode }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div variants={variants} initial="hidden" animate="enter" exit="exit">
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

---

### Scroll-Triggered Animations

**Intersection Observer fade-in (zero dependencies):**
```js
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.15, rootMargin: '0px 0px -60px 0px' }
);

document.querySelectorAll('[data-animate]').forEach((el) => observer.observe(el));
```

```css
[data-animate] {
  opacity: 0;
  transform: translateY(32px);
  transition: opacity 0.6s ease, transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
[data-animate].is-visible {
  opacity: 1;
  transform: translateY(0);
}
@media (prefers-reduced-motion: reduce) {
  [data-animate] { opacity: 1; transform: none; transition: none; }
}
```

**GSAP ScrollTrigger setup:**
```js
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

gsap.from('.card', {
  scrollTrigger: {
    trigger: '.cards-section',
    start: 'top 80%',
    toggleActions: 'play none none reverse',
  },
  opacity: 0,
  y: 48,
  stagger: 0.12,
  duration: 0.7,
  ease: 'power3.out',
});

// Horizontal scrub (pinned section)
gsap.to('.strip', {
  x: () => -(document.querySelector('.strip').scrollWidth - window.innerWidth),
  ease: 'none',
  scrollTrigger: {
    trigger: '.horizontal-section',
    pin: true,
    scrub: 1,
    end: () => `+=${document.querySelector('.strip').scrollWidth}`,
  },
});
```

---

### Parallax Effects

```js
let ticking = false;
window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      document.documentElement.style.setProperty('--scroll-y', `${window.scrollY}px`);
      ticking = false;
    });
    ticking = true;
  }
});
```

```css
.hero-bg {
  transform: translateY(calc(var(--scroll-y, 0px) * 0.4));
}
@media (prefers-reduced-motion: reduce) {
  .hero-bg { transform: none; }
}
```

---

### Micro-Interactions (CSS-only)

```css
.btn {
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1),
              box-shadow 0.2s ease;
}
.btn:hover  { transform: translateY(-3px) scale(1.02); box-shadow: 0 12px 40px rgba(0,0,0,0.18); }
.btn:active { transform: translateY(0) scale(0.98); transition-duration: 0.08s; }

/* Link underline draw */
.nav-link { position: relative; }
.nav-link::after {
  content: '';
  position: absolute;
  bottom: -2px; left: 0;
  width: 100%; height: 2px;
  background: currentColor;
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 0.3s ease;
}
.nav-link:hover::after,
.nav-link:focus-visible::after {
  transform: scaleX(1);
  transform-origin: left;
}

@media (prefers-reduced-motion: reduce) {
  .btn, .btn:hover, .btn:active,
  .nav-link::after { transition: none; transform: none; }
}
```

---

### Loading / Skeleton Animations

```css
@keyframes shimmer {
  to { background-position: 200% center; }
}
.skeleton {
  background: linear-gradient(90deg, #e8e8e8 25%, #f4f4f4 50%, #e8e8e8 75%) 0 0 / 200% auto;
  animation: shimmer 1.5s linear infinite;
  border-radius: 4px;
}
@media (prefers-reduced-motion: reduce) {
  .skeleton { animation: none; background: #e8e8e8; }
}
```

---

### Text Animations

**CSS word-split reveal:**
```css
@keyframes charReveal {
  from { opacity: 0; transform: translateY(0.5em) rotate(4deg); }
  to   { opacity: 1; transform: translateY(0) rotate(0); }
}
.word-reveal > span {
  display: inline-block;
  opacity: 0;
  animation: charReveal 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: calc(var(--i, 0) * 80ms);
}
@media (prefers-reduced-motion: reduce) {
  .word-reveal > span { opacity: 1; transform: none; animation: none; }
}
```

```js
document.querySelectorAll('.word-reveal').forEach((el) => {
  el.innerHTML = el.textContent
    .trim()
    .split(' ')
    .map((w, i) => `<span style="--i:${i}">${w}&nbsp;</span>`)
    .join('');
});
```

**CSS-only typewriter:**
```css
.typewriter {
  overflow: hidden;
  border-right: 2px solid currentColor;
  white-space: nowrap;
  width: 0;
  animation: type 2.5s steps(30) 0.5s forwards, blink 0.8s step-end infinite;
}
@keyframes type  { to { width: 100%; } }
@keyframes blink { 50% { border-color: transparent; } }
@media (prefers-reduced-motion: reduce) {
  .typewriter { width: 100%; animation: none; border-right: none; }
}
```

---

### Background Animations

**CSS animated gradient mesh:**
```css
@keyframes gradientShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.gradient-bg {
  background: linear-gradient(-45deg, #0f172a, #1e293b, #0f2460, #1a103d);
  background-size: 400% 400%;
  animation: gradientShift 12s ease infinite;
}
@media (prefers-reduced-motion: reduce) {
  .gradient-bg { animation: none; }
}
```

**Canvas particle background:**
```js
const canvas = document.getElementById('particles');
const ctx = canvas.getContext('2d');
let W = canvas.width  = window.innerWidth;
let H = canvas.height = window.innerHeight;

const particles = Array.from({ length: 60 }, () => ({
  x: Math.random() * W, y: Math.random() * H,
  r: Math.random() * 2 + 1,
  vx: (Math.random() - 0.5) * 0.4,
  vy: (Math.random() - 0.5) * 0.4,
  alpha: Math.random() * 0.5 + 0.2,
}));

let rafId;
function draw() {
  ctx.clearRect(0, 0, W, H);
  for (const p of particles) {
    p.x = (p.x + p.vx + W) % W;
    p.y = (p.y + p.vy + H) % H;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,255,255,${p.alpha})`;
    ctx.fill();
  }
  rafId = requestAnimationFrame(draw);
}

const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
if (!mq.matches) draw();
else canvas.style.display = 'none';
mq.addEventListener('change', (e) => {
  if (e.matches) { cancelAnimationFrame(rafId); canvas.style.display = 'none'; }
  else { canvas.style.display = ''; draw(); }
});
window.addEventListener('resize', () => {
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
});
```

---

### CSS Custom Property Animations

Custom properties let JS drive CSS animations without layout thrash:

```css
.progress-ring {
  --progress: 0;
  stroke-dashoffset: calc(251 - (251 * var(--progress)) / 100);
  transition: stroke-dashoffset 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
```

```js
el.style.setProperty('--progress', '75');
```

---

## Step 4 — Performance Contract

These rules are non-negotiable.

### Compositor-Thread-Only Properties

Animate **only** these — they run on the GPU and never trigger layout or paint:
- `transform` (translate, scale, rotate, skew)
- `opacity`
- `filter` (use sparingly on mobile)

**Never animate:** `width`, `height`, `top`, `left`, `right`, `bottom`, `margin`, `padding`, `border-width`, `font-size`.

### `will-change` Rules

Only add after profiling proves it helps. Remove after animation completes:
```js
el.style.willChange = 'transform';
doAnimation().then(() => { el.style.willChange = 'auto'; });
```

Limit to 4–6 simultaneously promoted layers on mobile.

### requestAnimationFrame Pattern

Batch reads before writes — never mix in the same frame:
```js
function updatePositions(items) {
  const bounds = items.map((el) => el.getBoundingClientRect()); // READ
  requestAnimationFrame(() => {
    items.forEach((el, i) => {
      el.style.transform = `translateY(${bounds[i].top * 0.1}px)`; // WRITE
    });
  });
}
```

### Lazy-Load Heavy Libraries

```js
let loaded = false;
window.addEventListener('scroll', async () => {
  if (loaded) return;
  loaded = true;
  const { default: gsap } = await import('gsap');
  const { ScrollTrigger } = await import('gsap/ScrollTrigger');
  gsap.registerPlugin(ScrollTrigger);
  initScrollAnimations(gsap, ScrollTrigger);
}, { passive: true });
```

---

## Step 5 — Accessibility: Reduced Motion

Structure code as **motion-opt-in**, not motion-opt-out:

```css
/* Default: static. Motion is an enhancement. */
.hero-title { opacity: 1; transform: none; }

@media (prefers-reduced-motion: no-preference) {
  .hero-title {
    opacity: 0;
    transform: translateY(24px);
    animation: fadeUp 0.6s ease forwards;
  }
}
```

For JS animations:
```js
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!reduceMotion) {
  gsap.from('.hero', { opacity: 0, y: 40, duration: 0.8 });
}
// GSAP helper:
gsap.defaults({ duration: reduceMotion ? 0 : 0.8 });
```

---

## CDN / Install Recipes

**HTML CDN:**
```html
<!-- GSAP + ScrollTrigger -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js"></script>

<!-- Anime.js -->
<script src="https://cdn.jsdelivr.net/npm/animejs@3/lib/anime.min.js"></script>

<!-- dotLottie (ESM) -->
<script type="module">
  import { DotLottie } from 'https://cdn.jsdelivr.net/npm/@lottiefiles/dotlottie-web/+esm';
  new DotLottie({ canvas: document.getElementById('lottie'), src: 'animation.lottie', loop: true, autoplay: true });
</script>
```

**npm (React/Next.js):**
```bash
npm install framer-motion
npm install gsap
npm install @react-three/fiber three @react-three/drei
npm install @lottiefiles/dotlottie-react
```

---

## Easing Reference

| Feel | CSS | GSAP |
|---|---|---|
| Natural decelerate | `cubic-bezier(0.22, 1, 0.36, 1)` | `power3.out` |
| Spring overshoot | `cubic-bezier(0.34, 1.56, 0.64, 1)` | `back.out(1.7)` |
| Sharp snap | `cubic-bezier(0.85, 0, 0.15, 1)` | `expo.inOut` |
| Elastic | chain keyframes | `elastic.out(1, 0.3)` |
| Scrub / linear | `linear` | `none` |

---

## Pre-Delivery Checklist

**Performance:**
- [ ] Only `transform` and `opacity` are animated
- [ ] `will-change` applied only where profiled to help
- [ ] `requestAnimationFrame` used for JS animation loops
- [ ] Heavy libraries are lazy-loaded or code-split
- [ ] Canvas particle count capped at 60 for mobile

**Accessibility:**
- [ ] `@media (prefers-reduced-motion: reduce)` on every animation
- [ ] Critical content visible without animation (no `opacity: 0` left in place)
- [ ] Animated elements don't convey information solely through motion

**Quality:**
- [ ] Animations have stagger/choreography, not all fire simultaneously
- [ ] Easing curves match emotional tone
- [ ] No animation runs indefinitely without user control (except subtle ambient loops)
- [ ] Scroll-triggered animations use `unobserve()` or `{ once: true }` after trigger

**Cross-browser:**
- [ ] CSS `animation-fill-mode: both` used to prevent flash-of-invisible
- [ ] `gsap.registerPlugin(ScrollTrigger)` called before any ScrollTrigger usage
- [ ] `overflow: hidden` on parent containers for clip/reveal effects
