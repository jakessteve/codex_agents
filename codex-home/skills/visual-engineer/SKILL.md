---
name: visual-engineer
description: Native UI/UX design intelligence for Codex CLI — style selection, color palettes, typography, chart guidance, landing patterns, UX rules, design system generation, and stack-specific guidelines.
---

# Visual Engineer — Codex CLI Design Intelligence

**Role**: UI/UX critique, design system generation, and visual consistency enforcement.  
**Scope**: All frontend stacks (React, Next.js, Vue, Svelte, SwiftUI, Flutter).  
**Policy**: Use the strongest supported model available; fall back to the nearest supported model on rejection.  
**Pre-work**: Before generating or modifying design tokens, call `codex_knowledge_project_context` to check existing tokens and `codegraph_callers_callees` to locate all components consuming a token.

---

## 1. Style Selection by Product Type

| Product Type | Recommended Style | Rationale |
|--------------|-------------------|-----------|
| SaaS / B2B | Clean, minimal, high whitespace | Trust, clarity, reduces cognitive load for power users |
| E-commerce | Warm, image-forward, card-heavy | Emotional engagement, scan-ability, conversion focus |
| Fintech | Dark mode optional, strict grid, high contrast | Security perception, precision, regulatory readability |
| Social / Community | Vibrant, rounded, fluid layouts | Approachability, frequent-use comfort, personality |
| Developer Tools | Monospace accents, dense info, keyboard hints | Efficiency, scan-ability, power-user density |
| Healthcare | Soft pastels, large touch targets, calm | Anxiety reduction, accessibility, trust |
| Education | Friendly, progressive disclosure, color-coded | Engagement, hierarchy, learning scaffolding |

**Rule**: Always align the visual density with the user's average session length. Short sessions → high contrast CTAs; long sessions → low eye strain.

---

## 2. Color Palette Generation

Generate semantic tokens by product mood. All values are hex; adapt to `rgba`, `hsl`, or platform equivalents as needed.

| Mood | Primary | Secondary | Accent | Background | Surface | Text | Muted |
|------|---------|-----------|--------|------------|---------|------|-------|
| Professional | `#0F172A` | `#334155` | `#3B82F6` | `#FFFFFF` | `#F8FAFC` | `#1E293B` | `#94A3B8` |
| Playful | `#7C3AED` | `#C084FC` | `#F59E0B` | `#FFFBEB` | `#FEF3C7` | `#431407` | `#B45309` |
| Calm | `#0D9488` | `#5EEAD4` | `#F97316` | `#F0FDFA` | `#CCFBF1` | `#134E4A` | `#0F766E` |
| Bold | `#DC2626` | `#991B1B` | `#FBBF24` | `#FFFFFF` | `#FEF2F2` | `#450A0A` | `#B91C1C` |
| Dark Mode | `#E2E8F0` | `#94A3B8` | `#38BDF8` | `#0F172A` | `#1E293B` | `#F1F5F9` | `#64748B` |

**Tailwind config snippet** (extend theme):
```js
colors: {
  primary:   { DEFAULT: '#0F172A', light: '#334155' },
  secondary: { DEFAULT: '#334155', light: '#64748B' },
  accent:    { DEFAULT: '#3B82F6', light: '#60A5FA' },
  surface:   { DEFAULT: '#F8FAFC', dark: '#1E293B' },
  muted:     '#94A3B8',
}
```

**Accessibility rule**: Every foreground/background pair must achieve WCAG 2.1 AA (4.5:1 for normal text, 3:1 for large text). Use an online contrast checker or platform tool before finalizing.

---

## 3. Typography Pairings

| Heading Font | Body Font | Mood | CSS Import / Tailwind |
|--------------|-----------|------|----------------------|
| Inter | Inter | Neutral, modern | `font-sans` (default) |
| Space Grotesk | Inter | Tech, editorial | `@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;600&display=swap');` |
| Playfair Display | Source Sans 3 | Luxury, editorial | `font-serif` headings, `font-sans` body |
| DM Sans | DM Sans | Friendly, rounded | `font-sans` with rounded tracking |
| JetBrains Mono | Inter | Developer, precise | `font-mono` for code, `font-sans` for prose |

