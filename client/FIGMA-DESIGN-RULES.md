# Figma → Code Design System Rules

Rules for turning Figma designs (via the Figma MCP) into code for this Vue 3 client.
Figma MCP output (React + Tailwind) is a **reference only**. Always translate it into the patterns below.

## 1. Tokens

**Current state:** there are no design tokens. Colors, spacing and type are hard-coded hex/rem values in
`src/App.vue` (global `<style>`) and in each component's `<style scoped>`. No CSS variables, no
Tailwind, no token build step.

**De-facto palette** (Tailwind's slate + status colors, by frequency of use):

| Role | Value | Use |
|---|---|---|
| Text strong | `#0f172a` | Headings, stat values |
| Text body | `#334155` / `#1e293b` | Table cells, body |
| Text muted | `#64748b` | Labels, subtitles |
| Text subtle | `#94a3b8` | Placeholders, hints |
| Border | `#e2e8f0` (hover `#cbd5e1`) | Cards, tables, inputs |
| Surface alt | `#f8fafc` / `#f1f5f9` | Page bg, table header, hover |
| Primary | `#2563eb` (soft `#eff6ff`) | Active nav, links, primary buttons |
| Chart blue | `#3b82f6` | SVG chart series |
| Success | `#10b981` / `#059669`, badge `#d1fae5` on `#065f46` | |
| Warning | `#f59e0b` / `#ea580c`, badge `#fed7aa` on `#92400e` | |
| Danger | `#ef4444` / `#dc2626`, badge `#fecaca` on `#991b1b` | |
| Info | badge `#dbeafe` on `#1e40af` | |

**Type:** `'Inter', -apple-system, ...` on `body` (Inter is **not loaded**; system fonts render).
Sizes: page title `1.875rem`/700, card title `1.125rem`/700, body `0.875–0.938rem`, labels `0.75rem` uppercase.
**Shape:** radius `6px` (buttons, badges), `8px` (alerts), `10px` (cards). Shadow on hover only: `0 4px 12px rgba(0,0,0,0.06)`.

**Rule:** map Figma variables to the closest value above. If you add new tokens, define them as CSS
custom properties in `:root` inside `App.vue` (see the `saas-ui-redesign` skill for the target token set)
rather than adding new hex values.

## 2. Components

- **Location:** routed pages in `src/views/*.vue`; shared pieces in `src/components/*.vue`; logic in
  `src/composables/use*.js`; formatting in `src/utils/`.
- **Architecture:** single-file components, Composition API. Views and App use `export default { setup() }`;
  the newer components (modals, `ProfileMenu`, `LanguageSwitcher`) use `<script setup>` with
  `defineProps` / `defineEmits`. Match the file you're editing. Shared state is singleton refs in composables (`useFilters`, `useI18n`, `useAuth`).
- **Modals** (`*DetailModal.vue`, `TasksModal.vue`) use `<Teleport to="body">`, a `.modal-overlay`
  (`position: fixed`, `rgba(0,0,0,0.5)`) and emit `close`. Copy an existing modal for new ones.
- **No Storybook or component docs.** Reusable global classes in `App.vue` act as the component library:
  `.page-header`, `.card` / `.card-header` / `.card-title`, `.stats-grid` / `.stat-card` (+ `.warning`,
  `.success`, `.danger`, `.info`), `.table-container`, `.badge.<status>`, `.loading`, `.error`.

```vue
<template>
  <div class="page-header">
    <h2>{{ t('inventory.title') }}</h2>
    <p>{{ t('inventory.subtitle') }}</p>
  </div>
  <div class="card">
    <div class="card-header"><h3 class="card-title">...</h3></div>
    <div class="table-container"><table>...</table></div>
  </div>
</template>
```

**Rule:** before creating a component from a Figma frame, reuse these global classes and existing
components (`FilterBar`, `LanguageSwitcher`, `ProfileMenu`). All `.vue` work goes through the
`vue-expert` subagent (root CLAUDE.md).

## 3. Frameworks and build

- Vue 3.4 + vue-router 4 (`src/main.js`, history mode) + axios (`src/api.js`).
- Vite 8 with `@vitejs/plugin-vue`, dev server on port 3000. No CSS preprocessor, PostCSS, or Tailwind.
- Don't add UI or CSS libraries to turn Figma output into code; write plain scoped CSS.

## 4. Assets

- No `public/` or `src/assets/` folder, and no images or fonts in the repo. There's no CDN configuration.
- If a design needs an image, add it under `src/assets/` and import it so Vite hashes it. Don't use
  remote Figma asset URLs in committed code, because they expire and the repo is public.

## 5. Icons

- No icon library or icon files. Icons are **inline SVG** written directly in templates.
- Common sizes: `20×20` (modal close), `18×18` (menu), `14×14` (small actions), `48×48` (empty states).
- Pattern: `fill="none"`, `stroke="currentColor"` so color comes from CSS.

```html
<svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
  <path d="M15 5L5 15M5 5l10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>
```

**Rule:** export Figma icons as SVG and inline them with `currentColor`. No emojis in the UI.

## 6. Styling

- **Global:** `App.vue` `<style>` (unscoped) holds the reset, body type, nav, and all shared classes.
- **Local:** every other component uses `<style scoped>`. Class names are plain kebab-case (BEM-lite:
  `.stat-card`, `.stat-label`, `.card-header`). No CSS Modules or CSS-in-JS.
- **Layout:** CSS Grid (`.stats-grid` with `repeat(auto-fit, minmax(280px, 1fr))`) and Flexbox.
  Content max width `1600px`, padding `1.5rem 2rem`.
- **Responsive:** there are **no `@media` queries**. Responsiveness comes only from `auto-fit` grids and
  `.table-container { overflow-x: auto }`. Add breakpoints when a Figma design has mobile frames
  (suggested: 1024px and 640px).
- **Charts:** custom SVG drawn in components (for example the donut in `Dashboard.vue`). No chart library.

## 7. Project structure

```
client/
├── index.html, vite.config.js, package.json
└── src/
    ├── main.js            # router: / inventory orders demand spending reports
    ├── App.vue            # shell + global styles
    ├── api.js             # all HTTP calls
    ├── views/             # one file per route
    ├── components/        # shared UI + modals
    ├── composables/       # useFilters, useI18n, useAuth
    ├── locales/en.js, ja.js
    └── utils/currency.js  # formatCurrency (USD/JPY by locale)
```

## Checklist for implementing a Figma frame

1. Read the frame with `get_design_context` and get a screenshot to compare against.
2. Map colors, type and spacing to section 1. Don't add new hex values without tokens.
3. Reuse the global classes and existing components. Put new pieces in `components/`.
4. Put all text in `locales/en.js` **and** `ja.js` and use `t('...')`. Never hard-code strings.
5. Format money with `formatCurrency` from `utils/currency.js`.
6. Use inline SVG icons with `currentColor`. Use unique `v-for` keys, never the index.
7. Keep files under 200 lines (`Dashboard.vue` and `Spending.vue` already break this, so split them, don't add to them).
8. Verify with the Playwright MCP at `http://localhost:3000` in English and Japanese.
