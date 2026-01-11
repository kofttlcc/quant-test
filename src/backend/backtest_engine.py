
import pandas as pd
import numpy as np
import logging
import sys
import os

# Ensure project root is in path for local execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from src.models.strategy_logic import MomentumStrategy
    from src.data_loader.downloader import fetch_data
except ImportError:
    # Fallback
    pass

from src.core.analyzers import SharpeAnalyzer, DrawdownAnalyzer, TradeAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Backtester:
    """
    Simple Vectorized Backtester.
    """
    def __init__(self, initial_capital=100000.0, commission_bps=10.0):
        self.initial_capital = initial_capital
        self.commission_rate = commission_bps / 10000.0
    
    def _format_date(self, index, strat_df):
        """格式化日期索引為 YYYY-MM-DD 字符串"""
        try:
            if hasattr(index, 'strftime'):
                return index.strftime("%Y-%m-%d")
            elif isinstance(index, (pd.Timestamp, np.datetime64)):
                return pd.Timestamp(index).strftime("%Y-%m-%d")
            elif isinstance(index, str):
                return index.split(' ')[0].split('T')[0]
            else:
                if 'Date' in strat_df.columns:
                    return str(strat_df.loc[index, 'Date'])[:10]
                return str(index)
        except Exception as e:
            logger.warning(f"Date format error: {e}")
            return str(index)
        
    def run_backtest(self, df: pd.DataFrame, strategy) -> dict:
        """
        Run backtest.
        Args:
            df: OHLCV DataFrame
            strategy: Strategy object with generate_signals method
        Returns:
            dict: Metrics and Equity Curve
        """
        if df.empty:
            return {"error": "Empty DataFrame"}
        
        # FIX: 確保使用 DatetimeIndex
        # 如果 Date 列存在且索引不是 DatetimeIndex，則設置 Date 為索引
        if 'Date' in df.columns and not isinstance(df.index, pd.DatetimeIndex):
            df = df.copy()
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        elif not isinstance(df.index, pd.DatetimeIndex):
            # 嘗試將現有索引轉為 DatetimeIndex
            try:
                df.index = pd.to_datetime(df.index)
            except Exception:
                pass  # 保留原索引
        
        # 1. Generate Signals
        strat_df = strategy.generate_signals(df)
        
        # 2. Calculate Returns
        # CRITICAL FIX: 移除 Look-ahead Bias
        # 原代碼使用 shift(-1) 偷看未來收益，現改為正確的時間對齊：
        # - Asset_Ret[T] = 當日收益率
        # - Position 需要 shift(1)：T日的持倉決策影響 T+1 日的收益
        strat_df['Asset_Ret'] = strat_df['Close'].pct_change()
        
        # Calculate Turnover for costs
        strat_df['Turnover'] = strat_df['Position'].diff().abs().fillna(0)
        strat_df['Cost'] = strat_df['Turnover'] * self.commission_rate
        
        # Position lagged by 1: T日持倉在 T+1 日生效
        strat_df['Strat_Ret'] = (strat_df['Position'].shift(1) * strat_df['Asset_Ret']) - strat_df['Cost']
        strat_df['Strat_Ret'] = strat_df['Strat_Ret'].fillna(0)
        
        # 3. Equity Curve
        strat_df['Equity'] = self.initial_capital * (1 + strat_df['Strat_Ret']).cumprod()
        
        # 5. Extract Trades (Phase 12) - (Re-ordered for Analyzer access)
        # 只記錄「開倉」和「平倉」交易，忽略持倉調整
        # 交易價格使用次日開盤價（T+1 Open），更接近實際執行價格
        trades = []
        trade_returns = []
        cumulative_pnl = 0.0  # 累計盈虧追蹤
        
        # 計算次日開盤價（用於交易執行價格）
        if 'Open' in strat_df.columns:
            strat_df['Exec_Price'] = strat_df['Open'].shift(-1)  # T+1 開盤價
            strat_df['Exec_Price'] = strat_df['Exec_Price'].fillna(strat_df['Close'])  # 最後一日用收盤價
        else:
            strat_df['Exec_Price'] = strat_df['Close']  # 無 Open 列時退回使用 Close
        
        # 記錄持倉狀態變化：0 → 非0 = 開倉(BUY)，非0 → 0 = 平倉(SELL)
        strat_df['Was_In_Position'] = (strat_df['Position'].shift(1).fillna(0) > 0)
        strat_df['Is_In_Position'] = (strat_df['Position'] > 0)
        
        # 開倉：之前無倉位，現在有倉位
        strat_df['Entry'] = ~strat_df['Was_In_Position'] & strat_df['Is_In_Position']
        # 平倉：之前有倉位，現在無倉位
        strat_df['Exit'] = strat_df['Was_In_Position'] & ~strat_df['Is_In_Position']
        
        entry_rows = strat_df[strat_df['Entry']].copy()
        exit_rows = strat_df[strat_df['Exit']].copy()
        
        # 記錄所有開倉點
        entry_list = []
        for index, row in entry_rows.iterrows():
            date_str = self._format_date(index, strat_df)
            exec_price = row['Exec_Price']  # 使用執行價格
            entry_info = {
                "time": date_str,
                "type": "BUY",
                "price": round(exec_price, 2),
                "size": round(row['Position'], 4),
                "value": round(row['Position'] * exec_price, 2),
                "position_after": round(row['Position'], 4),  # 交易後持倉
                "pnl": 0.0,  # 開倉時無盈虧
                "cumulative_pnl": round(cumulative_pnl, 2)
            }
            trades.append(entry_info)
            entry_list.append((index, exec_price, row['Position']))
        
        # 記錄所有平倉點並計算盈虧
        exit_idx = 0
        for index, row in exit_rows.iterrows():
            date_str = self._format_date(index, strat_df)
            exec_price = row['Exec_Price']  # 使用執行價格
            
            exit_info = {
                "time": date_str,
                "type": "SELL",
                "price": round(exec_price, 2),
                "size": 1.0,
                "value": round(exec_price, 2),
                "position_after": 0.0,  # 平倉後無持倉
                "pnl": 0.0,
                "cumulative_pnl": 0.0
            }
            
            # 匹配對應的買入點計算盈虧
            if exit_idx < len(entry_list):
                entry_date, entry_price, entry_size = entry_list[exit_idx]
                trade_pnl = (exec_price - entry_price) * entry_size
                cumulative_pnl += trade_pnl
                exit_info["pnl"] = round(trade_pnl, 2)
                exit_info["cumulative_pnl"] = round(cumulative_pnl, 2)
                exit_info["size"] = round(entry_size, 4)
                exit_info["value"] = round(exec_price * entry_size, 2)
                trade_returns.append(trade_pnl)
                exit_idx += 1
            
            trades.append(exit_info)

        # --- Architecture V2: Use Analyzers ---
        context = {
            "initial_capital": self.initial_capital,
            "trades": trades
        }
        
        sharpe_analyzer = SharpeAnalyzer()
        drawdown_analyzer = DrawdownAnalyzer()
        trade_analyzer = TradeAnalyzer()
        
        m1 = sharpe_analyzer.analyze(strat_df, context)
        m2 = drawdown_analyzer.analyze(strat_df, context)
        m3 = trade_analyzer.analyze(strat_df, context)
        
        metrics = {**m1, **m2, **m3}
        metrics['Final_Equity'] = strat_df['Equity'].iloc[-1]
        metrics['Total_Return'] = strat_df['Equity'].iloc[-1] / self.initial_capital - 1
        
        # Backward Compatibility Keys if Analyzers miss small logic details from before
        # (Though TradeAnalyzer covers Win_Rate, Profit_Factor etc)
        
        # Add Aux metrics manually if not in Analyzers yet (Kelly, Avg Win)
        # To strictly refactor, we should move these to TradeAnalyzer, but let's keep Hybrid for now
        # to ensure no regression on specific keys used by frontend.
        if len(trade_returns) > 0:
            wins = [pnl for pnl in trade_returns if pnl > 0]
            losses = [pnl for pnl in trade_returns if pnl < 0]
            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean(losses) if losses else 0
            win_rate = metrics.get('Win_Rate', 0)
            
            if avg_win > 0:
                kelly = (win_rate - (1 - win_rate) * abs(avg_loss) / avg_win)
                kelly = max(0, min(kelly, 1))
            else:
                kelly = 0
            
            metrics['Kelly'] = kelly
            metrics['Avg_Win'] = avg_win
            metrics['Avg_Loss'] = avg_loss
        else:
             metrics['Kelly'] = 0.1
             metrics['Avg_Win'] = 0
             metrics['Avg_Loss'] = 0
             
        # Re-assign calculated metrics to ensure variable availability for existing return structure
        # (End of V2 logic)

        logger.info(f"Backtest Complete. Sharpe: {metrics.get('Sharpe_Ratio', 0):.2f}. Trades: {len(trades)}")
        
        # Handle Dates
        dates = []
        if isinstance(strat_df.index, pd.DatetimeIndex):
            dates = [d.strftime("%Y-%m-%d") for d in strat_df.index]
        else:
            dates = [str(d) for d in strat_df.index]
            
        return {
            "metrics": metrics, 
            "equity_curve": strat_df['Equity'].tolist(),
            "dates": dates,
            "trades": trades, # Phase 12
            "daily_returns": strat_df['Strat_Ret'].tolist()  # 新增: 用於收益分佈
        }
    
    @staticmethod
    def get_return_distribution(daily_returns: list, bins: int = 20) -> dict:
        """
        計算收益率分佈直方圖數據
        
        Args:
            daily_returns: 每日收益率列表
            bins: 分桶數量 (默認 20)
        
        Returns:
            dict: {
                "bins": [(-0.05, -0.04), ...],  # 區間
                "counts": [5, 10, ...],          # 每區間數量
                "percentages": [2.5, 5.0, ...],  # 百分比
                "stats": {mean, std, skew, kurtosis}
            }
        """
        import numpy as np
        from scipy import stats as scipy_stats
        
        returns = np.array([r for r in daily_returns if not np.isnan(r)])
        
        if len(returns) == 0:
            return {"error": "No valid returns data"}
        
        # 計算直方圖
        counts, bin_edges = np.histogram(returns, bins=bins)
        
        # 構建區間標籤
        bin_labels = []
        for i in range(len(bin_edges) - 1):
            bin_labels.append({
                "min": round(bin_edges[i] * 100, 2),  # 轉為百分比
                "max": round(bin_edges[i + 1] * 100, 2)
            })
        
        # 計算統計量
        total = len(returns)
        percentages = [round(c / total * 100, 2) for c in counts]
        
        distribution_stats = {
            "mean": round(float(np.mean(returns)) * 100, 4),
            "std": round(float(np.std(returns)) * 100, 4),
            "skew": round(float(scipy_stats.skew(returns)), 4),
            "kurtosis": round(float(scipy_stats.kurtosis(returns)), 4),
            "median": round(float(np.median(returns)) * 100, 4),
            "positive_days": int(np.sum(returns > 0)),
            "negative_days": int(np.sum(returns < 0)),
            "total_days": total
        }
        
        return {
            "bins": bin_labels,
            "counts": counts.tolist(),
            "percentages": percentages,
            "stats": distribution_stats
        }

if __name__ == "__main__":
    print("--- SELF-TEST START: backtest_engine.py ---")
    
    # Dummy Data: Uptrend
    x = np.linspace(0, 100, 200)
    prices = 100 + x 
    df = pd.DataFrame({'Close': prices})
    
    # Strategy
    class DummyStrategy:
        def generate_signals(self, df):
            df = df.copy()
            df['Signal'] = 1
            df['Position'] = 1.0 # Always Long
            return df
            
    bt = Backtester()
    res = bt.run_backtest(df, DummyStrategy())
    
    print("[TEST] Metrics:", res['metrics'])
    
    if res['metrics']['Total_Return'] > 0:
        print("[TEST] SUCCESS: Backtest generated positive return on uptrend.")
    else:
        print("[TEST] FAILURE: Backtest logic error.")
        
    print("--- SELF-TEST END ---")