**Scale (Major Third — 1.25 ratio)**:
```css
--text-xs: 0.75rem;   /* 12px */
--text-sm: 0.875rem;  /* 14px */
--text-base: 1rem;    /* 16px */
--text-lg: 1.125rem;  /* 18px */
--text-xl: 1.25rem;   /* 20px */
--text-2xl: 1.5rem;   /* 24px */
--text-3xl: 1.875rem; /* 30px */
--text-4xl: 2.25rem;  /* 36px */
```

**Line heights**: Headings `1.2`, body `1.6`, UI labels `1.4`. Max line length: `65ch` for body text.

---

## 4. Chart Type Selection

| Data Goal | Chart Type | Accessibility Grade | Notes |
|-----------|------------|---------------------|-------|
| Trend over time | Line | A | Use distinct stroke patterns + color |
| Part-to-whole | Donut | B | Limit to 5 slices; label directly |
| Comparison (categories) | Bar (vertical) | A | Always start y-axis at 0 |
| Comparison (ranking) | Bar (horizontal) | A | Best for long labels |
| Distribution | Histogram / Box | B | Add mean/median annotations |
| Correlation | Scatter | C | Provide table fallback |
| Geographic | Choropleth | C | Never use as sole data source |
| Proportion (simple) | Pie | D | Avoid; use donut or bar instead |

**Accessibility mandates**:
- Every chart needs a text summary (`<figcaption>` or `aria-describedby`).
- Color must not be the sole encoding; add patterns, labels, or hatching.
- Interactive charts must be keyboard navigable.

---

## 5. Landing Page Patterns

| Product Type | Section Order | CTA Placement Strategy |
|--------------|---------------|--------------------------|
| SaaS | Hero → Social proof → Features → Pricing → FAQ → Footer | Primary CTA above fold; secondary CTA after social proof |
| E-commerce | Hero → Categories → Featured → Testimonials → Newsletter | Sticky add-to-cart; urgency badges near price |
| Fintech | Hero → Security signals → Features → Calculator/Tool → Footer | Trust CTA ("Get started — no credit check") above fold |
| Developer tool | One-liner → Install command → Features → Docs link → Footer | Copy-paste install snippet as primary CTA |
| Mobile app | Hero → App store badges → Feature carousel → Reviews | Dual CTA (App Store + Play Store) above fold |

**Rules**:
- Hero headline must communicate value in ≤10 words.
- First CTA must be visible without scrolling on a 13-inch display.
- Repeat primary CTA every 2–3 sections on long pages.

---

## 6. UX Do/Don't Guidelines

| # | Rule | Do | Don't |
|---|------|-----|-------|
| 1 | Contrast | Ensure 4.5:1 text contrast | Use light gray on white for body text |
| 2 | Touch targets | Make interactive elements ≥44×44 dp/px | Crowd buttons or links |
| 3 | Error messages | State what happened + how to fix | Show raw error codes alone |
| 4 | Forms | Label every input; group related fields | Rely solely on placeholder text |
| 5 | Loading | Show skeletons or progress, not spinners alone | Leave screen blank during load |
| 6 | Navigation | Keep primary nav ≤7 items | Nest more than 2 levels in top nav |
| 7 | Modals | Focus trap + close on Escape + overlay click | Open modal without return path |
| 8 | Autoplay | Never autoplay sound; pause video on hidden | Autoplay video with audio |
| 9 | Motion | Respect `prefers-reduced-motion` | Animate layout shifts without fallback |
| 10 | Links | Underline or distinct color for inline links | Color-only link differentiation |
| 11 | Tables | Freeze header row; zebra stripe optional | Horizontal scroll on small tables |
| 12 | Search | Show results on type; debounce ≥150 ms | Require submit for every query |
| 13 | Empty states | Explain why empty + next action | Show blank screen or "No data" |
| 14 | Confirmation | Destructive actions require explicit confirm | Delete on single click without warning |
| 15 | Feedback | Toast/alert for async outcomes | Silent failures |
| 16 | Consistency | Reuse the same component for the same concept | Invent new patterns for standard flows |
| 17 | Hierarchy | One H1 per page; logical heading order | Skip heading levels for styling |
| 18 | Inputs | Show format requirements before submission | Reject on blur without explanation |
| 19 | Images | Always provide `alt` text; decorative use `alt=""` | Omit alt or use filename as alt |
| 20 | Focus | Visible focus ring on all interactive elements | Remove outlines globally (`outline: none`) |

