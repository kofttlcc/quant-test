
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
except (ImportError, TypeError):
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
        執行回測
        
        Args:
            df (pd.DataFrame): OHLCV 數據 (必須包含 DatetimeIndex)
            strategy: 策略對象，必須包含 generate_signals 方法
            
        Returns:
            dict: 包含 Metrics (性能指標), Equity Curve (權益曲線) 等
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
        
        # 2. Calculate Returns (CRITICAL FIX: Next Open Execution)
        # 由於交易在「次日開盤」執行：
        # - 隔夜時段 (Close[t-1] -> Open[t]): 持有的是「前一日」的倉位 (由 Signal[t-2] 決定)
        # - 日內時段 (Open[t] -> Close[t]): 持有的是「當日」的倉位 (由 Signal[t-1] 決定，已在 Open[t] 執行)
        
        if 'Open' in strat_df.columns:
            # 計算分割收益
            strat_df['Ret_Gap'] = (strat_df['Open'] / strat_df['Close'].shift(1)) - 1
            strat_df['Ret_Intraday'] = (strat_df['Close'] / strat_df['Open']) - 1
            
            # 對齊持倉
            # Position 由 Close[t] 產生 -> Next Open[t+1] 執行
            # Gap[t] (C[t-1]->O[t]): 倉位是 P[t-2]
            # Intraday[t] (O[t]->C[t]): 倉位是 P[t-1]
            strat_df['Pos_Gap'] = strat_df['Position'].shift(2).fillna(0)
            strat_df['Pos_Intraday'] = strat_df['Position'].shift(1).fillna(0)
            
            # 組合策略收益: (1 + GapRet) * (1 + IntradayRet) - 1
            # 這裡分別應用持倉權重
            # 注意：這裡簡化處理，假設槓桿為 1 或 0 (Long/Flat)
            # Log Return 可能更精確，但這裡使用 Simple Return 逼近: Ret = P_gap * R_gap + P_intra * R_intra
            # 為了更精確 Compound:
            strat_df['Strat_Ret'] = (1 + strat_df['Pos_Gap'] * strat_df['Ret_Gap']) * \
                                    (1 + strat_df['Pos_Intraday'] * strat_df['Ret_Intraday']) - 1
                                    
            # 填充 NaN (第一天)
            strat_df['Strat_Ret'] = strat_df['Strat_Ret'].fillna(0)
            
            # 定義執行價格 (用於 Trade Log)
            strat_df['Exec_Price'] = strat_df['Open'].shift(-1) # T+1 Open
        else:
            # Fallback: 無 Open 數據，只能退回 Close-to-Close
            logger.warning("No 'Open' price found. Falling back to Close-to-Close execution (Less Accurate).")
            strat_df['Asset_Ret'] = strat_df['Close'].pct_change()
            strat_df['Strat_Ret'] = strat_df['Position'].shift(1) * strat_df['Asset_Ret']
            strat_df['Exec_Price'] = strat_df['Close'] # Fallback
            
        # Calculate Turnover & Cost
        # 交易發生在 Open[t]，倉位從 P[t-2] 變為 P[t-1]
        # Diff is between P[t-1] and P[t-2]
        # Shift(1) gives P[t-1], Shift(2) gives P[t-2]
        strat_df['Turnover'] = (strat_df['Position'].shift(1) - strat_df['Position'].shift(2)).abs().fillna(0)
        strat_df['Cost'] = strat_df['Turnover'] * self.commission_rate
        
        # 扣除成本
        strat_df['Strat_Ret'] = strat_df['Strat_Ret'] - strat_df['Cost']
        
        # 3. Equity Curve
        strat_df['Equity'] = self.initial_capital * (1 + strat_df['Strat_Ret']).cumprod()

        
        
        # 記錄持倉狀態變化：0 → 非0 = 開倉(BUY)，非0 → 0 = 平倉(SELL)
        strat_df['Was_In_Position'] = (strat_df['Position'].shift(1).fillna(0) > 0)
        strat_df['Is_In_Position'] = (strat_df['Position'] > 0)
        
        # 開倉：之前無倉位，現在有倉位
        strat_df['Entry'] = ~strat_df['Was_In_Position'] & strat_df['Is_In_Position']
        # 平倉：之前有倉位，現在無倉位
        strat_df['Exit'] = strat_df['Was_In_Position'] & ~strat_df['Is_In_Position']
        
        entry_rows = strat_df[strat_df['Entry']].copy()
        exit_rows = strat_df[strat_df['Exit']].copy()
        
        # Initialize Trade Logs
        trades = []
        trade_returns = []
        cumulative_pnl = 0.0
        
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
                
                # [MED-004] Deduct Commission (Round-trip)
                # Assuming simple fixed rate or reusing self.commission_rate if accessible
                # Since 'commission' variable is calculated in the loop (line 144: commission = cost * self.commission_rate)
                # But that's per transaction.
                # Here we are closing a trade. We paid entry commission and exit commission.
                # The 'cumulative_pnl' tracked in the loop already subtracts commission at each STEP (line 156: self.cash -= (cost + commission)).
                # However, valid 'trade_pnl' for analysis usually refers to Gross PnL or Net PnL.
                # If 'cumulative_pnl' updates cash, it includes commission.
                # But 'trade_pnl' calculated here is Gross.
                # Let's deduct commission to make it Net PnL for the trade record.
                # Entry cost = entry_price * entry_size
                # Exit cost = exec_price * entry_size
                # Comm = (Entry + Exit) * rate
                
                # We don't have commission_rate in local scope easily unless we use self.commission_rate
                # Assuming self.commission_rate is available (it is a class member)
                
                total_val = (entry_price + exec_price) * abs(entry_size)
                trade_comm = total_val * self.commission_rate
                trade_pnl -= trade_comm
                
                cumulative_pnl += trade_pnl # Wait, cumulative_pnl in loop is mostly for tracking? 
                # Actually, 'cumulative_pnl' variable here (line 173 init) aggregates 'trade_pnl'.
                # So if we want 'cumulative_pnl' to be Net, we must deduct commission.
                
                exit_info["pnl"] = round(trade_pnl, 2)
                exit_info["cumulative_pnl"] = round(cumulative_pnl, 2)
                exit_info["size"] = round(entry_size, 4)
                exit_info["value"] = round(exec_price * entry_size, 2)
                exit_info["commission"] = round(trade_comm, 4) # Add record
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
        
        # [MED-004] Expose Total Commission
        total_comm = strat_df['Cost'].sum()
        metrics['Total_Commission'] = total_comm
        
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

        # --- Phase 2: Advanced Risk Metrics (Trad-Fi) ---
        risk_metrics = self._calc_risk_metrics(strat_df['Strat_Ret'])
        metrics.update(risk_metrics)
        # ------------------------------------------------

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

    def run_portfolio_backtest(self, asset_returns: pd.DataFrame, weights: pd.DataFrame) -> dict:
        """
        執行投資組合回測 (支持動態權重)
        
        Args:
            asset_returns (pd.DataFrame): 資產收益率矩陣 (index=Date, columns=Assets)
            weights (pd.DataFrame): 資產權重矩陣 (index=Date, columns=Assets)
            
        Returns:
            dict: 性能指標與權益曲線
        """
        # Align dates
        common_idx = asset_returns.index.intersection(weights.index)
        if len(common_idx) == 0:
            return {"error": "No overlapping dates between returns and weights"}
            
        returns = asset_returns.loc[common_idx]
        w = weights.loc[common_idx]
        
        # Portfolio Return = sum(Weight * Return)
        # Shift weights because allocation at t affects return at t+1 (or same day depending on execution)
        # Assuming weights are set at Open/Close of t, and capturing Return of t (if rebalanced at Open)
        # Standard: Weights determined at t-1 Close (or t Open), applied to t Returns.
        
        # Here we assume 'weights' row T is the allocation for day T.
        port_ret = (returns * w).sum(axis=1)
        
        # Subtract Turnover Cost
        turnover = w.diff().abs().sum(axis=1).fillna(0)
        cost = turnover * self.commission_rate
        
        net_ret = port_ret - cost
        
        # Equity Curve
        equity = self.initial_capital * (1 + net_ret).cumprod()
        
        # Metrics
        strat_df = pd.DataFrame({'Strat_Ret': net_ret, 'Equity': equity})
        
        # Reuse risk metrics
        metrics = self._calc_risk_metrics(net_ret)
        metrics['Total_Return'] = equity.iloc[-1] / self.initial_capital - 1
        metrics['Final_Equity'] = equity.iloc[-1]
        metrics['Sharpe_Ratio'] = self._calc_sharpe(net_ret)
        
        return {
            "metrics": metrics,
            "equity_curve": equity.tolist(),
            "dates": [str(d) for d in equity.index],
            "daily_returns": net_ret.tolist()
        }
    
    def _calc_sharpe(self, returns, rf=0.0):
        if returns.std() == 0: return 0
        return (returns.mean() - rf/252) / returns.std() * np.sqrt(252)
    
    def _calc_risk_metrics(self, returns: pd.Series, alpha=0.95, rf=0.0) -> dict:
        """
        計算 VaR, CVaR 與 Sortino Ratio (Skill: trad-fi-risk).
        """
        if len(returns) < 2:
            return {}

        try:
             # Convert to numpy and drop NaNs
            rets_np = returns.dropna().values
            if len(rets_np) == 0: return {}
            
            # 1. VaR & CVaR (Historical Method)
            # 取分佈的左尾 (損失是負收益)
            var_level = 1 - alpha
            # quantile method in numpy: 0.05 quantile is the 5% worst return
            var_val = np.percentile(rets_np, var_level * 100)
            
            # CVaR: 所有小於等於 VaR 的收益率的平均值
            tail_losses = rets_np[rets_np <= var_val]
            cvar_val = tail_losses.mean() if len(tail_losses) > 0 else var_val
            
            # 2. Sortino Ratio
            excess_ret = rets_np - rf
            # 僅考慮負收益部分 (下行風險)
            downside_ret = np.minimum(0, excess_ret)
            downside_dev = np.sqrt(np.mean(downside_ret**2))
            
            if downside_dev == 0:
                sortino = 0.0 # Avoid Inf
            else:
                # Annualize typically? If returns are daily:
                # Sortino = (Mean_Daily_Exc_Ret * 252) / (Downside_Dev_Daily * sqrt(252))
                # = Mean * 252 / (DD * 15.87) 
                # = (Mean/DD) * sqrt(252)
                sortino = (np.mean(excess_ret) / downside_dev) * np.sqrt(252)

            return {
                'VaR_95': float(var_val),
                'CVaR_95': float(cvar_val),
                'Sortino_Ratio': float(sortino)
            }
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}

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
