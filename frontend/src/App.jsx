import { Fragment, useEffect, useMemo, useState } from 'react'
import {
  checkHealth,
  checkNashEquilibrium,
  compareAuctions,
  compareStrategies,
  computeBestResponse,
  computeBestResponseCurve,
  computePriceOfAnarchy,
  runGspAuction,
  runStatisticalSimulation,
  runVcgAuction,
  trackRlConvergence,
  trainMultiAgentRl,
} from './api'
import { modeCategories, modeConfig, modeToCategory } from './modeConfig'
import './App.css'


console.log('API base URL:', import.meta.env.VITE_API_BASE_URL);

const sampleMarket = {
  bidders: [
    { id: 'A', value: 10, bid: 10, quality_score: 1 },
    { id: 'B', value: 8, bid: 8, quality_score: 1 },
    { id: 'C', value: 5, bid: 5, quality_score: 1 },
  ],
  ctrs: [0.6, 0.3],
  reserve_price: 0,
}

const defaultCandidateBids = '0, 5, 6, 8, 10'
const defaultValueGrid = '4, 6, 8, 10, 12'

const defaultRlSettings = {
  num_episodes: 100,
  checkpoint_interval: 10,
  learning_rate: 0.1,
  discount_factor: 0,
  epsilon: 0.1,
}

const defaultStatSettings = {
  num_auctions: 100,
  num_bidders: 5,
  min_value: 1,
  max_value: 10,
  num_resamples: 100,
  confidence: 0.95,
  shade_factor: 0.7,
}

// Per-agent colors for multi-agent trajectory chart
const agentPalette = [
  'oklch(72% 0.12 220)',
  'oklch(73% 0.12 158)',
  'oklch(73% 0.11 285)',
  'oklch(74% 0.1 190)',
  'oklch(72% 0.14 50)',
  'oklch(70% 0.12 330)',
]

const metricLabels = {
  revenue: 'Revenue',
  welfare: 'Welfare',
  bidder_surplus: 'Bidder surplus',
}

const efficiencyLabels = {
  optimal_welfare: 'Optimal welfare',
  strategic_welfare: 'Strategic GSP welfare',
  price_of_anarchy: 'Price of anarchy',
  welfare_loss: 'Welfare loss',
}

function formatNumber(value) {
  if (value === Infinity) {
    return '∞'
  }

  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(value)
}

function getPercent(value, maxValue) {
  if (!Number.isFinite(value) || maxValue <= 0) {
    return 0
  }

  return Math.max(0, Math.min(100, (value / maxValue) * 100))
}

const glossary = {
  'Shade factor': 'Fraction of private value that shaded bidders submit as their bid (e.g. 0.7 means bid = 0.7 × value)',
  CTR: 'Click-through rate: probability a user clicks an ad in this slot position',
  Utility: "Bidder's value minus their payment for winning a slot (value − payment)",
  Welfare: "Sum of all winning bidders' private values, measuring allocative efficiency",
  'Bidder surplus': 'Total utility earned across all winning bidders',
  'Price of anarchy': 'Ratio of optimal welfare to strategic Nash equilibrium welfare. Closer to 1 means less efficiency loss from strategic bidding.',
  'Welfare loss': 'Optimal welfare minus strategic welfare: the cost of strategic bidding',
  'Optimal welfare': 'Welfare achieved by the socially optimal allocation, ignoring bids',
  'Strategic GSP welfare': 'Welfare achieved when all bidders play Nash equilibrium strategies in GSP',
  'Q-value': "Learned expected reward for the agent's current bid, stored in the Q-table",
  'Bid gap': 'Difference between the learned bid and the analytical best-response bid',
  'Utility gap': 'Difference between the learned Q-value and the best-response utility benchmark',
  'Recent reward': 'Average reward earned over the most recent training episodes',
  'Reserve price': 'Minimum bid required for a bidder to be allocated a slot',
}

function GlossaryTerm({ term }) {
  const definition = glossary[term]
  return definition ? <abbr title={definition}>{term}</abbr> : <>{term}</>
}

