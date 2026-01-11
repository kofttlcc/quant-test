
export const I18N = {
    header: {
        title: "ALPHA-1 // 量化交易系統",
        subtitle: "高頻交易儀表盤",
        status: "系統在線"
    },
    controls: {
        configTitle: "策略配置",
        tickerLabel: "資產代碼",
        strategyLabel: "策略模型",
        startDateLabel: "開始日期",
        endDateLabel: "結束日期",
        btnCalculate: "計算中...",
        btnInitiate: "開始回測",
        strategies: {
            ma: "雙均線交叉 (MA Crossover)",
            rsi: "RSI均值回歸 (RSI Reversion)",
            mom: "動量策略 (Momentum)"
        }
    },
    logs: {
        title: "系統日誌",
        init: "[系統] 核心模組初始化...",
        waiting: "[系統] 等待指令...",
        running: "[任務] 正在執行模擬...",
        success: "[成功] 回測完成。"
    },
    metrics: {
        "Total Return": "總回報率",
        "CAGR": "年化複合增長率",
        "Volatility": "波動率 (年化)",
        "Sharpe Ratio": "夏普比率",
        "Max Drawdown": "最大回撤",
        "Calmar Ratio": "卡爾瑪比率",
        "Win Rate": "勝率",
        "Sortino Ratio": "索提諾比率",
        "VaR (95%)": "風險價值 (VaR 95%)"
    },
    charts: {
        equity: "權益曲線 (Equity Curve)",
        drawdown: "回撤分析 (Drawdown Analysis)",
        awaiting: "等待輸入數據"
    },
    dataManager: {
        title: "數據管理 (Data Manager)",
        btnUpdatePrice: "更新 S&P 500",
        btnUpdateBTC: "更新 BTC 價格",
        btnUpdateFinancial: "更新 S&P 500 財報",
        sourceLabel: "數據源 (Source)",
        apiKeyPlaceholder: "Finnhub API Key"
    },
    signals: {
        title: "交易明細 (Transaction Details)",
        noSignals: "暫無交易信號 (No Signals)",
        colDate: "日期 (Date)",
        colAction: "動作 (Action)",
        colPrice: "價格 (Price)",
        colSize: "數量 (Size)"
    }
};
