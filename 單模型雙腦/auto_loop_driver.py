#!/usr/bin/env python3
import os
import time
import json
import subprocess
import sys
from datetime import datetime

# ==========================================
# 配置區域 (Configuration)
# ==========================================
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3-pro")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
STATE_FILE = os.path.join(ARTIFACTS_DIR, "dual_brain_state.json")

# 文件標誌
FILE_BUILDER_HANDOFF = "handoff_notes.md"
FILE_AUDITOR_REJECT = "auditor_handoff.md"
FILE_AUDITOR_APPROVE_PREFIX = "audit_approval_"

# CLI 上下文
CTX_BUILDER = "builder_brain"
CTX_AUDITOR = "auditor_brain"

# ==========================================
# 工具函數 (Utils)
# ==========================================

def log(role, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{role.upper()}] {message}")

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "current_turn": "builder",
            "iteration_count": 0,
            "last_action": "init",
            "status": "running",
            "last_update": datetime.now().isoformat()
        }
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        log("ERROR", "State file corrupted. Resetting.")
        return {"current_turn": "builder", "status": "running"}

def save_state(state):
    state["last_update"] = datetime.now().isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def run_gemini_cli(prompt, context):
    cmd = [
        "gemini",
        "-m", MODEL_NAME,
        "--context", context,
        "-p", prompt
    ]
    
    log("SYSTEM", f"Executing: {' '.join(cmd)}")
    try:
        # 使用 subprocess 調用，將輸出直接流式傳輸到終端
        result = subprocess.run(cmd, text=True, capture_output=False)
        if result.returncode != 0:
            log("ERROR", f"Gemini CLI failed with code {result.returncode}")
            return False
        return True
    except FileNotFoundError:
        log("ERROR", "Command 'gemini' not found. Please ensure gemini-cli is installed.")
        return False

def check_file_update(filename, last_check_time):
    path = os.path.join(ARTIFACTS_DIR, filename)
    if os.path.exists(path):
        mtime = os.path.getmtime(path)
        if mtime > last_check_time:
            return True, mtime
    return False, last_check_time

def find_latest_approval(last_check_time):
    latest_time = last_check_time
    found = False
    if not os.path.exists(ARTIFACTS_DIR):
        return False, latest_time
        
    for f in os.listdir(ARTIFACTS_DIR):
        if f.startswith(FILE_AUDITOR_APPROVE_PREFIX) and f.endswith(".md"):
            path = os.path.join(ARTIFACTS_DIR, f)
            mtime = os.path.getmtime(path)
            if mtime > latest_time:
                latest_time = mtime
                found = True
    return found, latest_time

# ==========================================
# 主邏輯 (Main Loop)
# ==========================================

def main():
    if not os.path.exists(ARTIFACTS_DIR):
        try:
            os.makedirs(ARTIFACTS_DIR)
        except OSError as e:
            log("ERROR", f"Could not create artifacts dir: {e}")
            sys.exit(1)

    log("SYSTEM", f"Starting Single Model Dual Brain Loop (Model: {MODEL_NAME})")
    
    # 加載狀態
    state = load_state()
    current_role = state.get("current_turn", "builder")
    last_check_time = time.time()
    
    log("SYSTEM", f"Resuming from state: {current_role}")
    
    try:
        while True:
            # 每次循環重新加載狀態（可選，防止外部修改）
            # state = load_state() 
            
            if current_role == "builder":
                log("LOOP", "Switching to BUILDER brain...")
                
                # 更新狀態
                state["current_turn"] = "builder"
                save_state(state)

                # 觸發 Builder
                success = run_gemini_cli("請執行 /vibe-build 流程。讀取最新的審計反饋（若有），並生成 handoff_notes.md。", CTX_BUILDER)
                
                if not success:
                    break
                
                # 等待產出
                log("WAIT", "Waiting for 'handoff_notes.md' update...")
                while True:
                    updated, new_time = check_file_update(FILE_BUILDER_HANDOFF, last_check_time)
                    if updated:
                        log("EVENT", "Builder finished! Handoff detected.")
                        last_check_time = new_time
                        current_role = "auditor"
                        state["last_action"] = "handoff_generated"
                        save_state(state)
                        break
                    time.sleep(2)
                    
            elif current_role == "auditor":
                log("LOOP", "Switching to AUDITOR brain...")
                
                # 更新狀態
                state["current_turn"] = "auditor"
                save_state(state)

                # 觸發 Auditor
                success = run_gemini_cli("請執行 /vibe-audit 流程。讀取 handoff_notes.md，並生成 audit_approval_*.md 或 auditor_handoff.md。", CTX_AUDITOR)
                
                if not success:
                    break
                
                # 等待產出
                log("WAIT", "Waiting for Audit Decision...")
                while True:
                    # 檢查拒絕
                    rejected, t1 = check_file_update(FILE_AUDITOR_REJECT, last_check_time)
                    if rejected:
                        log("EVENT", "Auditor REJECTED. Looping back to Builder.")
                        last_check_time = t1
                        current_role = "builder"
                        state["last_action"] = "audit_rejected"
                        state["iteration_count"] = state.get("iteration_count", 0) + 1
                        save_state(state)
                        break
                    
                    # 檢查批准
                    approved, t2 = find_latest_approval(last_check_time)
                    if approved:
                        log("EVENT", "Auditor APPROVED. Looping back to Builder.")
                        last_check_time = t2
                        current_role = "builder"
                        state["last_action"] = "audit_approved"
                        state["iteration_count"] = state.get("iteration_count", 0) + 1
                        save_state(state)
                        break
                        
                    time.sleep(2)
            
            time.sleep(1)

    except KeyboardInterrupt:
        log("STOP", "User interrupted.")
        state["status"] = "stopped"
        save_state(state)

if __name__ == "__main__":
    main()
