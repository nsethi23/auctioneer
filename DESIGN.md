# Design

## Visual Theme

Auctioneer uses a dark, focused workbench theme. The physical scene is a user studying auction behavior on a laptop or desktop in a quiet evening work setting, switching between code, API docs, and the dashboard. The interface should reduce glare and cognitive load while keeping the simulation results sharp.

The default color strategy is restrained: dark cool-tinted graphite neutrals, one orange accent reserved for primary actions only, blue for GSP series and heatmap intensity, teal for VCG series, cyan for benchmark/reference series, violet for learned/RL series, green for favorable states, and red for unfavorable states or errors. Color should annotate meaning, not decorate the page.

## Color

Use OKLCH values and keep neutrals lightly tinted toward blue.

```css
:root {
  --surface-base: oklch(16% 0.012 250);
  --surface-floor: oklch(12% 0.012 250);
  --surface-inset: oklch(15% 0.012 250);
  --surface-panel: oklch(20% 0.014 250);
  --surface-muted: oklch(25% 0.016 250);
  --surface-sidebar: oklch(18% 0.014 250);
  --surface-raised: oklch(23% 0.016 250);
  --border-subtle: oklch(32% 0.018 250);
  --border-muted: oklch(28% 0.016 250);
  --text-strong: oklch(93% 0.012 70);
  --text-base: oklch(84% 0.014 70);
  --text-muted: oklch(68% 0.018 70);
  --accent: oklch(72% 0.17 55);
  --accent-hover: oklch(78% 0.18 55);
  --accent-soft: oklch(27% 0.07 55);
  --accent-border: oklch(56% 0.13 55);
  --accent-contrast: oklch(16% 0.02 55);
  --accent-on: oklch(18% 0.02 55);
  --data-gsp: oklch(72% 0.12 220);
  --data-gsp-soft: oklch(26% 0.05 220);
  --data-gsp-start: oklch(46% 0.08 220);
  --data-vcg: oklch(73% 0.12 158);
  --data-vcg-soft: oklch(26% 0.05 158);
  --data-benchmark: oklch(74% 0.1 190);
  --data-benchmark-soft: oklch(26% 0.05 190);
  --data-benchmark-border: oklch(48% 0.07 190);
  --data-learning: oklch(73% 0.11 285);
  --data-learning-soft: oklch(25% 0.055 285);
  --data-learning-border: oklch(47% 0.08 285);
  --success: oklch(73% 0.13 150);
  --success-soft: oklch(26% 0.055 150);
  --success-border: oklch(50% 0.09 150);
  --danger: oklch(70% 0.14 25);
  --danger-soft: oklch(25% 0.06 25);
  --danger-border: oklch(50% 0.09 25);
}
```

## Typography

Auctioneer uses the IBM Plex family in three roles. Use `"IBM Plex Serif", ui-serif, Georgia, Cambria, "Times New Roman", Times, serif` for headings and large summary values so the product keeps an academic, research-workbench tone. Use `"IBM Plex Sans", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` for body copy, controls, labels, and dashboard chrome. Use `"IBM Plex Mono", "SFMono-Regular", Consolas, "Liberation Mono", monospace` for tabular values, bids, CTRs, payments, utilities, confidence intervals, Q-values, and heatmap cells.

Use tabular numerals for revenue, welfare, surplus, CTR, payment, utility, Q-values, bid gaps, confidence intervals, and convergence values. Prefer precise labels over explanatory paragraphs inside the interface. Dense numeric regions should prioritize scan speed over editorial personality.

Recommended hierarchy:

- Page title: 30 to 34px, 700 weight, tight line height.
- Section title: 18 to 20px, 700 weight.
- Table and control text: 13 to 15px.
- Eyebrow labels: 11 to 12px, uppercase, 700 weight, letter spacing only for metadata labels.

## Layout

Use a dashboard workbench structure:

- Top bar for product identity, docs link, and high-level status.
- Left or leading panel for experiment inputs and market configuration.
- Main panel for results, comparisons, tables, and charts.
- Tables and charts should have stable grid tracks so results do not shift when values change.

Avoid nested cards. Panels can be bordered sections, while repeated items such as bidders, slots, checkpoints, and rows may use compact cards or table rows. Keep spacing denser than a landing page, but leave enough rhythm for scanning.

## Components

Primary components:

- Experiment controls: buttons, numeric inputs, selects, and seed fields.
- Market summary: bidders, bids, values, quality scores, reserves, and CTRs.
- Mechanism comparison: GSP and VCG metrics shown side by side.
- Allocation tables: bidder, slot, CTR, payment, utility, and strategy.
- Strategy panels: truthful, shaded, Nash, and RL outcomes.
- Convergence views: checkpoints, learned bid, best-response bid, bid gap, utility gap, reward averages.
- Statistical summaries: mean, lower confidence bound, upper confidence bound, confidence level, resample count.

## Interaction

Primary actions should be explicit verbs such as "Run comparison", "Train agent", and "Check equilibrium". Loading states should preserve layout and describe the operation in plain language. Errors should be inline, specific, and recoverable.

Use 150ms to 200ms ease-out transitions for hover, focus, and status changes. Avoid ornamental motion. Any animation should make progression, convergence, or allocation changes easier to understand.

## Content

Use auction terms consistently: bidder, bid, private value, CTR, slot, allocation, payment, utility, revenue, welfare, surplus, best response, Nash check, Q-value, convergence.

Keep interface copy short. Do not claim a theoretical result unless the current screen shows the computed evidence or the assumptions behind it.
