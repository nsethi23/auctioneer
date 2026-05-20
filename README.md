# Auctioneer

Auctioneer is an interactive simulation platform for studying online ad auctions,
mechanism design, and bidder strategy. It models sponsored-search markets where
advertisers bid for slots with different click-through rates, and makes the theory
observable through a React dashboard backed by a FastAPI simulation engine.

## Architecture

```
backend/                          frontend/
  auctioneer/
    api/main.py        ←→  src/App.jsx        Dashboard with 13 experiment panels
    auctions/
      gsp.py                src/api.js         Typed fetch wrappers
      vcg.py
    agents/
      best_response.py      src/modeConfig.js  Panel routing and metadata
      nash.py
      q_learning*.py
      exp3*.py
    simulation/
      generation.py         Vite + Recharts
      runner.py
      statistical_runner.py
    metrics/efficiency.py
```

The backend is a pure Python library (`auctioneer` package) served over FastAPI.
The frontend calls it directly from the browser — no intermediary server.

## Setup

### Backend

```bash
python3 -m venv .venv && source .venv/bin/activate
cd backend
python -m pip install -e ".[dev]"
```

Run tests:

```bash
python -m pytest
```

Run linting and formatting:

```bash
python -m ruff check . && python -m ruff format .
```

Start the API:

```bash
python -m uvicorn auctioneer.api.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: `http://127.0.0.1:5173`

The dashboard shows API status in the header. All experiment panels are disabled
if the backend is offline.

## API Endpoints

- `GET /health` — liveness check.
- `POST /auction/gsp` — GSP auction with optional reserve price and quality-score ranking.
- `POST /auction/vcg` — VCG auction with optional reserve price.
- `POST /auction/compare` — GSP and VCG on the same market; returns revenue, welfare, and surplus differences.
- `POST /metrics/price-of-anarchy` — optimal welfare against strategic GSP welfare.
- `POST /nash/check` — checks whether a bid profile has profitable unilateral deviations over a candidate grid.
- `POST /best-response` — utility-maximizing GSP bid for one bidder with competitors fixed.
- `POST /best-response/curve` — sweeps private values and candidate bids for heatmap data.
- `POST /rl/convergence` — trains a Q-learning bidder and returns convergence checkpoints against best response.
- `POST /rl/exp3` — trains an EXP3 bandit bidder and returns weight and bid history.
- `POST /rl/multi-agent` — trains all market bidders as Q-learning agents simultaneously and returns bid trajectories.
- `POST /simulation/statistical` — repeated GSP/VCG auctions with bootstrap confidence intervals; supports uniform and log-normal value distributions.
- `POST /simulation/strategy-comparison` — runs truthful and shaded bidding populations on matched markets and compares revenue, welfare, and surplus CIs.

Example `/auction/compare` request:

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

## Results

The following numbers were produced by the `/simulation/strategy-comparison` and
`/rl/convergence` endpoints. Market: 5 bidders, 3 slots (CTRs 0.6/0.3/0.15),
values uniform on [1, 10], 1000 auctions, 1000 bootstrap resamples, 95% CI.

### Mechanism comparison — truthful bidding

| Metric | GSP | VCG |
|--------|-----|-----|
| Revenue | 6.482 [6.395, 6.577] | 5.563 [5.480, 5.648] |
| Welfare | 8.023 [7.944, 8.105] | 8.023 [7.943, 8.102] |
| Surplus | 1.541 [1.500, 1.583] | 2.460 [2.403, 2.518] |

GSP extracts more revenue than VCG (~17%) because its per-click payment rule
does not fully rebate the externality. Welfare is identical: both mechanisms
assign slots optimally when bids equal values.

### Strategy effect under GSP — shaded bidding (shade factor 0.7)

| Metric | Truthful | Shaded |
|--------|----------|--------|
| GSP revenue | 6.482 | 4.537 [4.476, 4.604] |
| GSP welfare | 8.023 | 8.023 |
| GSP surplus | 1.541 | 3.486 [3.448, 3.524] |
| VCG revenue | 5.563 | 5.563 (unchanged) |

Bid shading shifts ~2 units of per-auction value from revenue to bidder surplus
under GSP. VCG revenue is unaffected — incentive compatibility holds: shading
cannot improve utility, so the equilibrium bid remains truthful.

### Q-learning convergence