function AuctionAnimationPanel({ allocations, bidders, step, playing, onPlay, onPause, onStep, onBack }) {
  const maxSteps = allocations.length
  const ranked = [...bidders].sort(
    (a, b) => b.bid * (b.quality_score ?? 1) - a.bid * (a.quality_score ?? 1),
  )
  const revealedSlots = allocations.slice(0, step)
  const assignedIds = new Set(revealedSlots.map((a) => a.bidder_id))

  return (
    <div className="animation-panel">
      <div className="animation-columns">
        <div className="animation-section">
          <h3>Bid ranking</h3>
          <div className="anim-rank-list">
            {ranked.map((bidder, i) => {
              const slot = revealedSlots.find((a) => a.bidder_id === bidder.id)
              return (
                <div
                  key={bidder.id}
                  className={`anim-rank-row ${assignedIds.has(bidder.id) ? 'assigned' : ''}`}
                >
                  <span className="rank-badge">{i + 1}</span>
                  <div className="rank-info">
                    <strong>{bidder.id}</strong>
                    <span>Bid {formatNumber(bidder.bid)}</span>
                  </div>
                  {slot && <span className="rank-slot-tag">Slot {slot.slot + 1}</span>}
                </div>
              )
            })}
          </div>
        </div>

        <div className="animation-section">
          <h3>Slot assignment</h3>
          <div className="anim-slot-list">
            {allocations.map((allocation, i) => {
              const revealed = i < step
              return (
                <div key={i} className={`anim-slot-row ${revealed ? 'revealed' : 'pending'}`}>
                  <span className="anim-slot-label">Slot {i + 1}</span>
                  {revealed ? (
                    <div className="anim-slot-data">
                      <strong>{allocation.bidder_id}</strong>
                      <span><GlossaryTerm term="CTR" /> {formatNumber(allocation.ctr)}</span>
                      <span>Pay {formatNumber(allocation.payment)}</span>
                      <span className={allocation.utility > 0 ? 'positive' : ''}>
                        Util {formatNumber(allocation.utility)}
                      </span>
                    </div>
                  ) : (
                    <span className="anim-slot-pending">Waiting</span>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>

      <div className="animation-controls">
        <button type="button" className="icon-button" onClick={onBack} disabled={step === 0}>
          ←
        </button>
        <button
          type="button"
          className="secondary-button"
          onClick={playing ? onPause : onPlay}
          disabled={step >= maxSteps && !playing}
        >
          {playing ? 'Pause' : step >= maxSteps ? 'Done' : 'Play'}
        </button>
        <button type="button" className="icon-button" onClick={onStep} disabled={step >= maxSteps}>
          →
        </button>
        <span className="anim-counter">
          {step} / {maxSteps} slots
        </span>
      </div>
    </div>
  )
}

function MultiAgentChart({ history, bidderIds }) {
  if (!history.length) return null

  const width = 640
  const height = 220
  const padding = 36

  const allBids = history.flatMap((e) => Object.values(e.bids))
  const minBid = Math.min(...allBids, 0)
  const maxBid = Math.max(...allBids, 1)
  const bidRange = maxBid - minBid || 1
  const maxEpisode = Math.max(...history.map((e) => e.episode), 1)

  function ptX(episode) {
    return padding + (episode / maxEpisode) * (width - padding * 2)
  }

  function ptY(bid) {
    return height - padding - ((bid - minBid) / bidRange) * (height - padding * 2)
  }

  const yTicks = [0, 0.5, 1].map((t) => ({
    value: minBid + t * bidRange,
    y: height - padding - t * (height - padding * 2),
  }))

  return (
    <div className="rl-chart">
      <div className="chart-legend">
        {bidderIds.map((id, i) => (
          <span
            key={id}
            className="legend-item agent-legend"
            style={{ '--agent-color': agentPalette[i % agentPalette.length] }}
          >
            {id}
          </span>
        ))}
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Multi-agent bid trajectories">
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} />
        {yTicks.map((tick) => (
          <g key={tick.value}>
            <line x1={padding - 4} y1={tick.y} x2={padding} y2={tick.y} className="chart-tick" />
            <text
              x={padding - 6}
              y={tick.y}
              className="chart-axis-label"
              textAnchor="end"
              dominantBaseline="middle"
            >
              {formatNumber(tick.value)}
            </text>
          </g>
        ))}
        {bidderIds.map((id, i) => (
          <polyline
            key={id}
            points={history.map((e) => `${ptX(e.episode)},${ptY(e.bids[id] ?? 0)}`).join(' ')}
            fill="none"
            stroke={agentPalette[i % agentPalette.length]}
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            opacity={0.85}
          />
        ))}
      </svg>
    </div>
  )
}

function StrategyComparisonPanel({ result }) {
  const mechanisms = ['gsp', 'vcg']
  const metrics = [
    { key: 'revenue', label: 'Revenue' },
    { key: 'welfare', label: 'Welfare' },
    { key: 'bidder_surplus', label: 'Bidder surplus' },
  ]

  const allMeans = mechanisms.flatMap((m) =>
    metrics.flatMap(({ key }) => [result.truthful[m][key].mean, result.shaded[m][key].mean]),
  )
  const maxMean = Math.max(...allMeans, 1)

  return (
    <div className="strategy-comparison-panel">
      {mechanisms.map((mech) => (
        <div key={mech} className="strategy-mech-group">
          <h3>{mech.toUpperCase()}</h3>
          {metrics.map(({ key, label }) => {
            const t = result.truthful[mech][key]
            const s = result.shaded[mech][key]
            return (
              <div key={key} className="strategy-ci-row">
                <span className="strategy-ci-label">{label}</span>
                <div className="strategy-ci-bars">
                  <div className="strategy-ci-line">
                    <span className="strategy-ci-tag truthful-tag">Truthful</span>
                    <div className="bar-track">
                      <div
                        className="bar-fill gsp-fill"
                        style={{ width: `${getPercent(t.mean, maxMean)}%` }}
                      />
                    </div>
                    <span className="strategy-ci-value">
                      {formatNumber(t.mean)}
                      <small> [{formatNumber(t.lower)}–{formatNumber(t.upper)}]</small>
                    </span>
                  </div>
                  <div className="strategy-ci-line">
                    <span className="strategy-ci-tag shaded-tag">Shaded</span>
                    <div className="bar-track">
                      <div
                        className="bar-fill accent-fill"
                        style={{ width: `${getPercent(s.mean, maxMean)}%` }}
                      />
                    </div>
                    <span className="strategy-ci-value">
                      {formatNumber(s.mean)}
                      <small> [{formatNumber(s.lower)}–{formatNumber(s.upper)}]</small>
                    </span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      ))}
    </div>
  )
}

function MetricRow({ label, gsp, vcg, difference }) {
  return (
    <div className="metric-row">
      <span><GlossaryTerm term={label} /></span>
      <strong>{formatNumber(gsp)}</strong>
      <strong>{formatNumber(vcg)}</strong>
      <strong className={difference >= 0 ? 'positive' : 'negative'}>
        {difference >= 0 ? '+' : ''}
        {formatNumber(difference)}
      </strong>
    </div>
  )
}

function MetricBars({ rows }) {
  const maxValue = Math.max(...rows.flatMap((row) => [row.gsp, row.vcg]), 0)

  return (
    <div className="metric-bars">
      {rows.map((row) => (
        <div className="metric-bar-row" key={row.label}>
          <span><GlossaryTerm term={row.label} /></span>
          <div className="bar-pair">
            <div className="bar-line">
              <span>GSP</span>
              <div className="bar-track">
                <div
                  className="bar-fill gsp-fill"
                  style={{ width: `${getPercent(row.gsp, maxValue)}%` }}
                />
              </div>
              <strong>{formatNumber(row.gsp)}</strong>
            </div>
            <div className="bar-line">
              <span>VCG</span>
              <div className="bar-track">
                <div
                  className="bar-fill vcg-fill"
                  style={{ width: `${getPercent(row.vcg, maxValue)}%` }}
                />
              </div>
              <strong>{formatNumber(row.vcg)}</strong>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

function SingleMetricRow({ label, value }) {
  return (
    <div className="single-metric-row">
      <span><GlossaryTerm term={label} /></span>
      <strong>{formatNumber(value)}</strong>
    </div>
  )
}

function ConfidenceIntervalTable({ metrics }) {
  const rows = []

  for (const mechanism of ['gsp', 'vcg', 'difference']) {
    for (const [metric, label] of Object.entries(metricLabels)) {
      rows.push({
        mechanism,
        label,
        interval: metrics[mechanism][metric],
      })
    }
  }

  return (
    <div className="confidence-table">
      <div className="confidence-row table-head">
        <span>Group</span>
        <span>Metric</span>
        <span>Mean</span>
        <span>Lower</span>
        <span>Upper</span>
      </div>
      {rows.map((row) => (
        <div className="confidence-row" key={`${row.mechanism}-${row.label}`}>
          <span>{row.mechanism.toUpperCase()}</span>
          <span>{row.label}</span>
          <span>{formatNumber(row.interval.mean)}</span>
          <span>{formatNumber(row.interval.lower)}</span>
          <span>{formatNumber(row.interval.upper)}</span>
        </div>
      ))}
    </div>
  )
}

function MarketInput({ label, value, step = '1', onChange, disabled, hint }) {
  return (
    <label className="market-input">
      <span><GlossaryTerm term={label} /></span>
      <input
        type="number"
        min="0"
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        disabled={disabled}
        title={hint}
      />
    </label>
  )
}

function MarketSelect({ label, value, options, onChange, disabled }) {
  return (
    <label className="market-input">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)} disabled={disabled}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  )
}

function AllocationTable({ allocations }) {
  return (
    <div className="allocation-table">
      <div className="table-head">
        <span>Bidder</span>
        <span>Slot</span>
        <span><GlossaryTerm term="CTR" /></span>
        <span>Payment</span>
        <span><GlossaryTerm term="Utility" /></span>
      </div>
      {allocations.map((allocation) => (
        <div className="table-row" key={`${allocation.bidder_id}-${allocation.slot}`}>
          <span>{allocation.bidder_id}</span>
          <span>{allocation.slot + 1}</span>
          <span>{formatNumber(allocation.ctr)}</span>
          <span>{formatNumber(allocation.payment)}</span>
          <span>{formatNumber(allocation.utility)}</span>
        </div>
      ))}
    </div>
  )
}

function AllocationDiagram({ title, allocations }) {
  const maxCtr = Math.max(...allocations.map((allocation) => allocation.ctr), 0)

  return (
    <div className="allocation-diagram">
      <h3>{title}</h3>
      <div className="slot-map">
        {allocations.map((allocation) => (
          <div className="slot-map-row" key={`${title}-${allocation.bidder_id}-${allocation.slot}`}>
            <div className="slot-label">
              <span>Slot {allocation.slot + 1}</span>
              <strong>{allocation.bidder_id}</strong>
            </div>
            <div className="slot-visual">
              <div
                className="slot-visual-fill"
                style={{ width: `${getPercent(allocation.ctr, maxCtr)}%` }}
              />
            </div>
            <div className="slot-metrics">
              <span>CTR {formatNumber(allocation.ctr)}</span>
              <span>Pay {formatNumber(allocation.payment)}</span>
              <span>Util {formatNumber(allocation.utility)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function CandidateUtilityBars({ rows, bestBid }) {
  const maxUtility = Math.max(...rows.map((row) => row.utility), 0)

  return (
    <div className="utility-bars">
      {rows.map((candidate) => (
        <div
          className={candidate.bid === bestBid ? 'utility-bar-row best-candidate' : 'utility-bar-row'}
          key={candidate.bid}
        >
          <span>Bid {formatNumber(candidate.bid)}</span>
          <div className="bar-track">
            <div
              className="bar-fill utility-fill"
              style={{ width: `${getPercent(candidate.utility, maxUtility)}%` }}
            />
          </div>
          <strong>{formatNumber(candidate.utility)}</strong>
        </div>
      ))}
    </div>
  )
}

function RlConvergenceCurve({ checkpoints }) {
  if (checkpoints.length === 0) {
    return null
  }

  const width = 640
  const height = 220
  const padding = 28
  const values = checkpoints.flatMap((checkpoint) => [
    checkpoint.learned_q_value,
    checkpoint.best_response_utility,
  ])
  const maxValue = Math.max(...values, 1)
  const minValue = Math.min(...values, 0)
  const valueRange = maxValue - minValue || 1
  const maxEpisode = Math.max(...checkpoints.map((checkpoint) => checkpoint.episode), 1)

  function pointFor(checkpoint, value) {
    const x = padding + (checkpoint.episode / maxEpisode) * (width - padding * 2)
    const y = height - padding - ((value - minValue) / valueRange) * (height - padding * 2)
    return `${x},${y}`
  }

  const learnedPoints = checkpoints
    .map((checkpoint) => pointFor(checkpoint, checkpoint.learned_q_value))
    .join(' ')

  const benchmarkPoints = checkpoints
    .map((checkpoint) => pointFor(checkpoint, checkpoint.best_response_utility))
    .join(' ')

  const yTicks = [0, 0.5, 1].map((t) => ({
    value: minValue + t * valueRange,
    y: height - padding - t * (height - padding * 2),
  }))

  return (
    <div className="rl-chart">
      <div className="chart-legend">
        <span className="legend-item learned">Learned Q-value</span>
        <span className="legend-item benchmark">Best-response utility</span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="RL convergence curve">
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} />
        {yTicks.map((tick) => (
          <g key={tick.value}>
            <line
              x1={padding - 4}
              y1={tick.y}
              x2={padding}
              y2={tick.y}
              className="chart-tick"
            />
            <text
              x={padding - 6}
              y={tick.y}
              className="chart-axis-label"
              textAnchor="end"
              dominantBaseline="middle"
            >
              {formatNumber(tick.value)}
            </text>
          </g>
        ))}
        <polyline className="benchmark-line" points={benchmarkPoints} />
        <polyline className="learned-line" points={learnedPoints} />
        {checkpoints.map((checkpoint) => (
          <circle
            className="learned-point"
            key={checkpoint.episode}
            cx={pointFor(checkpoint, checkpoint.learned_q_value).split(',')[0]}
            cy={pointFor(checkpoint, checkpoint.learned_q_value).split(',')[1]}
            r="3"
          />
        ))}
      </svg>
    </div>
  )
}

function BestResponseHeatmap({ curve, candidateBids }) {
  const allUtilities = curve.flatMap((entry) => entry.results.map((result) => result.utility))
  const maxUtility = Math.max(...allUtilities, 0)
  const minUtility = Math.min(...allUtilities, 0)
  const utilityRange = maxUtility - minUtility || 1

  return (
    <div className="heatmap-panel">
      <div
        className="heatmap-grid"
        style={{ gridTemplateColumns: `96px repeat(${candidateBids.length}, minmax(64px, 1fr))` }}
      >
        <div className="heatmap-corner">Value / bid</div>
        {candidateBids.map((bid) => (
          <div className="heatmap-axis" key={`bid-${bid}`}>
            {formatNumber(bid)}
          </div>
        ))}
        {curve.map((entry) => (
          <Fragment key={entry.value}>
            <div className="heatmap-axis value-axis" key={`value-${entry.value}`}>
              {formatNumber(entry.value)}
            </div>
            {candidateBids.map((bid) => {
              const cell = entry.results.find((candidate) => candidate.bid === bid)
              const utility = cell?.utility ?? 0
              const intensity = (utility - minUtility) / utilityRange
              const lightness = 28 + intensity * 42

              return (
                <div
                  className={entry.best_bid === bid ? 'heatmap-cell best-cell' : 'heatmap-cell'}
                  key={`${entry.value}-${bid}`}
                  style={{
                    background: `oklch(${lightness}% 0.13 220)`,
                    color: lightness > 54 ? 'var(--surface-base)' : 'var(--text-strong)',
                  }}
                  title={`value ${formatNumber(entry.value)}, bid ${formatNumber(bid)}, utility ${formatNumber(utility)}`}
                >
                  {formatNumber(utility)}
                </div>
              )
            })}
          </Fragment>
        ))}
      </div>
      <div className="heatmap-note">
        Lighter cells have higher utility. Outlined cells are best-response bids for that value.
      </div>
    </div>
  )
}

function parseNumberList(text, label) {
  const tokens = text
    .split(',')
    .map((token) => token.trim())
    .filter(Boolean)

  const invalidToken = tokens.find((token) => !Number.isFinite(Number(token)))

  if (invalidToken) {
    throw new Error(`${label} contains an invalid number: ${invalidToken}`)
  }

  return tokens.map(Number)
}

function parseCandidateBids(candidateBidsText) {
  return parseNumberList(candidateBidsText, 'Bid grid')
}

function parseNumberGrid(text) {
  return parseNumberList(text, 'Value grid')
}

function App() {
  const [market, setMarket] = useState(sampleMarket)
  const [candidateBidsText, setCandidateBidsText] = useState(defaultCandidateBids)
  const [valueGridText, setValueGridText] = useState(defaultValueGrid)
  const [selectedBidderId, setSelectedBidderId] = useState(sampleMarket.bidders[0].id)
  const [rlSettings, setRlSettings] = useState(defaultRlSettings)
  const [statSettings, setStatSettings] = useState(defaultStatSettings)
  const [result, setResult] = useState(null)
  const [resultMode, setResultMode] = useState('compare')
  const [selectedCategory, setSelectedCategory] = useState('auction')
  const [apiStatus, setApiStatus] = useState('checking')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [animStep, setAnimStep] = useState(0)
  const [animPlaying, setAnimPlaying] = useState(false)

  const activeMode = modeConfig[resultMode]
  const activeCategory = modeCategories.find((category) => category.id === selectedCategory)
  const needsStrategyControls = ['nash', 'best-response', 'rl', 'heatmap', 'multi-agent'].includes(resultMode)
  const needsBidderSelector = ['nash', 'best-response', 'rl', 'heatmap'].includes(resultMode)
  const needsHeatmapControls = resultMode === 'heatmap'
  const needsRlControls = ['rl', 'multi-agent'].includes(resultMode)
  const needsStatControls = ['stats', 'strategy-compare'].includes(resultMode)
  const needsPricingControls = ['compare', 'gsp', 'vcg', 'animate'].includes(resultMode)

  useEffect(() => {
    let isMounted = true

    async function loadApiStatus() {
      try {
        await checkHealth()
        if (isMounted) {
          setApiStatus('online')
        }
      } catch {
        if (isMounted) {
          setApiStatus('offline')
        }
      }
    }

    loadApiStatus()

    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    if (!animPlaying || resultMode !== 'animate' || !result?.allocations) return
    const maxSteps = result.allocations.length
    if (animStep >= maxSteps) {
      setAnimPlaying(false)
      return
    }
    const timer = setTimeout(() => setAnimStep((s) => s + 1), 900)
    return () => clearTimeout(timer)
  }, [animPlaying, animStep, result, resultMode])

  function updateBidder(index, field, value) {
    setMarket((currentMarket) => ({
      ...currentMarket,
      bidders: currentMarket.bidders.map((bidder, bidderIndex) =>
        bidderIndex === index ? { ...bidder, [field]: value } : bidder,
      ),
    }))
    setResult(null)
  }

  function updateCtr(index, value) {
    setMarket((currentMarket) => ({
      ...currentMarket,
      ctrs: currentMarket.ctrs.map((ctr, ctrIndex) => (ctrIndex === index ? value : ctr)),
    }))
    setResult(null)
  }

  function addSlot() {
    setMarket((currentMarket) => ({
      ...currentMarket,
      ctrs: [...currentMarket.ctrs, 0.1],
    }))
    setResult(null)
  }

  function removeSlot(index) {
    setMarket((currentMarket) => ({
      ...currentMarket,
      ctrs: currentMarket.ctrs.filter((_, ctrIndex) => ctrIndex !== index),
    }))
    setResult(null)
  }

  function addBidder() {
    setMarket((currentMarket) => {
      const usedIds = new Set(currentMarket.bidders.map((bidder) => bidder.id))
      let nextIndex = 0

      while (usedIds.has(String.fromCharCode(65 + nextIndex))) {
        nextIndex += 1
      }

      const bidderId = String.fromCharCode(65 + nextIndex)
      const nextBidders = [
        ...currentMarket.bidders,
        {
          id: bidderId,
          value: 5,
          bid: 5,
          quality_score: 1,
        },
      ]

      return {
        ...currentMarket,
        bidders: nextBidders,
      }
    })
    setResult(null)
  }

  function removeBidder(index) {
    const nextBidders = market.bidders.filter((_, bidderIndex) => bidderIndex !== index)

    if (!nextBidders.some((bidder) => bidder.id === selectedBidderId) && nextBidders.length > 0) {
      setSelectedBidderId(nextBidders[0].id)
    }

    setMarket((currentMarket) => ({
      ...currentMarket,
      bidders: nextBidders,
    }))
    setResult(null)
  }

  function resetMarket() {
    setMarket(sampleMarket)
    setCandidateBidsText(defaultCandidateBids)
    setValueGridText(defaultValueGrid)
    setSelectedBidderId(sampleMarket.bidders[0].id)
    setRlSettings(defaultRlSettings)
    setStatSettings(defaultStatSettings)
    setSelectedCategory('auction')
    setResultMode('compare')
    setResult(null)
    setError('')
    setAnimStep(0)
    setAnimPlaying(false)
  }

  function selectCategory(category) {
    setSelectedCategory(category.id)
    setResultMode(category.modes[0])
    setResult(null)
    setError('')
  }

  function selectMode(mode) {
    setResultMode(mode)
    setSelectedCategory(modeToCategory[mode])
    setResult(null)
    setError('')
  }

  const rows = useMemo(() => {
    if (!result || resultMode !== 'compare') {
      return []
    }

    return Object.entries(metricLabels).map(([metric, label]) => ({
      label,
      gsp: result.gsp[metric],
      vcg: result.vcg[metric],
      difference: result.difference[metric],
    }))
  }, [result, resultMode])

  const singleRows = useMemo(() => {
    if (!result || (resultMode !== 'gsp' && resultMode !== 'vcg')) {
      return []
    }

    return Object.entries(metricLabels).map(([metric, label]) => ({
      label,
      value: result[metric],
    }))
  }, [result, resultMode])

  const efficiencyRows = useMemo(() => {
    if (!result || resultMode !== 'poa') {
      return []
    }

    return Object.entries(efficiencyLabels).map(([metric, label]) => ({
      label,
      value: result[metric],
    }))
  }, [result, resultMode])

  const bestResponseRows = useMemo(() => {
    if (!result || resultMode !== 'best-response') {
      return []
    }

    return result.results
  }, [result, resultMode])

  const checkpointRows = useMemo(() => {
    if (!result || resultMode !== 'rl') {
      return []
    }

    return result.checkpoints
  }, [result, resultMode])

  const heatmapCurve = useMemo(() => {
    if (!result || resultMode !== 'heatmap') {
      return []
    }

    return result.curve
  }, [result, resultMode])

  function updateRlSetting(field, value) {
    setRlSettings((currentSettings) => ({
      ...currentSettings,
      [field]: value,
    }))
    setResult(null)
  }

  function updateStatSetting(field, value) {
    setStatSettings((currentSettings) => ({
      ...currentSettings,
      [field]: value,
    }))
    setResult(null)
  }

  async function runExperiment(mode) {
    setIsLoading(true)
    setError('')
    setResultMode(mode)

    try {
      if (mode === 'nash') {
        const candidateBids = parseCandidateBids(candidateBidsText)

        if (candidateBids.length === 0) {
          throw new Error('Enter at least one candidate bid')
        }

        setResult(
          await checkNashEquilibrium({
            bidders: market.bidders,
            ctrs: market.ctrs,
            candidate_bids: candidateBids,
          }),
        )
        return
      }

      if (mode === 'best-response') {
        const candidateBids = parseCandidateBids(candidateBidsText)

        if (candidateBids.length === 0) {
          throw new Error('Enter at least one candidate bid')
        }

        setResult(
          await computeBestResponse({
            bidder_id: selectedBidderId,
            bidders: market.bidders,
            ctrs: market.ctrs,
            candidate_bids: candidateBids,
          }),
        )
        return
      }

      if (mode === 'rl') {
        const candidateBids = parseCandidateBids(candidateBidsText)
        const targetBidder = market.bidders.find((bidder) => bidder.id === selectedBidderId)

        if (candidateBids.length === 0) {
          throw new Error('Enter at least one candidate bid')
        }

        if (!targetBidder) {
          throw new Error('Select a bidder in the current market')
        }

        setResult(
          await trackRlConvergence({
            bidder_id: targetBidder.id,
            value: targetBidder.value,
            other_bidders: market.bidders.filter((bidder) => bidder.id !== targetBidder.id),
            ctrs: market.ctrs,
            candidate_bids: candidateBids,
            ...rlSettings,
          }),
        )
        return
      }

      if (mode === 'heatmap') {
        const candidateBids = parseCandidateBids(candidateBidsText)
        const values = parseNumberGrid(valueGridText)

        if (candidateBids.length === 0) {
          throw new Error('Enter at least one candidate bid')
        }

        if (values.length === 0) {
          throw new Error('Enter at least one private value')
        }

        setResult(
          await computeBestResponseCurve({
            bidder_id: selectedBidderId,
            bidders: market.bidders,
            ctrs: market.ctrs,
            values,
            candidate_bids: candidateBids,
          }),
        )
        return
      }

      if (mode === 'stats') {
        if (market.ctrs.length === 0) {
          throw new Error('Add at least one slot CTR before running statistical simulation')
        }

        setResult(
          await runStatisticalSimulation({
            ...statSettings,
            ctrs: market.ctrs,
          }),
        )
        return
      }

      if (mode === 'animate') {
        const gspResult = await runGspAuction({ ...market, use_quality_scores: true })
        setResult(gspResult)
        setAnimStep(0)
        setAnimPlaying(false)
        return
      }

      if (mode === 'multi-agent') {
        const candidateBids = parseCandidateBids(candidateBidsText)

        if (candidateBids.length === 0) {
          throw new Error('Enter at least one candidate bid')
        }

        setResult(
          await trainMultiAgentRl({
            bidder_specs: market.bidders,
            ctrs: market.ctrs,
            candidate_bids: candidateBids,
            num_episodes: rlSettings.num_episodes,
            learning_rate: rlSettings.learning_rate,
            discount_factor: rlSettings.discount_factor,
            epsilon: rlSettings.epsilon,
          }),
        )
        return
      }

      if (mode === 'strategy-compare') {
        if (market.ctrs.length === 0) {
          throw new Error('Add at least one slot CTR before running strategy comparison')
        }

        setResult(
          await compareStrategies({
            ...statSettings,
            ctrs: market.ctrs,
          }),
        )
        return
      }

      if (mode === 'gsp') {
        setResult(
          await runGspAuction({
            ...market,
            use_quality_scores: true,
          }),
        )
      } else if (mode === 'vcg') {
        setResult(await runVcgAuction(market))
      } else if (mode === 'poa') {
        setResult(
          await computePriceOfAnarchy({
            bidders: market.bidders,
            ctrs: market.ctrs,
          }),
        )
      } else {
        setResult(await compareAuctions(market))
      }
    } catch (caughtError) {
      setError(caughtError.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="topbar">
        <div>
          <p className="eyebrow">Auctioneer</p>
          <h1>Ad auction simulation lab</h1>
        </div>
        <div className="topbar-actions">
          <span className={`api-status ${apiStatus}`}>API {apiStatus}</span>
          <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">
            API docs
          </a>
        </div>
      </section>

      <section className="workspace">
        <aside className="market-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Market inputs</p>
              <h2>{market.bidders.length} bidders, {market.ctrs.length} slots</h2>
            </div>
            <div className="button-group">
              <button type="button" className="secondary-button" onClick={resetMarket} disabled={isLoading}>
                Reset
              </button>
              <button type="button" onClick={() => runExperiment(resultMode)} disabled={isLoading}>
                {isLoading ? 'Running...' : activeMode.action}
              </button>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          <div className="input-section">
            <div className="section-label">
              <span>Experiment type</span>
              <small>Choose a workflow</small>
            </div>
            <div className="mode-selector">
              <div className="category-controls" aria-label="Experiment categories">
                {modeCategories.map((category) => (
                  <button
                    type="button"
                    className={
                      selectedCategory === category.id ? 'category-button active' : 'category-button'
                    }
                    key={category.id}
                    onClick={() => selectCategory(category)}
                    disabled={isLoading}
                    aria-pressed={selectedCategory === category.id}
                  >
                    {category.label}
                  </button>
                ))}
              </div>
              <div className="mechanism-controls" aria-label="Experiment modes">
                {activeCategory.modes.map((mode) => (
                  <button
                    type="button"
                    className={resultMode === mode ? 'mode-button active' : 'mode-button'}
                    key={mode}
                    onClick={() => selectMode(mode)}
                    disabled={isLoading}
                    aria-pressed={resultMode === mode}
                  >
                    {modeConfig[mode].label}
                  </button>
                ))}
              </div>
              <p className="mode-note">{activeMode.note}</p>
            </div>
          </div>

          {needsStrategyControls && (
            <div className="input-section">
              <div className="section-label">
                <span>Strategy search</span>
                <small>Candidate bid grid and target bidder</small>
              </div>
              <div className="strategy-search">
                <label className="market-input">
                  <span>Bid grid</span>
                  <input
                    type="text"
                    value={candidateBidsText}
                    disabled={isLoading}
                    onChange={(event) => {
                      setCandidateBidsText(event.target.value)
                      setResult(null)
                    }}
                  />
                </label>
                {needsBidderSelector && (
                <MarketSelect
                  label="Target bidder"
                  value={selectedBidderId}
                  options={market.bidders.map((bidder) => bidder.id)}
                  disabled={isLoading}
                  onChange={(value) => {
                    setSelectedBidderId(value)
                    setResult(null)
                  }}
                />
              )}
              </div>
            </div>
          )}

          {needsHeatmapControls && (
            <div className="input-section">
              <div className="section-label">
                <span>Heatmap values</span>
                <small>Private value grid for the selected bidder</small>
              </div>
              <label className="market-input">
                <span>Value grid</span>
                <input
                  type="text"
                  value={valueGridText}
                  disabled={isLoading}
                  onChange={(event) => {
                    setValueGridText(event.target.value)
                    setResult(null)
                  }}
                />
              </label>
            </div>
          )}

          {needsRlControls && (
            <div className="input-section">
              <div className="section-label">
                <span>RL training</span>
                <small>Episode count and learning parameters</small>
              </div>
              <div className="rl-settings">
                <MarketInput
                  label="Episodes"
                  value={rlSettings.num_episodes}
                  disabled={isLoading}
                  hint="Typical range: 50–500"
                  onChange={(value) => updateRlSetting('num_episodes', value)}
                />
                <MarketInput
                  label="Checkpoint interval"
                  value={rlSettings.checkpoint_interval}
                  disabled={isLoading}
                  hint="Must be less than episode count"
                  onChange={(value) => updateRlSetting('checkpoint_interval', value)}
                />
                <MarketInput
                  label="Learning rate"
                  value={rlSettings.learning_rate}
                  step="0.05"
                  disabled={isLoading}
                  hint="Typical range: 0.01–0.5"
                  onChange={(value) => updateRlSetting('learning_rate', value)}
                />
                <MarketInput
                  label="Epsilon"
                  value={rlSettings.epsilon}
                  step="0.05"
                  disabled={isLoading}
                  hint="Exploration rate: 0.01–0.5"
                  onChange={(value) => updateRlSetting('epsilon', value)}
                />
                <MarketInput
                  label="Discount"
                  value={rlSettings.discount_factor}
                  step="0.05"
                  disabled={isLoading}
                  hint="Future reward weight: 0–1"
                  onChange={(value) => updateRlSetting('discount_factor', value)}
                />
              </div>
            </div>
          )}

          {needsStatControls && (
            <div className="input-section">
              <div className="section-label">
                <span>Statistical simulation</span>
                <small>Repeated synthetic auction settings</small>
              </div>
              <div className="stat-settings">
                <MarketInput
                  label="Auctions"
                  value={statSettings.num_auctions}
                  disabled={isLoading}
                  onChange={(value) => updateStatSetting('num_auctions', value)}
                />
                <MarketInput
                  label="Bidders"
                  value={statSettings.num_bidders}
                  disabled={isLoading}
                  onChange={(value) => updateStatSetting('num_bidders', value)}
                />
                <MarketInput
                  label="Min value"
                  value={statSettings.min_value}
                  disabled={isLoading}
                  onChange={(value) => updateStatSetting('min_value', value)}
                />
                <MarketInput
                  label="Max value"
                  value={statSettings.max_value}
                  disabled={isLoading}
                  onChange={(value) => updateStatSetting('max_value', value)}
                />
                <MarketInput
                  label="Resamples"
                  value={statSettings.num_resamples}
                  disabled={isLoading}
                  onChange={(value) => updateStatSetting('num_resamples', value)}
                />
                <MarketInput
                  label="Confidence"
                  value={statSettings.confidence}
                  step="0.01"
                  disabled={isLoading}
                  onChange={(value) => updateStatSetting('confidence', value)}
                />
                {resultMode === 'strategy-compare' && (
                  <MarketInput
                    label="Shade factor"
                    value={statSettings.shade_factor}
                    step="0.05"
                    disabled={isLoading}
                    hint="Fraction of value that shaded bidders submit as bid"
                    onChange={(value) => updateStatSetting('shade_factor', value)}
                  />
                )}
              </div>
            </div>
          )}

          {needsPricingControls && (
            <div className="input-section">
              <div className="section-label">
                <span>Pricing constraint</span>
                <small>Minimum bid for allocation</small>
              </div>
              <MarketInput
                label="Reserve price"
                value={market.reserve_price}
                step="0.5"
                disabled={isLoading}
                onChange={(value) => {
                  setMarket((currentMarket) => ({
                    ...currentMarket,
                    reserve_price: value,
                  }))
                  setResult(null)
                }}
              />
            </div>
          )}

          <div className="input-section">
            <div className="section-label">
              <span>Slots</span>
              <small>Click-through rates</small>
            </div>
            <div className="slot-strip">
              {market.ctrs.map((ctr, index) => (
                <div className="field-with-action" key={`slot-${index}`}>
                  <MarketInput
                    label={`Slot ${index + 1}`}
                    value={ctr}
                    step="0.05"
                    disabled={isLoading}
                    onChange={(value) => updateCtr(index, value)}
                  />
                  <button
                    type="button"
                    className="icon-button"
                    onClick={() => removeSlot(index)}
                    disabled={isLoading || market.ctrs.length <= 1}
                    aria-label={`Remove slot ${index + 1}`}
                  >
                    −
                  </button>
                </div>
              ))}
            </div>
            <button type="button" className="secondary-button full-width-button" onClick={addSlot} disabled={isLoading}>
              Add slot
            </button>
          </div>

          <div className="input-section">
            <div className="section-label">
              <span>Bidders</span>
              <small>Private value and submitted bid</small>
            </div>
            <div className="bidder-list">
              {market.bidders.map((bidder, index) => (
                <div className="bidder-editor" key={bidder.id}>
                  <strong>{bidder.id}</strong>
                  <MarketInput
                    label="Value"
                    value={bidder.value}
                    disabled={isLoading}
                    onChange={(value) => updateBidder(index, 'value', value)}
                  />
                  <MarketInput
                    label="Bid"
                    value={bidder.bid}
                    disabled={isLoading}
                    onChange={(value) => updateBidder(index, 'bid', value)}
                  />
                  <MarketInput
                    label="Quality"
                    value={bidder.quality_score}
                    step="0.1"
                    disabled={isLoading}
                    onChange={(value) => updateBidder(index, 'quality_score', value)}
                  />
                  <button
                    type="button"
                    className="icon-button"
                    onClick={() => removeBidder(index)}
                    disabled={isLoading || market.bidders.length <= 1}
                    aria-label={`Remove bidder ${bidder.id}`}
                  >
                    −
                  </button>
                </div>
              ))}
            </div>
            <button type="button" className="secondary-button full-width-button" onClick={addBidder} disabled={isLoading}>
              Add bidder
            </button>
          </div>

        </aside>

        <section className="results-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">{activeMode.eyebrow}</p>
              <h2>{activeMode.title}</h2>
            </div>
            <span className={isLoading ? 'status' : result ? 'status ready' : 'status'}>
              {isLoading ? 'Running' : result ? 'Result ready' : 'Waiting'}
            </span>
          </div>

          {isLoading ? (
            <div className="loading-state">
              <strong>Computing</strong>
              <span>{activeMode.action}</span>
            </div>
          ) : result ? (
            <>
              {resultMode === 'compare' ? (
                <>
                  <div className="metric-table">
                    <div className="metric-row table-head">
                      <span>Metric</span>
                      <span>GSP</span>
                      <span>VCG</span>
                      <span>Diff</span>
                    </div>
                    {rows.map((row) => (
                      <MetricRow
                        key={row.label}
                        label={row.label}
                        gsp={row.gsp}
                        vcg={row.vcg}
                        difference={row.difference}
                      />
                    ))}
                  </div>

                  <MetricBars rows={rows} />

                  <div className="allocation-visuals">
                    <AllocationDiagram title="GSP slot map" allocations={result.gsp.allocations} />
                    <AllocationDiagram title="VCG slot map" allocations={result.vcg.allocations} />
                  </div>

                  <div className="allocations">
                    <div>
                      <h3>GSP allocation</h3>
                      <AllocationTable allocations={result.gsp.allocations} />
                    </div>
                    <div>
                      <h3>VCG allocation</h3>
                      <AllocationTable allocations={result.vcg.allocations} />
                    </div>
                  </div>
                </>
              ) : resultMode === 'poa' ? (
                <div className="efficiency-result">
                  <div className="efficiency-summary">
                    <span>Welfare loss</span>
                    <strong>{formatNumber(result.welfare_loss)}</strong>
                    <small>
                      Optimal welfare is {formatNumber(result.optimal_welfare)} versus strategic
                      GSP welfare of {formatNumber(result.strategic_welfare)}.
                    </small>
                  </div>

                  <div className="single-metric-table">
                    <div className="single-metric-row table-head">
                      <span>Metric</span>
                      <span>Value</span>
                    </div>
                    {efficiencyRows.map((row) => (
                      <SingleMetricRow key={row.label} label={row.label} value={row.value} />
                    ))}
                  </div>
                </div>
              ) : resultMode === 'nash' ? (
                <div className="nash-result">
                  <div
                    className={
                      result.is_equilibrium ? 'nash-summary equilibrium' : 'nash-summary deviation'
                    }
                  >
                    <span>{result.is_equilibrium ? 'Equilibrium' : 'Profitable deviation'}</span>
                    <strong>
                      {result.is_equilibrium ? 'No bidder can improve' : 'Deviation found'}
                    </strong>
                    <small>
                      Maximum utility gain: {formatNumber(result.max_utility_gain)} over the
                      candidate bid grid.
                    </small>
                  </div>

                  {result.deviations.length > 0 ? (
                    <div className="deviation-table">
                      <div className="deviation-row table-head">
                        <span>Bidder</span>
                        <span>Current bid</span>
                        <span>Best bid</span>
                        <span>Gain</span>
                      </div>
                      {result.deviations.map((deviation) => (
                        <div className="deviation-row" key={deviation.bidder_id}>
                          <span>{deviation.bidder_id}</span>
                          <span>{formatNumber(deviation.current_bid)}</span>
                          <span>{formatNumber(deviation.best_bid)}</span>
                          <span className="positive">{formatNumber(deviation.utility_gain)}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state compact">
                      <strong>No profitable deviations</strong>
                      <span>The current bids pass this candidate-grid Nash check.</span>
                    </div>
                  )}
                </div>
              ) : resultMode === 'best-response' ? (
                <div className="best-response-result">
                  <div className="best-response-summary">
                    <span>Selected bidder {selectedBidderId}</span>
                    <strong>Bid {formatNumber(result.bid)}</strong>
                    <small>
                      Best utility is {formatNumber(result.utility)} over the candidate bid grid.
                    </small>
                  </div>

                  <div className="candidate-table">
                    <div className="candidate-row table-head">
                      <span>Candidate bid</span>
                      <span>Utility</span>
                    </div>
                    {bestResponseRows.map((candidate) => (
                      <div
                        className={
                          candidate.bid === result.bid
                            ? 'candidate-row best-candidate'
                            : 'candidate-row'
                        }
                        key={candidate.bid}
                      >
                        <span>{formatNumber(candidate.bid)}</span>
                        <span>{formatNumber(candidate.utility)}</span>
                      </div>
                    ))}
                  </div>

                  <CandidateUtilityBars rows={bestResponseRows} bestBid={result.bid} />
                </div>
              ) : resultMode === 'rl' ? (
                <div className="rl-result">
                  <div className="rl-summary">
                    <span>Best response benchmark</span>
                    <strong>Bid {formatNumber(result.best_response.bid)}</strong>
                    <small>
                      Best-response utility is {formatNumber(result.best_response.utility)} for
                      selected bidder {selectedBidderId}.
                    </small>
                  </div>

                  <RlConvergenceCurve checkpoints={checkpointRows} />

                  <div className="checkpoint-table">
                    <div className="checkpoint-row table-head">
                      <span>Episode</span>
                      <span>Learned bid</span>
                      <span><GlossaryTerm term="Q-value" /></span>
                      <span><GlossaryTerm term="Bid gap" /></span>
                      <span><GlossaryTerm term="Utility gap" /></span>
                      <span><GlossaryTerm term="Recent reward" /></span>
                    </div>
                    {checkpointRows.map((checkpoint) => (
                      <div className="checkpoint-row" key={checkpoint.episode}>
                        <span>{checkpoint.episode}</span>
                        <span>{formatNumber(checkpoint.learned_bid)}</span>
                        <span>{formatNumber(checkpoint.learned_q_value)}</span>
                        <span>{formatNumber(checkpoint.bid_gap)}</span>
                        <span>{formatNumber(checkpoint.utility_gap)}</span>
                        <span>{formatNumber(checkpoint.average_recent_reward)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : resultMode === 'heatmap' ? (
                <div className="heatmap-result">
                  <div className="best-response-summary">
                    <span>Selected bidder {selectedBidderId}</span>
                    <strong>{heatmapCurve.length} values</strong>
                    <small>
                      Each row holds competitors fixed and searches the selected bidder's utility
                      over the candidate bid grid.
                    </small>
                  </div>

                  <BestResponseHeatmap
                    curve={heatmapCurve}
                    candidateBids={result.candidate_bids}
                  />
                </div>
              ) : resultMode === 'stats' ? (
                <div className="stats-result">
                  <div className="stats-summary">
                    <span>Repeated auctions</span>
                    <strong>{formatNumber(result.num_auctions)}</strong>
                    <small>
                      {formatNumber(result.confidence * 100)}% bootstrap confidence intervals from{' '}
                      {formatNumber(result.num_resamples)} resamples.
                    </small>
                  </div>

                  <ConfidenceIntervalTable metrics={result.metrics} />
                </div>
              ) : resultMode === 'animate' ? (
                <AuctionAnimationPanel
                  allocations={result.allocations}
                  bidders={market.bidders}
                  step={animStep}
                  playing={animPlaying}
                  onPlay={() => setAnimPlaying(true)}
                  onPause={() => setAnimPlaying(false)}
                  onStep={() => setAnimStep((s) => Math.min(result.allocations.length, s + 1))}
                  onBack={() => { setAnimPlaying(false); setAnimStep((s) => Math.max(0, s - 1)) }}
                />
              ) : resultMode === 'multi-agent' ? (
                <div className="rl-result">
                  <div className="rl-summary">
                    <span>Multi-agent training</span>
                    <strong>{result.history.length} episodes</strong>
                    <small>
                      {market.bidders.length} agents trained simultaneously on the same auction.
                    </small>
                  </div>
                  <MultiAgentChart
                    history={result.history}
                    bidderIds={market.bidders.map((b) => b.id)}
                  />
                </div>
              ) : resultMode === 'strategy-compare' ? (
                <div className="stats-result">
                  <div className="stats-summary">
                    <span>Strategy comparison</span>
                    <strong>Shade {formatNumber(result.shade_factor)}</strong>
                    <small>
                      {formatNumber(result.num_auctions)} auctions,{' '}
                      {formatNumber(result.confidence * 100)}% CI. Shaded bidders bid{' '}
                      {formatNumber(result.shade_factor * 100)}% of their value.
                    </small>
                  </div>
                  <StrategyComparisonPanel result={result} />
                </div>
              ) : (
                <div className="single-result">
                  <div className="single-metric-table">
                    <div className="single-metric-row table-head">
                      <span>Metric</span>
                      <span>Value</span>
                    </div>
                    {singleRows.map((row) => (
                      <SingleMetricRow key={row.label} label={row.label} value={row.value} />
                    ))}
                  </div>

                  <div>
                    <AllocationDiagram
                      title={`${resultMode.toUpperCase()} slot map`}
                      allocations={result.allocations}
                    />
                    <AllocationTable allocations={result.allocations} />
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <strong>{activeMode.emptyTitle}</strong>
              <span>
                {apiStatus === 'offline' ? 'Start the backend, then try again.' : activeMode.emptyText}
              </span>
            </div>
          )}
        </section>
      </section>
    </main>
  )
}

export default App