---

## 7. Design System Generation Protocol

Run this protocol when asked to generate or refactor a design system. Before step 1, query `codex_knowledge_project_context` for existing tokens and `codegraph_callers_callees` on token symbols to understand blast radius.

1. **Audit**: Inventory all existing colors, fonts, spacing, and components. Flag duplicates and orphans.
2. **Tokenize**: Create a single source of truth for primitives (colors, typography, spacing, shadows, radii, z-index).
3. **Semantic layer**: Map primitives to semantic names (`--color-text-primary`, `--color-surface-error`).
4. **Component layer**: Build components from semantic tokens only; never hardcode primitives in components.
5. **Document**: Add usage rules, do/don't examples, and prop tables for every component.
6. **Validate**: Run visual regression or snapshot tests; check contrast ratios programmatically.
7. **Distribute**: Export tokens to all target platforms (CSS, Tailwind, iOS, Android, Figma JSON).

**Spacing scale** (4px base):
```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-10: 2.5rem;  /* 40px */
--space-12: 3rem;    /* 48px */
--space-16: 4rem;    /* 64px */
```

---

## 8. Stack-Specific Guidelines

### React / Next.js
- Use CSS Modules or Tailwind; avoid inline styles for theming.
- Prefer `next/font` for self-hosted fonts and zero layout shift.
- Use `prefers-reduced-motion` media query in global CSS; respect it in Framer Motion via `reducedMotion` prop.
- Image optimization: always use `next/image` with explicit `width`/`height` to prevent CLS.

### Vue
- Use CSS custom properties in `:root` for theming; bind to component props via `computed` style objects only when dynamic.
- Keep `<style scoped>` for component-level overrides; global tokens in a dedicated `theme.css`.
- Use `v-bind()` in CSS sparingly; it breaks static extraction.

### Svelte
- Leverage CSS custom properties natively; Svelte scopes styles automatically.
- Use `style:property` directives for dynamic values instead of inline style strings.
- Keep design tokens in a `$lib/tokens.js` (or `.ts`) module for JS/TS access and tree-shaking.

### SwiftUI
- Use `Color` and `Font` extensions for semantic tokens; avoid raw hex strings in views.
- Respect Dynamic Type by using `.font(.body)`, `.font(.headline)`, etc., rather than fixed sizes.
- Test color contrast in both Light and Dark Mode; use `.preferredColorScheme` previews.
- Minimum touch target: 44×44 points. Use `.frame(minWidth:minHeight:)` on small tappable elements.

### Flutter
- Define tokens in `ThemeData` inside `MaterialApp`; access via `Theme.of(context)`.
- Use `ColorScheme.fromSeed()` for automatic harmonious palettes.
- Ensure text contrast with `ThemeData.contrastLevel` and `ColorScheme` roles (`onPrimary`, `onSurface`).
- Minimum touch target: 48×48 logical pixels. Use `Material` or `InkWell` hit areas.

---

## Execution Checklist

Before approving any visual change:
- [ ] Contrast ratios meet WCAG AA.
- [ ] Touch targets meet platform minimums.
- [ ] `prefers-reduced-motion` is respected.
- [ ] No orphaned tokens; all colors/spacing reference the design system.
- [ ] `codegraph_impact_analysis` run on changed token paths to identify affected components.
- [ ] `codex_knowledge_project_context` checked for existing design conventions.

**Codex model policy**: Use the strongest supported model available to the runtime. If a model name is rejected, fall back to the nearest supported model rather than failing.
