# CittaAI — Living Intelligence Rebuild (v2)

## Original Problem Statement
Redesign cittaai.com as an enterprise "Living Intelligence" experience.
100% content preservation from the Master Prompt v2 Section 2.
Real photos of team, real logo, real certification badges.
Same content. Completely elevated experience.

## User Choices
- Content source: Master Prompt v2 (Section 2) + real photos uploaded by user
- Tech stack: React (CRA) + JS + Tailwind (kept existing) — NOT Next.js/TS
- 3D: Enhanced R3F node network + connecting lines + pulsing data packets (46 nodes, 28 packets)
- Backend: Pure frontend (no API endpoints; contact form client-side success)
- Services sub-pages: `{{PENDING_CONTENT}}` placeholder as instructed
- Rebuild: Full rebuild from scratch (per user)

## Tech Stack
- React 19 + React Router v7 + CRACO
- Tailwind CSS 3 with Living Intelligence tokens + CSS variables for per-page accents
- Framer Motion 11 (staggered entrances, hover, scroll reveals)
- React Three Fiber v9 + drei v9.121 + three v0.161 (hero node-network scene)
- Fonts: Geist Sans / Inter / JetBrains Mono
- Lucide React icons

## Design System — "Living Intelligence"
- Dark: `#0A0F1E` `#0F172A`  ·  Light: `#F8FAFC` `#FFFFFF`
- Text: `#0F172A` / `#F1F5F9` / muted `#64748B`  ·  Border subtle `rgba(148,163,184,0.15)`
- Brand: `#2563EB` (blue) / `#60A5FA` (light)
- Per-page accents (drive `--accent`, `--accent-light`, `--accent-grad` at `<html>` level):
  - WhatsApp Marketing — green `#16A34A → #4ADE80`
  - Influencer Marketing — purple `#9333EA → #C084FC`
  - E-Commerce OS — blue
  - Real Estate OS — indigo
  - Pharma OS — pink `#DB2777 → #F472B6`
  - Smart Cities OS — teal `#0D9488 → #5EEAD4`
  - Education OS — violet `#7C3AED → #A78BFA`
  - Enterprise AI OS — cyan `#0891B2 → #67E8F9`
- Glass: dark `rgba(255,255,255,0.04)` @ blur16, strong @ blur22, light `rgba(255,255,255,0.6)` @ blur16
- Motion: 4–6° tilt on cards, staggered fade+rise entrances (60–80ms), animated stat counters, gradient drift on hero orbs, marquee client logos

## Content Lock
All copy lives in `/app/frontend/src/data/content.js` — single source of truth.
Structured as: `BRAND`, `CONTACT`, `NAV`, `HOMEPAGE`, `PAGE_CONFIGS` (8 product/solution configs), `ACCENT`, `RECOGNITION`, `CASESTUDIES`, `ABOUT`, `CONTACT_PAGE`, `FOOTER`.

## Real Assets (uploaded, cropped from user photos)
- `/assets/brand/logo-square.png` (favicon + navbar), `/assets/brand/logo-wide.png` (unused)
- `/assets/team/` — 7 headshot JPGs: vinay-velivela, saladi-chandra-balaji, akhil-reddy, ganesh-gandhi-vadalani, harish-nerati, aravind-reddy, parvatha-mohan
- `/assets/badges/` — iso.png, msme.png, startup-india.png (cropped from footer screenshot)

## Site Architecture / Routes
```
/                              → Home (11 sections)
/products/:slug                → PSPage (kind=product)
   whatsapp-marketing (green) · influencer-marketing (purple)
/solutions/:slug               → PSPage (kind=solution)
   ecommerce-os (blue) · real-estate-os (indigo) · pharma-os (pink)
   smart-cities-os (teal) · education-os (violet) · enterprise-ai-os (cyan)
/services                      → index (5 service cards + PENDING_CONTENT note)
/services/:slug                → ServiceSubPage ({{PENDING_CONTENT}})
/recognition                   → Awards page (AP MSME + HYBIZ TV)
/case-studies                  → 3 case cards with chart mocks
/about                         → About with signature team wow moment
/contact                       → Form (client-side success, no backend)
```

