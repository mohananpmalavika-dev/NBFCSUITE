# EDS-005: Design Tokens & Theme System

**Version:** 1.0

**Priority:** ⭐⭐⭐⭐⭐

**Owner:** Platform Team

---

## Purpose

Design tokens are the single source of truth for the entire UI.

No developer should ever write:

```
color:#2563eb;padding:14px;border-radius:11px;
```

Instead they use tokens:

```
color.primary.600
spacing.4
radius.lg
```

When branding changes, only tokens change and the entire platform updates.

---

## Design Token Hierarchy

```
Global Tokens │ Semantic Tokens │ Component Tokens │ Page Tokens
```

---

## Token Structure

```
packages/design-system/tokens/
  color.ts
  spacing.ts
  radius.ts
  typography.ts
  shadows.ts
  motion.ts
  size.ts
  z-index.ts
  breakpoints.ts
```

---

## Color System

Everything comes from a single palette.

### Brand Colors

```
Primary Blue
```

```
50 100 200 300 400 500 600 700 800 900
```

### Secondary

```
Slate
```

### Accent

```
Cyan
```

### Success

```
Green
```

### Warning

```
Amber
```

### Danger

```
Red
```

### Information

```
Sky
```

---

## Neutral Scale

```
0 25 50 100 200 300 400 500 600 700 800 900 950
```

Used for backgrounds, borders, text, cards, tables.

---

## Semantic Colors

Use semantic tokens instead of raw colors:

```
background.default
background.surface
background.elevated
background.sidebar
background.header
background.drawer
background.dialog

text.primary
text.secondary
text.muted
text.inverse
text.success
text.warning
text.error

border.default
border.light
border.focus
border.error
border.success
```

---

## Spacing Scale

Everything follows an 8-point grid.

```
0 2 4 8 12 16 24 32 40 48 64 80 96
```

No arbitrary spacing values.

---

## Radius

```
none xss xs sm md lg xl 2xl pill full
```

Default: `lg`

---

## Shadows

```
xs sm md lg xl 2xl
```

Use:

- Cards → `sm`
- Dialogs → `xl`
- Dropdowns → `lg`

---

## Typography

Font:

```
Inter
```

Fallback:

```
system-ui
```

---

## Text Scale

```
display-xl
display-lg
h1
h2
h3
h4
body-l
body-m
body-s
caption
label
code
```

---

## Font Weight

```
regular
medium
semibold
bold
```

---

## Line Heights

Use a consistent scale.
No manual line-height values in components.

---

## Icon Tokens

Icon library:

```
Lucide
```

Sizes:

```
12 16 18 20 24 28 32 40
```

---

## Motion

Animation:

```
fast
normal
slow
```

Timing:

```
100ms 150ms 200ms 300ms
```

Curves:

```
standard
entrance
exit
emphasized
```

---

## Z-Index

```
base
header
sidebar
dropdown
drawer
modal
toast
tooltip
ai-panel
```

Never hardcode z-index values in components.

---

## Breakpoints

```
Mobile 0–767
Tablet 768–1023
Laptop 1024–1439
Desktop 1440–1919
Ultra 1920+
```

---

## Component Tokens

Each component uses typed semantic tokens.

Example: Button

```
button.primary.background
button.primary.text
button.primary.hover
button.primary.active
button.primary.disabled
```

Same structure applies for:

- Cards
- Inputs
- Tables
- Drawers
- Modals
- Tabs
- Charts

---

## Theme System

Every tenant can create themes:

- `ICICI Theme` → Primary Orange, Accent Blue
- `Federal Theme` → Blue, Green
- `HDFC Theme` → Red, Blue

Application code does not change; only tokens change.

---

## Dark Theme

Every token has light and dark values.

No component should contain conditional dark-mode logic.
Components consume semantic tokens.

---

## High Contrast

Accessibility mode uses separate semantic tokens.

---

## Banking Branding

Every tenant can configure:

- Logo
- Primary Color
- Accent Color
- Font
- Favicon
- Login Screen
- Email Theme
- Report Header
- PDF Theme

without changing the application.

---

## Token Naming Convention

```
color.primary.600
spacing.4
radius.lg
font.body.md
shadow.md
motion.fast
icon.20
```

Never use:

```
blueColor
radius12
padding16
```

---

## Token Delivery

Generate tokens automatically as:

- JSON
- TypeScript
- CSS variables
- Tailwind config

---

## Example Tailwind Integration

```js
theme: {
  extend: {
    colors: {
      primary: 'var(--color-primary)',
      surface: 'var(--surface)',
      border: 'var(--border)',
    },
  },
}
```

Components should never hard-code values.

---

## Design Token Governance

Every new token must answer:

- Is an existing token sufficient?
- Is this semantic rather than brand-specific?
- Will it work across light, dark, and branded themes?
- Does it reduce duplication?

If not, do not add it.

---

## Folder Structure

```
packages/design-system/tokens/
  colors.ts
  spacing.ts
  typography.ts
  radius.ts
  shadows.ts
  motion.ts
  breakpoints.ts
  zIndex.ts
  themes/
    default.ts
    dark.ts
    highContrast.ts
  index.ts
```

---

## Quality Checklist

A design token system is complete when:

- No hard-coded colors exist in UI components.
- No hard-coded spacing, radius, or shadows are used.
- Themes can switch at runtime.
- Multiple tenant brands are supported.
- Light, dark, and high-contrast modes use the same semantic API.
- Tokens can be exported for React, Tailwind, and CSS.

---

## Deliverable Status

- ✅ EDS-001 Design Principles — Complete
- ✅ EDS-002 Information Architecture — Complete
- ✅ EDS-003 Enterprise Navigation — Complete
- ✅ EDS-004 Enterprise App Shell — Complete
- ✅ EDS-005 Design Tokens & Theme System — Complete
- ⏳ EDS-006 Component Library — Next

---

## What Comes Next

The next deliverable is one of the largest in the entire platform:

### EDS-006 — Enterprise Component Library

This will define approximately 120–150 reusable enterprise components organized into:

- Foundations (buttons, typography, icons)
- Form controls (inputs, selects, date pickers, upload, rich text)
- Data display (tables, cards, KPI widgets, charts)
- Navigation (tabs, breadcrumbs, pagination, menus)
- Feedback (alerts, toasts, progress, skeletons)
- Workflow (approval cards, timelines, comments, activity feeds)
- Layout (drawers, dialogs, split panes, resizable panels)
- Banking-specific components (Customer 360 card, Loan Summary card, GL Account selector, Branch selector, Approval timeline, Document checklist)

Once EDS-006 is complete, the platform will have a reusable UI foundation that every ARTH.OS module can build upon with consistency and minimal duplication.
