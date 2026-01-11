
import React, { useEffect, useRef } from 'react';
import { createChart, CrosshairMode, LineSeries, AreaSeries } from 'lightweight-charts';

export const TradingChart = ({ data, lineData, markers = [], rsiData = [] }) => {
    const chartContainerRef = useRef();
    const rsiContainerRef = useRef();
    const chartRef = useRef();
    const rsiChartRef = useRef();
    const candleSeriesRef = useRef();
    const lineSeriesRef = useRef();
    const rsiSeriesRef = useRef();

    useEffect(() => {
        if (!chartContainerRef.current) return;

        try {
            // 主圖表 - 價格走勢 (優化：使用線型圖適應長週期回測)
            const chart = createChart(chartContainerRef.current, {
                layout: {
                    backgroundColor: '#1E1E1E',
                    textColor: '#DDD',
                },
                grid: {
                    vertLines: { color: '#333' },
                    horzLines: { color: '#333' },
                },
                crosshair: {
                    mode: CrosshairMode.Normal,
                    vertLine: {
                        width: 1,
                        color: '#555',
                        style: 0, // 實線
                        labelVisible: false,
                    },
                    horzLine: {
                        width: 1,
                        color: '#555',
                        style: 0,
                    },
                },
                rightPriceScale: {
                    borderColor: '#444',
                },
                timeScale: {
                    borderColor: '#444',
                    visible: false, // Hide on main chart, show on RSI
                },
                width: chartContainerRef.current.clientWidth,
                height: 300,
            });

            // RSI Sub-Chart
            const rsiChart = createChart(rsiContainerRef.current, {
                layout: {
                    backgroundColor: '#1A1A1A',
                    textColor: '#DDD',
                },
                grid: {
                    vertLines: { color: '#333' },
                    horzLines: { color: '#333' },
                },
                crosshair: {
                    mode: CrosshairMode.Normal,
                    vertLine: {
                        width: 1,
                        color: '#555',
                        style: 0,
                        labelVisible: true,
                    },
                    horzLine: {
                        width: 1,
                        color: '#555',
                        style: 0,
                    },
                },
                rightPriceScale: {
                    borderColor: '#444',
                    scaleMargins: { top: 0.1, bottom: 0.1 },
                },
                timeScale: {
                    borderColor: '#444',
                },
                width: rsiContainerRef.current.clientWidth,
                height: 100,
            });

            // 同步 timeScale (關鍵：確保十字星垂直對齊)
            const syncTimeScales = () => {
                const mainTimeScale = chart.timeScale();
                const rsiTimeScale = rsiChart.timeScale();

                mainTimeScale.subscribeVisibleLogicalRangeChange((range) => {
                    if (range) {
                        rsiTimeScale.setVisibleLogicalRange(range);
                    }
                });

                rsiTimeScale.subscribeVisibleLogicalRangeChange((range) => {
                    if (range) {
                        mainTimeScale.setVisibleLogicalRange(range);
                    }
                });
            };

            // 同步十字星位置
            chart.subscribeCrosshairMove((param) => {
                if (param.time && rsiSeriesRef.current) {
                    rsiChart.setCrosshairPosition(NaN, param.time, rsiSeriesRef.current);
                }
                if (!param.time) {
                    rsiChart.clearCrosshairPosition();
                }
            });

            rsiChart.subscribeCrosshairMove((param) => {
                if (param.time && candleSeriesRef.current) {
                    chart.setCrosshairPosition(NaN, param.time, candleSeriesRef.current);
                }
                if (!param.time) {
                    chart.clearCrosshairPosition();
                }
            });

            // 價格線型圖 (替代 K 線圖以適應長週期回測)
            const candleSeries = chart.addSeries(AreaSeries, {
                topColor: 'rgba(38, 166, 154, 0.56)',
                bottomColor: 'rgba(38, 166, 154, 0.04)',
                lineColor: '#26a69a',
                lineWidth: 2,
            });

            // 權益曲線
            const lineSeries = chart.addSeries(LineSeries, {
                color: '#2962FF',
                lineWidth: 2,
                priceScaleId: 'left',
            });

            // RSI Series
            const rsiSeries = rsiChart.addSeries(LineSeries, {
                color: '#FF9800',
                lineWidth: 2,
            });

            // 添加 RSI 參考線 (30/70)
            rsiSeries.createPriceLine({ price: 70, color: '#ef5350', lineWidth: 1, lineStyle: 2, axisLabelVisible: true, title: '超買' });
            rsiSeries.createPriceLine({ price: 30, color: '#26a69a', lineWidth: 1, lineStyle: 2, axisLabelVisible: true, title: '超賣' });

            chartRef.current = chart;
            rsiChartRef.current = rsiChart;
            candleSeriesRef.current = candleSeries;
            lineSeriesRef.current = lineSeries;
            rsiSeriesRef.current = rsiSeries;

            // 啟用 timeScale 同步
            syncTimeScales();

            // Resize Handler
            const handleResize = () => {
                if (chartContainerRef.current && chart) {
                    chart.applyOptions({ width: chartContainerRef.current.clientWidth });
                }
                if (rsiContainerRef.current && rsiChart) {
                    rsiChart.applyOptions({ width: rsiContainerRef.current.clientWidth });
                }
            };
            window.addEventListener('resize', handleResize);

            return () => {
                window.removeEventListener('resize', handleResize);
                chart.remove();
                rsiChart.remove();
            };
        } catch (e) {
            console.error("Chart Init Error:", e);
        }
    }, []);

    useEffect(() => {
        try {
            if (!chartRef.current) return;

            // 更新價格線型圖數據 (將 K 線格式轉換為線型圖格式)
            if (candleSeriesRef.current && Array.isArray(data)) {
                // 轉換數據格式: { time, open, high, low, close } -> { time, value }
                const lineChartData = data.map(d => ({
                    time: d.time,
                    value: d.close  // 使用收盤價
                }));
                candleSeriesRef.current.setData(lineChartData);

                // 買賣標記仍然可以用於 AreaSeries
                if (Array.isArray(markers) && markers.length > 0) {
                    try {
                        if (typeof candleSeriesRef.current.setMarkers === 'function') {
                            candleSeriesRef.current.setMarkers(markers);
                        } else {
                            console.warn('setMarkers not available in this version');
                        }
                    } catch (markerErr) {
                        console.warn('Markers error:', markerErr.message);
                    }
                }
            }

            // Update Equity Line
            if (lineSeriesRef.current && Array.isArray(lineData)) {
                lineSeriesRef.current.setData(lineData);
            }

            // Update RSI Data - Enhanced logging
            if (rsiSeriesRef.current && Array.isArray(rsiData) && rsiData.length > 0) {
                console.log('Setting RSI data:', rsiData.length, 'points');
                console.log('RSI first point:', rsiData[0]);
                console.log('RSI last point:', rsiData[rsiData.length - 1]);
                try {
                    rsiSeriesRef.current.setData(rsiData);
                    console.log('RSI data set successfully');
                } catch (rsiErr) {
                    console.error('RSI setData error:', rsiErr);
                }
            } else {
                console.log('RSI skipped: ref=', !!rsiSeriesRef.current, 'data=', rsiData?.length || 0);
            }

            // Fit Content
            if (data?.length > 0 || lineData?.length > 0) {
                chartRef.current.timeScale().fitContent();
                rsiChartRef.current?.timeScale().fitContent();
            }
        } catch (e) {
            console.warn("Chart Update Error:", e);
        }
    }, [data, lineData, markers, rsiData]);

    return (
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
            <div
                ref={chartContainerRef}
                style={{ width: '100%', height: '300px', position: 'relative' }}
            />
            <div style={{
                height: '20px',
                background: '#1A1A1A',
                borderTop: '1px solid #333',
                display: 'flex',
                alignItems: 'center',
                paddingLeft: '10px',
                fontSize: '0.8em',
                color: '#FF9800'
            }}>
                RSI (14)
            </div>
            <div
                ref={rsiContainerRef}
                style={{ width: '100%', height: '100px', position: 'relative' }}
            />
        </div>
    );
};
