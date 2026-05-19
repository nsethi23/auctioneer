import { useEffect, useMemo, useState } from 'react'
import { checkHealth, compareAuctions, runGspAuction, runVcgAuction } from './api'
import './App.css'

const sampleMarket = {
  bidders: [
    { id: 'A', value: 10, bid: 10 },
    { id: 'B', value: 8, bid: 8 },
    { id: 'C', value: 5, bid: 5 },
  ],
  ctrs: [0.6, 0.3],
}

const metricLabels = {
  revenue: 'Revenue',
  welfare: 'Welfare',
  bidder_surplus: 'Bidder surplus',
}

function formatNumber(value) {
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

function App() {
  const [market, setMarket] = useState(sampleMarket)
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
    if (!result || resultMode === 'compare') {
      return []
    }

    return Object.entries(metricLabels).map(([metric, label]) => ({
      label,
      value: result[metric],
    }))
  }, [result, resultMode])

  async function runExperiment(mode) {
    setIsLoading(true)
    setError('')
    setResultMode(mode)

    try {
      if (mode === 'gsp') {
        setResult(await runGspAuction(market))
      } else if (mode === 'vcg') {
        setResult(await runVcgAuction(market))
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
            </div>
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
              </div>
            ))}
          </div>

          {error && <p className="error-message">{error}</p>}
        </aside>

        <section className="results-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">
                {resultMode === 'compare' ? 'GSP vs VCG' : resultMode.toUpperCase()}
              </p>
              <h2>{resultMode === 'compare' ? 'Mechanism comparison' : 'Auction result'}</h2>
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