Setup: single Q-learning bidder (value 10), three competitors (bids 8/6/4),
3 slots (CTRs 0.6/0.3/0.15), candidate bids [1..10], 500 episodes.

- Analytical best response: bid 6, utility 1.20
- Learned policy after training: bid ~5, reward stabilizes near 0.9
- Bid gap: ~1 (one candidate bid below best response)

The agent learns to shade below its value without seeing the auction math,
approaching but not exactly matching the analytical optimum within 500 episodes.

## Limitations

**No multi-bidder equilibrium solver.** The Nash check endpoint tests a single
bid profile for stability. It does not iterate toward equilibrium or guarantee
finding one. Multi-agent training tracks bid trajectories but convergence is not
guaranteed; cycling is common.

**Discrete candidate bid grid.** Best-response, Nash check, and RL all operate
over an explicit list of candidate bids supplied by the caller. Optimal bids
between grid points cannot be found.

**Single-shot GSP pricing.** The GSP model is the standard second-price-per-click
rule from Edelman et al. It does not model squashing, quality-adjusted reserve
prices, or the variants deployed in production systems.

**No bandit regret guarantees under non-stationarity.** EXP3 minimizes regret
against the best fixed action in hindsight. When competitors also learn (as in
multi-agent mode), the environment is non-stationary and regret bounds do not
apply.

**Bootstrap CIs assume i.i.d. auctions.** Each simulated auction draws fresh
random values. The CI calculation treats auctions as independent samples, which
holds by construction but would not hold for a panel dataset with the same
bidders.

## Mathematical Appendix

### GSP pricing

Bidders are ranked by effective bid (bid × quality score if enabled). Bidder
ranked $i$ wins slot $i$ and pays:

$$p_i = \frac{\alpha_{i+1}}{\alpha_i} \cdot b_{i+1}$$

where $\alpha_i$ is the CTR of slot $i$ and $b_{i+1}$ is the next-highest bid.
The lowest winner pays the reserve price if no bidder falls below them.

### VCG externality payment

$$p_i^{\text{VCG}} = \sum_{j > i} (\alpha_j - \alpha_{j-1}) \cdot b_{j+1}$$

Each winner pays the welfare loss imposed on bidders displaced below them. This
is the externality definition: what would the other bidders have earned if
bidder $i$ were absent.

### Price of anarchy

$$\text{PoA} = \frac{W^*}{W^{\text{GSP}}}$$

where $W^*$ is the maximum achievable welfare (optimal slot assignment) and
$W^{\text{GSP}}$ is the welfare under the GSP Nash equilibrium. PoA $\geq 1$;
values near 1 indicate low efficiency loss.

### Q-learning update

$$Q(s, a) \leftarrow Q(s, a) + \alpha \bigl[ r + \gamma \max_{a'} Q(s, a') - Q(s, a) \bigr]$$

In a single-shot auction ($\gamma = 0$) this simplifies to a running average of
observed rewards for each candidate bid.

### EXP3 update

Let $k$ be the number of candidate bids and $p_a$ the probability assigned to
the selected bid $a$. After observing reward $r$:

$$w_a \leftarrow w_a \cdot \exp\!\left(\frac{\gamma \cdot \hat{r}}{k}\right), \quad \hat{r} = \frac{r}{p_a}$$

The importance-weighted estimator $\hat{r}$ corrects for the fact that $a$ was
not always selected. Probabilities are the mixture:

$$p_a = (1-\gamma) \frac{w_a}{\sum_j w_j} + \frac{\gamma}{k}$$

This ensures every action has probability $\geq \gamma/k$, bounding regret
against the best fixed action in hindsight (Auer et al. 2002).

## References

- Benjamin Edelman, Michael Ostrovsky, and Michael Schwarz, "Internet Advertising
  and the Generalized Second-Price Auction," *American Economic Review* 97(1), 2007.
- Hal R. Varian, "Position Auctions," *International Journal of Industrial
  Organization* 25(6), 2007.
- Peter Auer, Nicolò Cesa-Bianchi, Yoav Freund, and Robert E. Schapire,
  "The Nonstochastic Multiarmed Bandit Problem," *SIAM Journal on Computing*
  32(1), 2002.
- Jacob Abernethy and Satyen Kale, "Adaptive Market Making via Online Learning,"
  *NeurIPS* 2013.
