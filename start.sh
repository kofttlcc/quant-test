#!/bin/bash
# ============================================
# Gemini Quant System - 一鍵啟動腳本
# ============================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_PORT=5001
FRONTEND_PORT=5173

# 使用虛擬環境中的 Python
PYTHON_BIN="$PROJECT_DIR/venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    # 回退到系統 python3
    PYTHON_BIN="python3"
    echo "⚠️ 未找到 venv，使用系統 Python"
fi

echo "🚀 啟動 Gemini Quant 系統..."
echo "================================"

# 檢查依賴
check_dependencies() {
    echo "📦 檢查依賴..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 未安裝"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo "❌ npm 未安裝"
        exit 1
    fi
    
    echo "✅ 依賴檢查通過"
}

# 殺掉已存在的進程
kill_existing_processes() {
    echo ""
    echo "🔍 檢查已存在的進程..."
    
    # 殺掉已存在的後端進程
    EXISTING_BACKEND=$(pgrep -f "api_server.py" 2>/dev/null || true)
    if [ -n "$EXISTING_BACKEND" ]; then
        echo "   發現已存在的後端進程 (PID: $EXISTING_BACKEND)，正在終止..."
        kill $EXISTING_BACKEND 2>/dev/null || true
        sleep 1
    fi
    
    # 殺掉已存在的前端進程 (vite)
    EXISTING_FRONTEND=$(pgrep -f "vite" 2>/dev/null | head -1 || true)
    if [ -n "$EXISTING_FRONTEND" ]; then
        echo "   發現已存在的前端進程 (PID: $EXISTING_FRONTEND)，正在終止..."
        kill $EXISTING_FRONTEND 2>/dev/null || true
        sleep 1
    fi
    
    # 檢查端口佔用
    if lsof -i :$BACKEND_PORT > /dev/null 2>&1; then
        echo "   端口 $BACKEND_PORT 被佔用，正在釋放..."
        lsof -ti :$BACKEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    if lsof -i :$FRONTEND_PORT > /dev/null 2>&1; then
        echo "   端口 $FRONTEND_PORT 被佔用，正在釋放..."
        lsof -ti :$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    echo "✅ 進程清理完成"
}

# 啟動後端
start_backend() {
    echo ""
    echo "🔧 啟動後端 (Port: $BACKEND_PORT)..."
    cd "$PROJECT_DIR"
    export PYTHONPATH=$PROJECT_DIR
    $PYTHON_BIN src/api/main.py &
    BACKEND_PID=$!
    echo "   Backend PID: $BACKEND_PID"
    sleep 2
    
    # 健康檢查
    if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null; then
        echo "✅ 後端啟動成功"
    else
        echo "⚠️ 後端可能需要更多時間啟動..."
    fi
}

# 啟動前端
start_frontend() {
    echo ""
    echo "🎨 啟動前端 (Port: $FRONTEND_PORT)..."
    cd "$PROJECT_DIR/src/frontend"
    
    # 檢查 node_modules
    if [ ! -d "node_modules" ]; then
        echo "   安裝前端依賴..."
        npm install
    fi
    
    npm run dev &
    FRONTEND_PID=$!
    echo "   Frontend PID: $FRONTEND_PID"
    sleep 3
    echo "✅ 前端啟動成功"
}

# 顯示訪問信息
show_info() {
    echo ""
    echo "================================"
    echo "🎉 系統啟動完成!"
    echo ""
    echo "📍 訪問地址:"
    echo "   前端: http://localhost:$FRONTEND_PORT"
    echo "   後端: http://localhost:$BACKEND_PORT"
    echo "   API:  http://localhost:$BACKEND_PORT/health"
    echo ""
    echo "⏹️  按 Ctrl+C 停止所有服務"
    echo "================================"
}

# 清理函數
cleanup() {
    echo ""
    echo "🛑 停止服務..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ 已停止所有服務"
    exit 0
}

# 主流程
main() {
    check_dependencies
    kill_existing_processes
    start_backend
    start_frontend
    show_info
    
    # 捕獲退出信號
    trap cleanup SIGINT SIGTERM
    
    # 保持運行
    wait
}

main
