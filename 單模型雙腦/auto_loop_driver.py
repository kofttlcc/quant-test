#!/usr/bin/env python3
import os
import time
import json
import subprocess
import sys
import shutil
from datetime import datetime

# ==========================================
# 配置區域 (Configuration)
# ==========================================
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3-pro")

# 路徑設定
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) # coding/單模型雙腦/
BASE_DIR = os.path.dirname(CURRENT_DIR) # coding/
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
STATE_FILE = os.path.join(ARTIFACTS_DIR, "dual_brain_state.json")

# Context 文件源 (模板)
CTX_SRC_BUILDER = os.path.join(CURRENT_DIR, "contexts", "builder.md")
CTX_SRC_AUDITOR = os.path.join(CURRENT_DIR, "contexts", "auditor.md")

# 目標 Context 文件 (gemini-cli 讀取的默認文件)
GEMINI_CONTEXT_FILE = os.path.join(BASE_DIR, "GEMINI.md")

# 文件標誌
FILE_BUILDER_HANDOFF = "handoff_notes.md"
FILE_AUDITOR_REJECT = "auditor_handoff.md"
FILE_AUDITOR_APPROVE_PREFIX = "audit_approval_"

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

def swap_context(role):
    """
    將對應角色的 Context 文件複製為 GEMINI.md
    """
    src = CTX_SRC_BUILDER if role == "builder" else CTX_SRC_AUDITOR
    try:
        shutil.copy(src, GEMINI_CONTEXT_FILE)
        log("SYSTEM", f"Swapped context to {role.upper()} (GEMINI.md updated)")
        return True
    except FileNotFoundError:
        log("ERROR", f"Context file not found: {src}")
        return False
    except Exception as e:
        log("ERROR", f"Failed to swap context: {e}")
        return False

def run_gemini_cli(prompt):
    """
    調用 gemini-cli 執行指令
    注意：不再傳遞 --context 參數，而是依賴 swap_context 準備好的 GEMINI.md
    """
    cmd = [
        "gemini",
        "-m", MODEL_NAME,
        "-p", prompt
    ]
    
    log("SYSTEM", f"Executing: {' '.join(cmd)}")
    try:
        # 使用 subprocess 調用，確保在 BASE_DIR (coding/) 下執行，這樣才能讀取到 GEMINI.md
        result = subprocess.run(cmd, cwd=BASE_DIR, text=True, capture_output=False)
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
            if current_role == "builder":
                log("LOOP", "Switching to BUILDER brain...")
                state["current_turn"] = "builder"
                save_state(state)

                # 1. 切換 Context
                if not swap_context("builder"):
                    break

                # 2. 觸發 Builder
                success = run_gemini_cli("【指令】請執行 /vibe-build 流程。讀取 artifacts/ 下最新的文件（handoff 或 audit_approval），規劃下一步並生成 handoff_notes.md。")
                
                if not success:
                    break
                
                # 3. 等待產出
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
                state["current_turn"] = "auditor"
                save_state(state)

                # 1. 切換 Context
                if not swap_context("auditor"):
                    break

                # 2. 觸發 Auditor
                success = run_gemini_cli("【指令】請執行 /vibe-audit 流程。仔細審閱 artifacts/handoff_notes.md 及相關代碼，生成 audit_approval_*.md (通過) 或 auditor_handoff.md (拒絕)。")
                
                if not success:
                    break
                
                # 3. 等待產出
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
