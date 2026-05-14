# Auctioneer

Auctioneer is an interactive simulation project for studying online ad auctions,
mechanism design, and bidder strategy.

The project models sponsored-search style ad markets where advertisers bid for a
limited number of ad slots with different click-through rates. The core goal is
to compare how auction mechanisms change platform revenue, market efficiency,
and bidder surplus.

## Current Scope

The backend currently implements:

- Generalized Second Price (GSP) auction pricing
- Vickrey-Clarke-Groves (VCG) auction pricing
- A comparison helper for running GSP and VCG on the same market
- Synthetic bidder generation with configurable bidding strategies
- Synthetic click-through rate (CTR) generation for ad slots
- Repeated auction simulations with averaged revenue, welfare, and surplus
- Deterministic tests for auction math, simulation helpers, and strategies

## Core Concepts

In GSP, bidders are ranked by bid and each winner pays based on the next-highest
bid scaled by the click-through rate of their slot. GSP is widely associated
with sponsored-search auctions, but it is not incentive compatible: bidders may
benefit from shading bids below their true values.

In VCG, each winner pays the externality they impose on other bidders. This
means the payment is based on how much worse off the rest of the market is
because that bidder won a slot. VCG is incentive compatible, so truthful bidding
is the dominant strategy under the standard assumptions.

Bidder strategies separate an advertiser's private value from the bid they
submit. Truthful bidders bid their value directly, while shaded bidders bid a
fraction of their value to preserve surplus. This distinction is central to
studying why GSP creates strategic incentives.

## Backend Setup

Create and activate a virtual environment from the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the backend package with development dependencies:

```bash
cd backend
python -m pip install -e ".[dev]"
```

Run tests:

```bash
python -m pytest
```

Run linting:

```bash
python -m ruff check .
```

Format code:

```bash
python -m ruff format .
```

## Project Direction

Planned next steps:

- Compare truthful and shaded strategy profiles across repeated simulations
- Support mixed bidder populations with different strategies in the same market
- Compute best-response bids under GSP
- Add reinforcement learning agents that learn bidding behavior over time
- Build a React and D3 frontend for auction visualization
