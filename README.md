# Auctioneer

Auctioneer is an interactive simulation project for studying online ad auctions,
mechanism design, and bidder strategy.

The project models sponsored-search style ad markets where advertisers bid for a
limited number of ad slots with different click-through rates. The core goal is
to compare how auction mechanisms change platform revenue, market efficiency,
bidder surplus, and strategic bidding behavior.

## Current Scope

The backend currently implements:

- Generalized Second Price (GSP) auction pricing
- Vickrey-Clarke-Groves (VCG) auction pricing
- A comparison helper for running GSP and VCG on the same market
- Synthetic bidder generation with configurable bidding strategies
- Synthetic click-through rate (CTR) generation for ad slots
- Repeated auction simulations with averaged revenue, welfare, and surplus
- Truthful, shaded, and mixed bidder strategy profiles
- GSP best-response bid search and curve data for strategy visualization
- Q-learning bidder core, GSP training loop, best-response comparison, and
  convergence metrics
- Deterministic tests for auction math, simulation helpers, strategies, and
  learned bidding behavior

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

Best-response search makes that incentive visible by holding the rest of the
market fixed, trying candidate bids for one bidder, and selecting the bid that
maximizes utility under GSP. Running that search across private values produces
curve data for future equilibrium and heatmap visualizations.

The Q-learning bidder learns from repeated GSP auction rewards instead of being
given the auction math directly. Its learned policy can be compared against the
best-response benchmark using bid gap, utility gap, and reward averages.

## Target Demonstrations

The completed project is intended to demonstrate four layers of auction behavior:

- Economic mechanism design: GSP and VCG can allocate the same slots while
  creating different payment incentives. VCG is truthful under the standard
  assumptions; GSP generally is not.
- Strategic interaction: truthful and shaded bidder populations produce different
  revenue and surplus outcomes, especially under GSP.
- Best-response analysis: given competitors' bids, a bidder can compute the GSP
  bid that maximizes utility. Repeating this across values produces strategy
  curve and heatmap data.
- Learned behavior: a Q-learning bidder should learn high-utility shaded bids
  from repeated auction rewards and can be compared with the analytical
  best-response benchmark.

The simulation is not intended to reprove the theory in the papers. It turns the
theory into testable, visual, and interactive experiments.

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

Run the API server:

```bash
python -m uvicorn auctioneer.api.main:app --reload
```

Open the generated API docs:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

The backend exposes the simulation engine through FastAPI:

- `GET /health`: confirms the API is running.
- `POST /auction/gsp`: runs a GSP auction, including optional reserve prices
  and quality-score ranking.
- `POST /auction/vcg`: runs a VCG auction, including optional reserve prices.
- `POST /auction/compare`: runs GSP and VCG on the same bidder market and
  returns revenue, welfare, and surplus differences.
- `POST /metrics/price-of-anarchy`: compares optimal welfare against strategic
  GSP welfare.
- `POST /nash/check`: checks whether a bid profile has profitable unilateral
  deviations over a candidate bid grid.
- `POST /rl/convergence`: trains a Q-learning bidder and returns convergence
  checkpoints against the analytical best response.
- `POST /simulation/statistical`: runs repeated GSP/VCG simulations and returns
  bootstrap confidence intervals.

Example auction comparison request:

```json
{
  "bidders": [
    {"id": "A", "value": 10.0, "bid": 10.0},
    {"id": "B", "value": 8.0, "bid": 8.0},
    {"id": "C", "value": 5.0, "bid": 5.0}
  ],
  "ctrs": [0.6, 0.3]
}
```

## Project Direction

Planned next steps:

- Strengthen the RL convergence experiment so learned bids can be tracked against
  best-response bids over training.
- Add Nash-style population dynamics where bidders iteratively update toward
  best responses.
- Expose auction, simulation, strategy, and learning workflows through an API
- Build a React and D3 frontend for GSP/VCG comparison, strategy outcomes,
  best-response curves, and RL learning curves.

## References

- Benjamin Edelman, Michael Ostrovsky, and Michael Schwarz, "Internet
  Advertising and the Generalized Second-Price Auction"
- Hal R. Varian, "Position Auctions"
