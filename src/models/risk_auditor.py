"""
risk_auditor.py - 模型邏輯審計與風控模組
=========================================
版本: v1.0 (Phase 2 Sprint 2)
功能:
1. 靜態代碼分析 (檢查未來函數、硬編碼風險)
2. 壓力測試 (Stress Testing)

移植自: old-system/risk_auditor.py
"""

import os
import logging
from typing import List, Dict, Any
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelAuditor:
    """模型審計器"""
    
    RISKY_KEYWORDS = [
        "shift(-1)", "shift(-2)",  # Look-ahead bias
        "future", "lookahead", "tomorrow", "next_day",
        "hardcode", "hack", "fix", "TODO"
    ]
    
    def audit_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        靜態代碼分析
        檢查源代碼中是否包含潛在的風險關鍵詞或模式
        
        Args:
            file_path: 要審計的文件路徑
            
        Returns:
            發現的問題列表
        """
        findings = []
        
        if not os.path.exists(file_path):
            return [{"type": "error", "message": f"File not found: {file_path}"}]
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines):
                lower_line = line.lower()
                stripped = line.strip()
                
                # 跳過註釋
                if stripped.startswith("#"):
                    continue
                    
                for kw in self.RISKY_KEYWORDS:
                    if kw.lower() in lower_line:
                        findings.append({
                            "type": "warning",
                            "line": i + 1,
                            "keyword": kw,
                            "content": stripped[:80],
                            "file": os.path.basename(file_path)
                        })
                        
        except Exception as e:
            findings.append({"type": "error", "message": f"Audit failed: {e}"})
            
        return findings
    
    def audit_directory(self, dir_path: str, extensions: List[str] = [".py"]) -> Dict[str, List]:
        """
        審計整個目錄
        
        Args:
            dir_path: 目錄路徑
            extensions: 要審計的文件擴展名
            
        Returns:
            文件名到發現列表的映射
        """
        all_findings = {}
        
        for root, dirs, files in os.walk(dir_path):
            # 跳過 venv, __pycache__ 等
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', 'node_modules', '.git']]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    findings = self.audit_file(file_path)
                    if findings:
                        all_findings[file_path] = findings
                        
        return all_findings
    
    def generate_report(self, findings: Dict[str, List]) -> str:
        """生成審計報告"""
        if not findings:
            return "✅ 審計通過：未發現風險關鍵詞"
            
        report = ["# 代碼審計報告\n"]
        total_issues = sum(len(v) for v in findings.values())
        report.append(f"**發現問題數量**: {total_issues}\n")
        
        for file_path, issues in findings.items():
            report.append(f"\n## {os.path.basename(file_path)}")
            for issue in issues:
                if issue.get("type") == "warning":
                    report.append(f"- Line {issue['line']}: `{issue['keyword']}` - {issue['content']}")
                else:
                    report.append(f"- {issue.get('message', 'Unknown error')}")
                    
        return "\n".join(report)


class StressTester:
    """壓力測試器"""
    
    SCENARIOS = {
        "normal": {"wacc": 0.09, "growth": 0.08, "description": "正常市場"},
        "high_inflation": {"wacc": 0.15, "growth": 0.02, "description": "高通脹"},
        "crash": {"wacc": 0.12, "growth": -0.05, "description": "市場崩盤"},
        "euphoria": {"wacc": 0.04, "growth": 0.20, "description": "泡沫狂歡"},
        "zero_interest": {"wacc": 0.01, "growth": 0.05, "description": "零利率"}
    }
    
    def run_valuation_stress_test(self, valuation_func, fcf: float = 1000000) -> Dict[str, Any]:
        """
        運行估值模型壓力測試
        
        Args:
            valuation_func: 估值函數，接受 (fcf, wacc, growth) 返回估值
            fcf: 自由現金流
            
        Returns:
            測試結果
        """
        results = {}
        all_passed = True
        
        for name, params in self.SCENARIOS.items():
            try:
                value = valuation_func(fcf, params["wacc"], params["growth"])
                
                status = "PASS"
                if value is None:
                    status = "FAIL: None returned"
                    all_passed = False
                elif value < 0:
                    status = "WARN: Negative value"
                elif value > fcf * 1000:
                    status = "WARN: Extremely high"
                    
                results[name] = {
                    "params": params,
                    "value": value,
                    "status": status
                }
                
            except Exception as e:
                results[name] = {
                    "params": params,
                    "error": str(e),
                    "status": "FAIL: Exception"
                }
                all_passed = False
                
        return {"passed": all_passed, "scenarios": results}


if __name__ == "__main__":
    print("--- SELF-TEST: risk_auditor.py ---")
    
    auditor = ModelAuditor()
    
    # 測試審計當前目錄
    print("\n[TEST] Auditing src/backend/")
    findings = auditor.audit_directory("src/backend/")
    report = auditor.generate_report(findings)
    print(report[:500] if len(report) > 500 else report)
    
    # 測試壓力測試
    print("\n[TEST] Stress Test")
    tester = StressTester()
    
    def simple_dcf(fcf, wacc, growth):
        if wacc <= growth:
            return None
        return fcf / (wacc - growth)
    
    results = tester.run_valuation_stress_test(simple_dcf)
    print(f"All scenarios passed: {results['passed']}")
    for name, data in results['scenarios'].items():
        print(f"  {name}: {data['status']}")
    
    print("\n--- SELF-TEST COMPLETE ---")
