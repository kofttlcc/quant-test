#!/bin/bash
# ============================================
# Skill-Antigravity 一鍵啟動腳本
# ============================================
#
# 用法: ./start.sh
#
# 功能:
#   1. 啟動後端 Express 服務器 (port 3001)
#   2. 啟動前端 Vite 開發服務器 (port 5173)
#   3. 自動打開瀏覽器
#

set -e

# 顏色定義
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 目錄設置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$SCRIPT_DIR/server"
CLIENT_DIR="$SCRIPT_DIR/client"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Skill-Antigravity 一鍵啟動${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 檢查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  未找到 Node.js，請先安裝${NC}"
    exit 1
fi

# 檢查並安裝依賴
install_deps_if_needed() {
    local dir=$1
    local name=$2
    if [ ! -d "$dir/node_modules" ]; then
        echo -e "${YELLOW}📦 正在安裝 $name 依賴...${NC}"
        cd "$dir" && npm install
    fi
}

# 安裝依賴
install_deps_if_needed "$SERVER_DIR" "Server"
install_deps_if_needed "$CLIENT_DIR" "Client"

# 清理函數
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 正在關閉服務...${NC}"
    kill $SERVER_PID 2>/dev/null || true
    kill $CLIENT_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# 啟動後端
echo -e "${GREEN}🚀 啟動後端服務器 (port 3001)...${NC}"
cd "$SERVER_DIR"
npm run dev &
SERVER_PID=$!

# 等待後端啟動
sleep 2

# 啟動前端
echo -e "${GREEN}🚀 啟動前端開發服務器 (port 5173)...${NC}"
cd "$CLIENT_DIR"
npm run dev &
CLIENT_PID=$!

# 等待前端啟動
sleep 3

# 打開瀏覽器
echo ""
echo -e "${GREEN}✅ 服務已啟動！${NC}"
echo ""
echo -e "   ${CYAN}前端${NC}: http://localhost:5173"
echo -e "   ${CYAN}後端${NC}: http://localhost:3001"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服務${NC}"
echo ""

# 嘗試打開瀏覽器
if command -v open &> /dev/null; then
    open http://localhost:5173
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173
fi

# 等待進程
wait $SERVER_PID $CLIENT_PID
