"use client";

import { useState, useEffect } from 'react';
import styles from './Dashboard.module.css';
import { I18N } from '@/components/i18n';
import { ChartCard } from '@/components/ChartCard';
import { DataManager } from '@/components/DataManager';
import { SignalTable } from '@/components/SignalTable';
import { api, SentinelReport, ValuationDetail, MLSignalReport } from '@/services/api';
import { MacroSentinelCard } from '@/components/MacroSentinelCard';
import { ValuationAnalysis } from '@/components/ValuationAnalysis';
import { MLSignalBadge } from '@/components/MLSignalBadge';

interface Metric {
  name: string;
  value: number;
  format: string;
}

interface BacktestResult {
  ticker: string;
  metrics: Metric[];
  equity_curve: any[];
  drawdown_curve: any[];
  signals: any[];
}

export default function Dashboard() {
  const [ticker, setTicker] = useState('BTC-USD');
  const [strategy, setStrategy] = useState('MA Crossover');
  // Default to recent full year
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2023-12-31');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);

  // Phase 6 State
  const [macroData, setMacroData] = useState<SentinelReport | null>(null);
  const [valuationData, setValuationData] = useState<ValuationDetail | null>(null);
  const [mlData, setMlData] = useState<MLSignalReport | null>(null);

  // Load Macro Data on Mount
  useEffect(() => {
    api.getMacroReport().then(setMacroData).catch(e => console.error("Macro fetch failed", e));
  }, []);

  // Use Effect to load stock specific advanced data when ticker changes (debounced or on run?)
  // For now, let's load it when we run backtest or user clicks a button, 
  // but to make it "live", we can load it alongside.
  const loadAdvancedData = async () => {
    try {
      const [val, ml] = await Promise.all([
        api.getValuation(ticker),
        api.getMLSignal(ticker)
      ]);
      setValuationData(val);
      setMlData(ml);
    } catch (e) {
      console.error("Advanced data fetch failed", e);
    }
  };

  const runBacktest = async () => {
    setLoading(true);
    // Load advanced data in parallel
    loadAdvancedData();

    try {
      const res = await fetch('http://127.0.0.1:8000/api/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ticker: ticker,
          start_date: startDate,
          end_date: endDate,
          initial_capital: 10000,
          strategy: {
            strategy_name: strategy,
            params: {}
          }
        }),
      });

      if (!res.ok) throw new Error('API Error');

      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.error(e);
      alert('回測失敗 (Backtest Failed)');
    } finally {
      setLoading(false);
    }
  };

  const formatMetric = (m: Metric) => {
    if (m.format === 'percent') return `${(m.value * 100).toFixed(2)}%`;
    if (m.format === 'currency') return `$${m.value.toFixed(2)}`;
    return m.value.toFixed(4);
  };

  const translateMetricName = (name: string) => {
    return I18N.metrics[name as keyof typeof I18N.metrics] || name;
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>{I18N.header.title}</h1>
          <span className={styles.subtitle}>{I18N.header.subtitle}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {mlData && <MLSignalBadge data={mlData} />}
          <div style={{ color: '#00ff9d' }}>● {I18N.header.status}</div>
        </div>
      </header>

      <div className={styles.grid}>
        {/* Sidebar Controls */}
        <aside>
          {/* Phase 6: Macro Sentinel Widget */}
          {macroData && <MacroSentinelCard data={macroData} />}

          <div className={styles.card}>
            <h3 className={styles.cardTitle}>{I18N.controls.configTitle}</h3>

            <div className={styles.formGroup}>
              <label className={styles.label}>{I18N.controls.tickerLabel}</label>
              <input
                className={styles.input}
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>{I18N.controls.strategyLabel}</label>
              <select
                className={styles.select}
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
              >
                <option value="MA Crossover">{I18N.controls.strategies.ma}</option>
                <option value="RSI Reversion">{I18N.controls.strategies.rsi}</option>
                <option value="Momentum">{I18N.controls.strategies.mom}</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>{I18N.controls.startDateLabel}</label>
              <input
                type="date"
                className={styles.input}
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>{I18N.controls.endDateLabel}</label>
              <input
                type="date"
                className={styles.input}
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>

            <button
              className={styles.button}
              onClick={runBacktest}
              disabled={loading}
              style={{ opacity: loading ? 0.7 : 1 }}
            >
              {loading ? I18N.controls.btnCalculate : I18N.controls.btnInitiate}
            </button>
          </div>

          <DataManager />

          <div className={styles.card} style={{ marginTop: '1.5rem' }}>
            <h3 className={styles.cardTitle}>{I18N.logs.title}</h3>
            <div style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: '#666' }}>
              <div>{I18N.logs.init}</div>
              <div>{I18N.logs.waiting}</div>
              {loading && <div style={{ color: '#00ffff' }}>{I18N.logs.running}</div>}
              {result && <div style={{ color: '#00ff9d' }}>{I18N.logs.success}</div>}
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main>
          {/* Phase 6: Valuation Detail (Top) */}
          {valuationData && (
            <div style={{ marginBottom: '1.5rem' }}>
              <ValuationAnalysis data={valuationData} />
            </div>
          )}

          {result && (
            <>
              {/* Metrics Grid */}
              <div className={styles.metricGrid}>
                {result.metrics.map((m) => (
                  <div key={m.name} className={styles.metricCard}>
                    <div className={`${styles.metricValue} ${m.value > 0 ? styles.positive : styles.negative}`}>
                      {formatMetric(m)}
                    </div>
                    <div className={styles.metricLabel}>{translateMetricName(m.name)}</div>
                  </div>
                ))}
              </div>

              {/* Charts Grid */}
              <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
                <ChartCard
                  title={I18N.charts.equity}
                  data={result.equity_curve}
                  dataKey="equity"
                  color="#00d2ff"
                />
                <ChartCard
                  title={I18N.charts.drawdown}
                  data={result.drawdown_curve}
                  dataKey="drawdown"
                  color="#ff0055"
                />
              </div>

              {/* Transaction Table */}
              <SignalTable signals={result.signals} />
            </>
          )}

          {!result && !loading && !valuationData && (
            <div style={{
              display: 'flex',
              height: '400px',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#333',
              fontSize: '1.5rem',
              border: '2px dashed #333',
              borderRadius: '12px'
            }}>
              {I18N.charts.awaiting}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
