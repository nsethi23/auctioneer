import { Fragment, useEffect, useMemo, useState } from 'react'
import {
  checkHealth,
  checkNashEquilibrium,
  compareAuctions,
  computeBestResponse,
  computeBestResponseCurve,
  computePriceOfAnarchy,
  runGspAuction,
  runStatisticalSimulation,
  runVcgAuction,
  trackRlConvergence,
} from './api'
import './App.css'

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
}

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

function MetricRow({ label, gsp, vcg, difference }) {
  return (
    <div className="metric-row">
      <span>{label}</span>
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
          <span>{row.label}</span>
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
      <span>{label}</span>
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

function MarketInput({ label, value, step = '1', onChange }) {
  return (
    <label className="market-input">
      <span>{label}</span>
      <input
        type="number"
        min="0"
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  )
}

function MarketSelect({ label, value, options, onChange }) {
  return (
    <label className="market-input">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
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
        <span>CTR</span>
        <span>Payment</span>
        <span>Utility</span>
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

  return (
    <div className="rl-chart">
      <div className="chart-legend">
        <span className="legend-item learned">Learned Q-value</span>
        <span className="legend-item benchmark">Best-response utility</span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="RL convergence curve">
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} />
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
              const lightness = 96 - intensity * 42

              return (
                <div
                  className={entry.best_bid === bid ? 'heatmap-cell best-cell' : 'heatmap-cell'}
                  key={`${entry.value}-${bid}`}
                  style={{ background: `oklch(${lightness}% 0.12 245)` }}
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
        Darker cells have higher utility. Outlined cells are best-response bids for that value.
      </div>
    </div>
  )
}

function parseCandidateBids(candidateBidsText) {
  return candidateBidsText
    .split(',')
    .map((bid) => Number(bid.trim()))
    .filter((bid) => Number.isFinite(bid))
}

function parseNumberGrid(text) {
  return text
    .split(',')
    .map((value) => Number(value.trim()))
    .filter((value) => Number.isFinite(value))
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
  const [apiStatus, setApiStatus] = useState('checking')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

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
              <button type="button" className="secondary-button" onClick={resetMarket}>
                Reset
              </button>
              <button type="button" onClick={() => runExperiment('compare')} disabled={isLoading}>
                {isLoading ? 'Running...' : 'Run comparison'}
              </button>
            </div>
          </div>

          <div className="input-section">
            <div className="section-label">
              <span>Mechanism</span>
              <small>Choose what to run</small>
            </div>
            <div className="mechanism-controls">
              <button
                type="button"
                className={resultMode === 'compare' ? 'mode-button active' : 'mode-button'}
                onClick={() => runExperiment('compare')}
                disabled={isLoading}
              >
                GSP vs VCG
              </button>
              <button
                type="button"
                className={resultMode === 'gsp' ? 'mode-button active' : 'mode-button'}
                onClick={() => runExperiment('gsp')}
                disabled={isLoading}
              >
                GSP only
              </button>
              <button
                type="button"
                className={resultMode === 'vcg' ? 'mode-button active' : 'mode-button'}
                onClick={() => runExperiment('vcg')}
                disabled={isLoading}
              >
                VCG only
              </button>
              <button
                type="button"
                className={resultMode === 'poa' ? 'mode-button active' : 'mode-button'}
                onClick={() => runExperiment('poa')}
                disabled={isLoading}
              >
                Efficiency loss
              </button>
              <button
                type="button"
                className={resultMode === 'nash' ? 'mode-button active' : 'mode-button'}
                onClick={() => runExperiment('nash')}
                disabled={isLoading}
              >
                Nash check
              </button>
              <button
                type="button"
                className={resultMode === 'best-response' ? 'mode-button active' : 'mode-button'}
                onClick={() => runExperiment('best-response')}
                disabled={isLoading}
              >
                Best response
              </button>
              <button
                type="button"
                className={resultMode === 'rl' ? 'mode-button active' : 'mode-button'}
                onClick={() => runExperiment('rl')}
                disabled={isLoading}
              >
                RL convergence
              </button>
              <button
                type="button"
                className={resultMode === 'heatmap' ? 'mode-button active' : 'mode-button'}
                onClick={() => runExperiment('heatmap')}
                disabled={isLoading}
              >
                Heatmap
              </button>
              <button
                type="button"
                className={resultMode === 'stats' ? 'mode-button active' : 'mode-button'}
                onClick={() => runExperiment('stats')}
                disabled={isLoading}
              >
                Statistics
              </button>
            </div>
            <p className="mode-note">
              Statistics runs many synthetic auctions and reports bootstrap confidence intervals.
            </p>
          </div>

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
                  onChange={(event) => {
                    setCandidateBidsText(event.target.value)
                    setResult(null)
                  }}
                />
              </label>
              <MarketSelect
                label="Target bidder"
                value={selectedBidderId}
                options={market.bidders.map((bidder) => bidder.id)}
                onChange={(value) => {
                  setSelectedBidderId(value)
                  setResult(null)
                }}
              />
            </div>
          </div>

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
                onChange={(event) => {
                  setValueGridText(event.target.value)
                  setResult(null)
                }}
              />
            </label>
          </div>

          <div className="input-section">
            <div className="section-label">
              <span>RL training</span>
              <small>Episode count and learning parameters</small>
            </div>
            <div className="rl-settings">
              <MarketInput
                label="Episodes"
                value={rlSettings.num_episodes}
                onChange={(value) => updateRlSetting('num_episodes', value)}
              />
              <MarketInput
                label="Checkpoint"
                value={rlSettings.checkpoint_interval}
                onChange={(value) => updateRlSetting('checkpoint_interval', value)}
              />
              <MarketInput
                label="Learn rate"
                value={rlSettings.learning_rate}
                step="0.05"
                onChange={(value) => updateRlSetting('learning_rate', value)}
              />
              <MarketInput
                label="Epsilon"
                value={rlSettings.epsilon}
                step="0.05"
                onChange={(value) => updateRlSetting('epsilon', value)}
              />
              <MarketInput
                label="Discount"
                value={rlSettings.discount_factor}
                step="0.05"
                onChange={(value) => updateRlSetting('discount_factor', value)}
              />
            </div>
          </div>

          <div className="input-section">
            <div className="section-label">
              <span>Statistical simulation</span>
              <small>Repeated synthetic auction settings</small>
            </div>
            <div className="stat-settings">
              <MarketInput
                label="Auctions"
                value={statSettings.num_auctions}
                onChange={(value) => updateStatSetting('num_auctions', value)}
              />
              <MarketInput
                label="Bidders"
                value={statSettings.num_bidders}
                onChange={(value) => updateStatSetting('num_bidders', value)}
              />
              <MarketInput
                label="Min value"
                value={statSettings.min_value}
                onChange={(value) => updateStatSetting('min_value', value)}
              />
              <MarketInput
                label="Max value"
                value={statSettings.max_value}
                onChange={(value) => updateStatSetting('max_value', value)}
              />
              <MarketInput
                label="Resamples"
                value={statSettings.num_resamples}
                onChange={(value) => updateStatSetting('num_resamples', value)}
              />
              <MarketInput
                label="Confidence"
                value={statSettings.confidence}
                step="0.01"
                onChange={(value) => updateStatSetting('confidence', value)}
              />
            </div>
          </div>

          <div className="input-section">
            <div className="section-label">
              <span>Pricing constraint</span>
              <small>Minimum bid for allocation</small>
            </div>
            <MarketInput
              label="Reserve price"
              value={market.reserve_price}
              step="0.5"
              onChange={(value) => {
                setMarket((currentMarket) => ({
                  ...currentMarket,
                  reserve_price: value,
                }))
                setResult(null)
              }}
            />
          </div>

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
                    onChange={(value) => updateCtr(index, value)}
                  />
                  <button
                    type="button"
                    className="icon-button"
                    onClick={() => removeSlot(index)}
                    disabled={market.ctrs.length <= 1}
                    aria-label={`Remove slot ${index + 1}`}
                  >
                    −
                  </button>
                </div>
              ))}
            </div>
            <button type="button" className="secondary-button full-width-button" onClick={addSlot}>
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
                    onChange={(value) => updateBidder(index, 'value', value)}
                  />
                  <MarketInput
                    label="Bid"
                    value={bidder.bid}
                    onChange={(value) => updateBidder(index, 'bid', value)}
                  />
                  <MarketInput
                    label="Quality"
                    value={bidder.quality_score}
                    step="0.1"
                    onChange={(value) => updateBidder(index, 'quality_score', value)}
                  />
                  <button
                    type="button"
                    className="icon-button"
                    onClick={() => removeBidder(index)}
                    disabled={market.bidders.length <= 1}
                    aria-label={`Remove bidder ${bidder.id}`}
                  >
                    −
                  </button>
                </div>
              ))}
            </div>
            <button type="button" className="secondary-button full-width-button" onClick={addBidder}>
              Add bidder
            </button>
          </div>

          <div className="market-summary">
            {market.bidders.map((bidder) => (
              <div className="bidder" key={bidder.id}>
                <strong>{bidder.id}</strong>
                <span>value {formatNumber(bidder.value)}</span>
                <span>bid {formatNumber(bidder.bid)}</span>
                <span>quality {formatNumber(bidder.quality_score)}</span>
              </div>
            ))}
          </div>

          {error && <p className="error-message">{error}</p>}
        </aside>

        <section className="results-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">
                {resultMode === 'compare'
                  ? 'GSP vs VCG'
                  : resultMode === 'poa'
                    ? 'Efficiency'
                    : resultMode === 'nash'
                      ? 'Nash'
                      : resultMode === 'best-response'
                        ? 'Best response'
                        : resultMode === 'rl'
                          ? 'RL'
                          : resultMode === 'heatmap'
                            ? 'Heatmap'
                            : resultMode === 'stats'
                              ? 'Statistics'
                              : resultMode.toUpperCase()}
              </p>
              <h2>
                {resultMode === 'compare'
                  ? 'Mechanism comparison'
                  : resultMode === 'poa'
                    ? 'Price of anarchy'
                    : resultMode === 'nash'
                      ? 'Equilibrium check'
                      : resultMode === 'best-response'
                        ? 'Bid search'
                        : resultMode === 'rl'
                          ? 'Convergence'
                          : resultMode === 'heatmap'
                            ? 'Best-response heatmap'
                            : resultMode === 'stats'
                              ? 'Bootstrap intervals'
                              : 'Auction result'}
              </h2>
            </div>
            <span className={result ? 'status ready' : 'status'}>
              {result ? 'Result ready' : 'Waiting'}
            </span>
          </div>

          {result ? (
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
                      <span>Q-value</span>
                      <span>Bid gap</span>
                      <span>Utility gap</span>
                      <span>Recent reward</span>
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
              <strong>No comparison run yet</strong>
              <span>Start the backend, then run the sample market.</span>
            </div>
          )}
        </section>
      </section>
    </main>
  )
}

export default App
