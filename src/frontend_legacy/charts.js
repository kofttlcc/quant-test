
// charts.js - Wrapper for Lightweight Charts

let chart;
let candleSeries;
let equitySeries;

function initChart() {
    const chartElement = document.getElementById('tv-chart');
    if (!chartElement) return;

    chart = LightweightCharts.createChart(chartElement, {
        width: chartElement.clientWidth,
        height: chartElement.clientHeight,
        layout: {
            backgroundColor: '#181b21',
            textColor: '#d1d4dc',
        },
        grid: {
            vertLines: { color: '#2B2B43' },
            horzLines: { color: '#2B2B43' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: '#2B2B43',
        },
        timeScale: {
            borderColor: '#2B2B43',
        },
    });

    // Candlestick Series (Price)
    candleSeries = chart.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderDownColor: '#ef5350',
        borderUpColor: '#26a69a',
        wickDownColor: '#ef5350',
        wickUpColor: '#26a69a',
    });

    // Equity Series (Line) - On a separate scale? Or overlay?
    // Let's put equity on left scale or overlay. Actually separate pane is better but library is single pane by default.
    // For simplicity, we just plot Equity as a Line Series.
    // To visualize properly, we might need dual axis. 
    // Lightweight charts supports overlays.

    // NOTE: Price is 90000, Equity is 100000. Similar scale.
    equitySeries = chart.addLineSeries({
        color: '#00E5FF',
        lineWidth: 2,
        priceScaleId: 'left' // Use left axis for Equity
    });

    chart.applyOptions({
        leftPriceScale: {
            visible: true,
            borderColor: '#2B2B43',
        }
    });

    // Resize handler
    window.addEventListener('resize', () => {
        chart.resize(chartElement.clientWidth, chartElement.clientHeight);
    });
}

function updateChartData(priceData, equityData) {
    if (!chart) initChart();

    // Format Price Data: { time: '2019-04-11', open: 80.01, high: 96.63, low: 76.6, close: 88.65 }
    // Format Equity Data: { time: '...', value: ... }

    candleSeries.setData(priceData);
    equitySeries.setData(equityData);

    chart.timeScale().fitContent();
}
