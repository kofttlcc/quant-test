"""
valuation_sensitivity.py - 敏感度分析模組
=============================================
版本: v1.0
功能: DCF 模型敏感度分析 (WACC vs 成長率)
"""

import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class SensitivityResult:
    """敏感度分析結果"""
    base_value: float
    wacc_range: List[float]
    growth_range: List[float]
    sensitivity_matrix: List[List[float]]


class SensitivityAnalyzer:
    """
    DCF 敏感度分析器
    
    計算不同 WACC 和永續成長率組合下的公允價值
    """
    
    def __init__(self, base_fcf: float, shares_outstanding: float):
        """
        初始化
        
        Args:
            base_fcf: 基礎自由現金流
            shares_outstanding: 流通股數
        """
        self.base_fcf = base_fcf
        self.shares = shares_outstanding
    
    def calculate_dcf_value(
        self, 
        wacc: float, 
        growth_rate: float, 
        projection_years: int = 5,
        growth_decay: float = 0.85
    ) -> float:
        """
        計算單一 DCF 公允價值
        
        Args:
            wacc: 加權平均資本成本 (e.g., 0.08 = 8%)
            growth_rate: 永續成長率 (e.g., 0.025 = 2.5%)
            projection_years: 預測年數
            growth_decay: 成長率衰減因子
        
        Returns:
            每股公允價值
        """
        if wacc <= growth_rate:
            return 0.0  # 避免無意義結果
        
        # 計算預測期現金流
        fcf = self.base_fcf
        npv = 0.0
        current_growth = 0.10  # 初始 10% 成長
        
        for year in range(1, projection_years + 1):
            fcf *= (1 + current_growth)
            npv += fcf / ((1 + wacc) ** year)
            current_growth *= growth_decay  # 成長率衰減
        
        # 計算終值 (Gordon Growth Model)
        terminal_value = fcf * (1 + growth_rate) / (wacc - growth_rate)
        terminal_pv = terminal_value / ((1 + wacc) ** projection_years)
        
        enterprise_value = npv + terminal_pv
        equity_value = enterprise_value  # 簡化：假設無淨負債
        
        return equity_value / self.shares if self.shares > 0 else 0.0
    
    def run_sensitivity(
        self,
        wacc_range: List[float] = None,
        growth_range: List[float] = None
    ) -> SensitivityResult:
        """
        執行敏感度分析
        
        Args:
            wacc_range: WACC 範圍列表 (e.g., [0.07, 0.08, 0.09])
            growth_range: 成長率範圍列表 (e.g., [0.02, 0.025, 0.03])
        
        Returns:
            敏感度分析結果
        """
        if wacc_range is None:
            wacc_range = [0.065, 0.07, 0.075, 0.08, 0.085, 0.09, 0.095]
        
        if growth_range is None:
            growth_range = [0.015, 0.02, 0.025, 0.03, 0.035]
        
        # 計算基準值
        base_wacc = 0.08
        base_growth = 0.025
        base_value = self.calculate_dcf_value(base_wacc, base_growth)
        
        # 生成敏感度矩陣
        matrix = []
        for wacc in wacc_range:
            row = []
            for g in growth_range:
                value = self.calculate_dcf_value(wacc, g)
                row.append(round(value, 2))
            matrix.append(row)
        
        return SensitivityResult(
            base_value=round(base_value, 2),
            wacc_range=[round(w * 100, 1) for w in wacc_range],
            growth_range=[round(g * 100, 1) for g in growth_range],
            sensitivity_matrix=matrix
        )


def calculate_sensitivity(
    base_fcf: float,
    shares_outstanding: float,
    wacc_range: List[float] = None,
    growth_range: List[float] = None
) -> Dict[str, Any]:
    """
    便捷函數：執行敏感度分析
    
    Args:
        base_fcf: 基礎自由現金流
        shares_outstanding: 流通股數
        wacc_range: WACC 範圍 (可選)
        growth_range: 成長率範圍 (可選)
    
    Returns:
        敏感度分析結果字典
    """
    analyzer = SensitivityAnalyzer(base_fcf, shares_outstanding)
    result = analyzer.run_sensitivity(wacc_range, growth_range)
    return asdict(result)


if __name__ == "__main__":
    print("--- SELF-TEST: valuation_sensitivity.py ---")
    
    # Apple 示例數據 (假設)
    base_fcf = 100_000_000_000  # 100B FCF
    shares = 15_500_000_000     # 15.5B shares
    
    result = calculate_sensitivity(base_fcf, shares)
    
    print(f"\n基準公允價值: ${result['base_value']}")
    print(f"\nWACC 範圍: {result['wacc_range']}")
    print(f"成長率範圍: {result['growth_range']}")
    
    print("\n敏感度矩陣 (WACC \\ Growth):")
    print("WACC\\g", end="\t")
    for g in result['growth_range']:
        print(f"{g}%", end="\t")
    print()
    
    for i, wacc in enumerate(result['wacc_range']):
        print(f"{wacc}%", end="\t")
        for val in result['sensitivity_matrix'][i]:
            print(f"${val}", end="\t")
        print()
    
    print("\n--- SELF-TEST COMPLETE ---")
