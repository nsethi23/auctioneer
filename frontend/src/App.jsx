import { useEffect, useMemo, useState } from 'react'
import {
  checkHealth,
  checkNashEquilibrium,
  compareAuctions,
  computePriceOfAnarchy,
  runGspAuction,
  runVcgAuction,
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

function SingleMetricRow({ label, value }) {
  return (
    <div className="single-metric-row">
      <span>{label}</span>
      <strong>{formatNumber(value)}</strong>
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

function parseCandidateBids(candidateBidsText) {
  return candidateBidsText
    .split(',')
    .map((bid) => Number(bid.trim()))
    .filter((bid) => Number.isFinite(bid))
}

function App() {
  const [market, setMarket] = useState(sampleMarket)
  const [candidateBidsText, setCandidateBidsText] = useState(defaultCandidateBids)
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

  function resetMarket() {
    setMarket(sampleMarket)
    setCandidateBidsText(defaultCandidateBids)
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
    if (!result || resultMode === 'compare' || resultMode === 'poa') {
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
            </div>
            <p className="mode-note">
              GSP uses reserve and quality scores. VCG uses reserve. Nash checks whether bidders
              can improve by changing only their own bid.
            </p>
          </div>

          <div className="input-section">
            <div className="section-label">
              <span>Candidate bids</span>
              <small>Comma-separated grid for Nash and best response</small>
            </div>
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
                <MarketInput
                  key={`slot-${index}`}
                  label={`Slot ${index + 1}`}
                  value={ctr}
                  step="0.05"
                  onChange={(value) => updateCtr(index, value)}
                />
              ))}
            </div>
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
                </div>
              ))}
            </div>
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
                      : resultMode.toUpperCase()}
              </p>
              <h2>
                {resultMode === 'compare'
                  ? 'Mechanism comparison'
                  : resultMode === 'poa'
                    ? 'Price of anarchy'
                    : resultMode === 'nash'
                      ? 'Equilibrium check'
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
                    <h3>{resultMode.toUpperCase()} allocation</h3>
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
