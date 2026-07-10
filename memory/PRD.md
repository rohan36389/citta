# CittaAI NextGen Experience — PRD

## Original Problem Statement
Redesign the existing CittaAI website (https://cittaai.com) into a flagship
enterprise AI experience while preserving 100% of the original information.
Same content. Completely elevated experience.

## User Choices (from ask_human)
- Content source: Scrape from https://cittaai.com and build fresh in existing /app React setup
- Stack: React (CRA) + JavaScript + Tailwind (kept existing, no Next.js migration)
- 3D: Full React Three Fiber hero centerpiece + particles + orbit rings
- Backend: Pure frontend (no API endpoints)
- AI Assistant: UI-only placeholder chat widget (no LLM integration)

## Tech Stack
- React 19 + React Router v7 + CRACO (existing)
- Tailwind CSS v3 with custom brand tokens
- Framer Motion 11 (animations, scroll reveals)
- React Three Fiber v9 + @react-three/drei v9.121 + three v0.161 (3D hero)
- Fonts: Space Grotesk (display), Inter (body), JetBrains Mono (code/labels)
- Lucide React icons

## Content Lock
All copy is sourced verbatim from cittaai.com and centralised in
`/app/frontend/src/data/content.js`. Any content edits must happen there.

## Architecture / Files
- App shell: `src/App.js` (routes) + `src/components/{Navbar,Footer,ScrollToTop,AIAssistant,SectionHeader}.jsx`
- 3D hero: `src/components/HeroCanvas.jsx` (icosahedron + orbit rings + orbiting nodes + sparkles)
- Home sections: `src/sections/{Hero,Challenge,WhoWeAre,Stack,Products,Services,Solutions,Results,Trust,Why}.jsx`
- Pages: `src/pages/{Home,Contact,Services,ProductPage,SolutionPage}.jsx`
- Design tokens: `tailwind.config.js` + `src/index.css` (glassmorphism, aurora, grid overlay, gradient text, chips, buttons)

## Routes
- `/` — Home (all sections)
- `/contact` — Contact page with form (client-side alert on submit)
- `/services` — Services page
- `/products/:slug` — marktech | agentic | lms | pharma | govtech
- `/solutions/:slug` — ecommerce | real-estate | pharma | smart-cities

## Design System (verbatim from prompt)
- Dark: #050816, #0D1326  ·  Light: #FFFFFF, #F8FAFC, #F1F5F9
- Primary #2D7FF9  ·  Accent #00E5FF  ·  Secondary #5B5FEF
- Alternating dark/light section rhythm (Hero→Challenge dark, WhoWeAre light,
  Stack dark, Products light, Services dark, Solutions light, Results dark,
  Trust light, Why dark)
- Bento & asymmetric grids, editorial hero, animated marquee for client logos
- Glassmorphism (blur 18–22px), aurora blobs, grid overlay, gradient text
- Motion: staggered entrances, hover lift on cards, scroll-triggered reveals

## What's Been Implemented (2026-01)
- 3D interactive hero with distorted icosahedron, wireframe shell, 3 orbit rings,
  10+6 orbiting nodes, 90 sparkles, mouse-parallax rotation
- Glass sticky navbar with mobile menu, gradient logo mark, hover underlines
- Full homepage: 10 unique sections, each with its own visual identity
- Interactive Industry OS tab-panel selector (Solutions)
- Animated client-logo marquee (26 slots) with mask fade
- Floating AI Assistant chat widget with suggestion chips (UI-only)
- Contact page with glass form
- Product and Solution detail pages with content-locked data
- Reduced-motion support, focus-visible outlines, semantic landmarks

## Testing Status
- testing_agent_v3 iteration 1: **18/18 passed**
- No runtime errors, no console errors
- Mobile responsive verified at 390px

## Backlog / P1
- Wire Contact form to a FastAPI `/api/contact` endpoint + Mongo storage
- Enable working AI Assistant via Emergent LLM key (Claude/GPT)
- Deep sub-pages for each Product/Solution with case studies scraped verbatim
- Real client logo SVGs (currently rendered as text badges in marquee)
- Lighthouse pass — code-split R3F further, preload fonts, add sitemap.xml

## Backlog / P2
- Blog / insights section
- Interactive Neural Knowledge Graph visualisation in the Stack section
- Case study modal for the Results section (Read Case Study CTA)
- i18n scaffolding

## Next Tasks (if user continues)
1. Add real client logos (SVG upload) to replace text placeholders in marquee
2. Wire contact form to backend + email/CRM webhook
3. Populate deeper product/solution pages with additional scraped sections
