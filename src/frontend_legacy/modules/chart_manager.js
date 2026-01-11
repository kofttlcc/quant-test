
// Chart Manager - Wraps Lightweight Charts logic

let chart;
let candlestickSeries;
let lineSeries;

export const ChartManager = {
    init() {
        if (chart) return; // Prevent double init

        const container = document.getElementById('tv-chart');
        if (!container) return;

        // Create Chart
        chart = LightweightCharts.createChart(container, {
            width: container.offsetWidth,
            height: container.offsetHeight,
            layout: {
                backgroundColor: '#1E1E1E',
                textColor: '#DDD',
            },
            grid: {
                vertLines: { color: '#333' },
                horzLines: { color: '#333' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: '#444',
            },
            timeScale: {
                borderColor: '#444',
            },
        });

        // Add Series
        candlestickSeries = chart.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderVisible: false,
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350',
        });

        lineSeries = chart.addLineSeries({
            color: '#2962FF',
            lineWidth: 2,
        });

        // Resize Observer
        new ResizeObserver(entries => {
            if (entries.length === 0 || entries[0].target !== container) { return; }
            const newRect = entries[0].contentRect;
            chart.applyOptions({ height: newRect.height, width: newRect.width });
        }).observe(container);
    },

    /**
     * Update Chart Data
     * @param {Array} candles - [{time, open, high, low, close}, ...]
     * @param {Array} lineData - [{time, value}, ...]
     */
    update(candles = [], lineData = []) {
        if (!chart) this.init();

        if (candles.length > 0) candlestickSeries.setData(candles);
        if (lineData.length > 0) lineSeries.setData(lineData);

        chart.timeScale().fitContent();
    },

    /**
     * Clear chart container (used when switching to Arena Table view)
     */
    clear() {
        // We don't destroy the chart instance usually, but for Arena table replacement
        // we might just hide it or we rely on InnerHTML overwrite in the main logic.
        // For now, let's keep it simple. If we overwrite innerHTML, chart is gone.
    },

    /**
     * Get container element
     */
    getContainer() {
        return document.getElementById('tv-chart');
    }
};
