# Design

## Visual Theme

Auctioneer uses a light, focused workbench theme. The physical scene is a user studying auction behavior on a laptop or desktop in a quiet work setting, switching between code, API docs, and the dashboard. The interface should reduce glare and cognitive load while keeping the simulation results sharp.

The default color strategy is restrained: cool-tinted neutrals, one blue accent for primary action and navigation, green for favorable deltas, and red for unfavorable deltas or errors. Color should annotate meaning, not decorate the page.

## Color

Use OKLCH values and keep neutrals lightly tinted toward blue.

```css
:root {
  --surface-base: oklch(98% 0.006 250);
  --surface-panel: oklch(99% 0.004 250);
  --surface-muted: oklch(96% 0.008 250);
  --surface-sidebar: oklch(97% 0.008 250);
  --border-subtle: oklch(86% 0.014 250);
  --border-muted: oklch(89% 0.012 250);
  --text-strong: oklch(18% 0.02 250);
  --text-base: oklch(21% 0.02 250);
  --text-muted: oklch(48% 0.035 250);
  --accent: oklch(42% 0.13 245);
  --accent-hover: oklch(36% 0.13 245);
  --accent-soft: oklch(92% 0.045 245);
  --success: oklch(35% 0.12 155);
  --success-soft: oklch(95% 0.035 160);
  --danger: oklch(42% 0.13 25);
  --danger-soft: oklch(96% 0.025 25);
}
```

## Typography

Use `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`. Keep display text compact because this is a tool, not a marketing page.

Use tabular numerals for revenue, welfare, surplus, CTR, payment, utility, Q-values, bid gaps, confidence intervals, and convergence values. Prefer precise labels over explanatory paragraphs inside the interface.

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
