import { useMemo, useState } from 'react'
import { compareAuctions } from './api'
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
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const rows = useMemo(() => {
    if (!result) {
      return []
    }

    return Object.entries(metricLabels).map(([metric, label]) => ({
      label,
      gsp: result.gsp[metric],
      vcg: result.vcg[metric],
      difference: result.difference[metric],
    }))
  }, [result])

  async function runComparison() {
    setIsLoading(true)
    setError('')

    try {
      const comparison = await compareAuctions(sampleMarket)
      setResult(comparison)
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
        <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">
          API docs
        </a>
      </section>

      <section className="workspace">
        <aside className="market-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Sample market</p>
              <h2>3 bidders, 2 slots</h2>
            </div>
            <button type="button" onClick={runComparison} disabled={isLoading}>
              {isLoading ? 'Running...' : 'Run comparison'}
            </button>
          </div>

          <div className="slot-strip">
            {sampleMarket.ctrs.map((ctr, index) => (
              <div className="slot" key={ctr}>
                <span>Slot {index + 1}</span>
                <strong>{formatNumber(ctr)}</strong>
                <small>CTR</small>
              </div>
            ))}
          </div>

          <div className="bidder-list">
            {sampleMarket.bidders.map((bidder) => (
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
              <p className="eyebrow">GSP vs VCG</p>
              <h2>Mechanism comparison</h2>
            </div>
            <span className={result ? 'status ready' : 'status'}>
              {result ? 'Result ready' : 'Waiting'}
            </span>
          </div>

          {result ? (
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