## Component Inventory (Section 5 of brief)
1. `Navbar` — sticky, glass-on-scroll, dropdown mega-menus, language, Say Hello! CTA
2. `Footer` — full lockup, real logo, 4 columns, contact, socials, ISO/MSME/Startup India badges
3. `SectionHeader` — chip + H2 + sub/lead, light+dark variants
4. `StatValue` — count-up on IntersectionObserver (preserves non-numeric parts like `₹`, `+`, `→`)
5. `CapabilityIcon` — 60+ capability→lucide-icon mapping, accent-tinted background
6. `HeroCanvas` — 46-node fibonacci sphere + distance-thresholded lines + 28 pulsing instanced packets
7. `BackToTop` — floating button (bottom-6 LEFT-6 to avoid Emergent badge collision)
8. `ScrollToTop` — resets scroll on route change, resets per-page --accent CSS vars
9. `PSPage` — shared template for all 8 product/solution pages (config-driven)
10. `TeamCard` (About) — scale-1.04 on hover, animated underline, LinkedIn slide-in for Akhil / Aravind

## What's Been Implemented (2026-01)
- Full 12-page redesign at production quality
- Signature 3D hero with node network + data packet flows (60 FPS)
- Interactive Solutions tabs; alternating dark/light section rhythm
- 8 product/solution pages driven by ONE template with per-page accent themes
- Animated stat counters (100+, 50M+, 1B+, 99.9%, ₹3.5 Cr+, 2K→37K, 50+ tons, etc.)
- About page team wow moment with all 7 real headshots
- Recognition page with two awards (AP MSME + HYBIZ TV)
- Contact form with Inquiry Type dropdown + reCAPTCHA placeholder + client-side success
- Footer with real ISO / MSME / Startup India badges
- Full mobile responsiveness, focus-visible outlines, reduced-motion support

## Testing Status
- testing_agent_v3 iteration 2: **success_rate = 94%**
- 0 backend issues · 0 critical frontend issues · zero console/runtime errors
- Fixes applied post-report:
  - BackToTop moved to `bottom-6 left-6` (was overlapped by Emergent badge)
  - LinkedIn hover on team cards: full opacity + brand-blue shadow
  - About team second row: `grid-cols-2` on mobile (was 1-col)

## MOCKED / Non-functional flows
- **Contact form** → success is client-side only (no backend endpoint). MOCKED.
- **AI Assistant** → removed in v2 (was UI-only placeholder in v1).
- **LinkedIn URLs for Akhil / Aravind** → `#` placeholder pending real URLs.
- **Certification badge images** → cropped from user's footer screenshot; production may want higher-resolution vector assets.

## Backlog / P1
- Wire Contact form to a FastAPI `/api/contact` endpoint + Mongo storage + email/CRM webhook
- Replace `#` LinkedIn hrefs with real profile URLs (Akhil / Aravind)
- Fill Services sub-page content for Data Engineering / Enterprise AI / AI Strategy / MarTech 360 / Consulting
- Upload higher-resolution certification SVGs

## Backlog / P2
- Real ceremony photos (AP MSME + HYBIZ TV) — currently abstract SVG art placeholders
- Blog / Careers pages (footer links stubbed as `#`)
- Deep case-study pages (currently 3 tiles only)
- Language selector functionality (currently UI-only "English")

## Next Tasks (if user continues)
1. Provide real LinkedIn URLs for Akhil Reddy & Aravind Reddy
2. Provide real award-ceremony photos for Recognition page
3. Draft copy for the 5 Services sub-pages so `{{PENDING_CONTENT}}` can be replaced
4. Choose whether Contact form should POST to a backend or a form service (Formspree / SendGrid)
