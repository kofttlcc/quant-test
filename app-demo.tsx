import React, { useState, useEffect } from 'react';
import {
   LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, Legend, PieChart, Pie, Cell, ReferenceLine, ComposedChart, Scatter, LabelList, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import {
   Activity, Terminal, TrendingUp, TrendingDown, DollarSign,
   Settings, Layers, Code, Play, Pause, Save, BarChart2,
   ShieldAlert, Clock, MoreHorizontal, Layout, Search, Bell,
   Database, Server, RefreshCw, AlertTriangle, FileText, Cpu,
   Calendar, Filter, Sliders, Hash, Flame, BrainCircuit, Newspaper, CalendarClock, Zap, Globe, Gauge, BarChart4, ArrowRight, MousePointer2, Bot, Swords, Calculator, Percent, Table2, Sparkles, Loader2, MessageSquare, Key, Lock, Network, User
} from 'lucide-react';

// --- Local Gemini Proxy Configuration (Dynamic) ---

// 修改後的調用函數，接收動態配置
const callLocalGeminiProxy = async (prompt, apiUrl, apiKey) => {
   // 如果沒有設置 URL，使用默認提示
   const targetUrl = apiUrl || "http://localhost:8080/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent";

   const payload = {
      contents: [{ parts: [{ text: prompt }] }]
   };

   try {
      // 構建請求 URL，如果有 Key 則附加
      const fetchUrl = apiKey ? `${targetUrl}?key=${apiKey}` : targetUrl;

      const response = await fetch(fetchUrl, {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(`Connection failed: ${response.status}`);

      const data = await response.json();
      return data.candidates?.[0]?.content?.parts?.[0]?.text || "AI 返回數據格式異常。";
   } catch (error) {
      console.error("Local AI Error:", error);
      // 模擬數據用於演示，當連接失敗時
      return new Promise(resolve => {
         setTimeout(() => {
            resolve(`[系統提示] 無法連接至配置的 API 地址：${targetUrl}。\n請檢查左側「設置」中的 API 地址是否正確，以及您的本地代理是否已啟動。\n\n(這是一條模擬回覆，用於展示 UI 效果)`);
         }, 1500);
      });
   }
};

// --- 組件：AI 分析結果展示框 ---
const AIAnalysisCard = ({ title, content, isLoading, onGenerate, buttonText = "生成分析" }) => (
   <div className="bg-gradient-to-br from-indigo-50 to-white border border-indigo-100 rounded-lg p-4 shadow-sm mt-4">
      <div className="flex justify-between items-center mb-2">
         <h3 className="text-sm font-bold text-indigo-800 flex items-center">
            <Sparkles size={14} className="mr-2 text-indigo-500" /> {title}
         </h3>
         <button
            onClick={onGenerate}
            disabled={isLoading}
            className="text-xs flex items-center bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded transition-colors disabled:opacity-50 shadow-sm"
         >
            {isLoading ? <Loader2 size={12} className="mr-1 animate-spin" /> : <Bot size={12} className="mr-1" />}
            {isLoading ? "分析中..." : buttonText}
         </button>
      </div>
      {content && (
         <div className="text-xs text-gray-700 leading-relaxed font-mono bg-white/50 p-3 rounded border border-indigo-50 animate-in fade-in">
            {content.split('\n').map((line, i) => <p key={i} className="mb-1">{line}</p>)}
         </div>
      )}
   </div>
);

// --- 模擬數據生成 (Simulated Data) ---

const generateKLineData = (points = 60) => {
   let data = [];
   let price = 150;

   for (let i = 0; i < points; i++) {
      const move = (Math.random() - 0.48) * 3;
      const volatility = Math.random() * 2;
      const open = price;
      const close = price + move;
      const high = Math.max(open, close) + Math.random() * volatility;
      const low = Math.min(open, close) - Math.random() * volatility;
      price = close;
      let rsi = 50 + (Math.random() - 0.5) * 40;

      let signal = null;
      let signalPrice = null;
      if (rsi < 30 && Math.random() > 0.5) { signal = 'buy'; signalPrice = low * 0.98; }
      else if (rsi > 70 && Math.random() > 0.5) { signal = 'sell'; signalPrice = high * 1.02; }

      const isUp = close > open;
      data.push({
         time: `10-${i + 1}`, open: parseFloat(open.toFixed(2)), high: parseFloat(high.toFixed(2)),
         low: parseFloat(low.toFixed(2)), close: parseFloat(close.toFixed(2)),
         body: [Math.min(open, close), Math.max(open, close)], wick: [low, high],
         color: isUp ? '#10b981' : '#f43f5e', rsi: parseFloat(rsi.toFixed(2)),
         signal, signalPrice
      });
   }
   return data;
};

const initialArenaData = [
   { id: 1, name: 'DeepSeek-Quant-V3', type: 'AI (Transformer)', return: 18.5, sharpe: 2.4, drawdown: -4.2, status: 'active', rank: 1 },
   { id: 2, name: 'Classic-MeanRev', type: 'Trad (Stat Arb)', return: 12.1, sharpe: 1.8, drawdown: -2.1, status: 'active', rank: 3 },
   { id: 3, name: 'AlphaZero-RL', type: 'AI (Reinforcement)', return: 15.8, sharpe: 2.1, drawdown: -8.5, status: 'active', rank: 2 },
   { id: 4, name: 'Trend-Following-MA', type: 'Trad (Momentum)', return: 5.4, sharpe: 0.9, drawdown: -12.3, status: 'active', rank: 5 },
   { id: 5, name: 'LSTM-Predictor', type: 'AI (Deep Learning)', return: 8.9, sharpe: 1.2, drawdown: -6.7, status: 'training', rank: 4 },
];

const sensitivityData = [
   { wacc: '7.5%', g2: '$145', g25: '$158', g3: '$172' },
   { wacc: '8.0%', g2: '$132', g25: '$142', g3: '$155' },
   { wacc: '8.5%', g2: '$120', g25: '$128', g3: '$138' },
];

const generateDrawdownData = (points = 60) => {
   let data = [];
   let currentDrawdown = 0;
   for (let i = 0; i < points; i++) {
      const change = Math.random() > 0.6 ? 0.5 : -0.8;
      currentDrawdown = Math.min(0, currentDrawdown + change);
      if (Math.random() > 0.8) currentDrawdown = 0;
      data.push({ time: `10-${i + 1}`, drawdown: parseFloat(currentDrawdown.toFixed(2)) });
   }
   return data;
};

const monthlyReturns = [
   { month: 'Jan', ret: 2.5 }, { month: 'Feb', ret: -1.2 }, { month: 'Mar', ret: 3.8 }, { month: 'Apr', ret: 0.5 },
   { month: 'May', ret: -0.8 }, { month: 'Jun', ret: 1.2 }, { month: 'Jul', ret: 4.1 }, { month: 'Aug', ret: 2.2 },
   { month: 'Sep', ret: -2.5 }, { month: 'Oct', ret: 1.8 }, { month: 'Nov', ret: 3.0 }, { month: 'Dec', ret: 1.5 },
];

const distributionData = [
   { range: '<-3%', count: 2 }, { range: '-2%~-3%', count: 5 }, { range: '-1%~-2%', count: 12 },
   { range: '-0%~-1%', count: 25 }, { range: '0%~1%', count: 35 }, { range: '1%~2%', count: 20 },
   { range: '2%~3%', count: 8 }, { range: '>3%', count: 3 },
];

const dataFeeds = [
   { name: 'NYSE Tick Data (L1)', status: 'active', latency: '4ms', source: 'Direct' },
   { name: 'NASDAQ TotalView (L2)', status: 'active', latency: '12ms', source: 'Direct' },
   { name: 'Crypto Aggregate', status: 'warning', latency: '145ms', source: 'REST API' },
   { name: 'Alt-Data: Sentiment', status: 'active', latency: '800ms', source: 'Webhook' },
   { name: 'Futures Options Chain', status: 'inactive', latency: '-', source: 'Socket' },
];

// --- 組件部分 (Components) ---

const SignalMarker = (props: any) => {
   const { cx, cy, payload } = props;
   if (!payload.signal) return null;
   const isBuy = payload.signal === 'buy';
   const color = isBuy ? '#10b981' : '#f43f5e';
   return (
      <g transform={`translate(${cx},${cy})`}>
         <polygon points={isBuy ? "-6,6 0,-6 6,6" : "-6,-6 0,6 6,-6"} fill={color} stroke="none" />
         <text x={0} y={isBuy ? 20 : -15} textAnchor="middle" fill={color} fontSize={10} fontWeight="bold">{isBuy ? 'B' : 'S'}</text>
      </g>
   );
};

const MetricCard = ({ title, value, subValue, isPositive, icon: Icon }) => (
   <div className="bg-white border border-gray-200 p-4 rounded-lg flex flex-col justify-between hover:border-gray-300 transition-colors shadow-sm">
      <div className="flex justify-between items-start mb-2">
         <span className="text-gray-500 text-xs uppercase font-semibold tracking-wider">{title}</span>
         <Icon size={16} className="text-gray-400" />
      </div>
      <div>
         <div className="text-2xl font-mono text-gray-900 font-bold">{value}</div>
         {subValue && (
            <div className={`text-xs font-mono mt-1 flex items-center ${isPositive ? 'text-emerald-600' : 'text-rose-600'}`}>
               {isPositive ? <TrendingUp size={12} className="mr-1" /> : <TrendingDown size={12} className="mr-1" />}
               {subValue}
            </div>
         )}
      </div>
   </div>
);

const IconButton = ({ icon: Icon, label, active, onClick }) => (
   <div className="group relative flex items-center justify-center w-full">
      <button
         onClick={onClick}
         className={`p-3 rounded-xl mb-3 transition-all duration-200 ${active ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30' : 'text-gray-400 hover:bg-gray-100 hover:text-gray-900'}`}
      >
         <Icon size={20} />
      </button>
      <div className="absolute left-14 bg-gray-800 text-white text-[10px] px-2 py-1 rounded border border-gray-700 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
         {label}
      </div>
   </div>
);

const Badge = ({ children, type }) => {
   const styles = {
      INFO: 'bg-blue-100 text-blue-700 border-blue-200',
      WARN: 'bg-amber-100 text-amber-700 border-amber-200',
      EXEC: 'bg-emerald-100 text-emerald-700 border-emerald-200',
      ERROR: 'bg-rose-100 text-rose-700 border-rose-200',
      active: 'bg-emerald-50 text-emerald-600 border-emerald-200',
      inactive: 'bg-gray-100 text-gray-500 border-gray-200',
      warning: 'bg-amber-50 text-amber-600 border-amber-200',
      training: 'bg-indigo-50 text-indigo-600 border-indigo-200 animate-pulse',
   };
   return (
      <span className={`px-2 py-0.5 rounded text-[10px] font-mono border flex items-center w-fit ${styles[type] || styles.INFO}`}>
         {type === 'active' && <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></div>}
         {type === 'training' && <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mr-1.5 animate-bounce"></div>}
         {type === 'warning' && <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mr-1.5"></div>}
         {children || (type === 'active' ? '運行中' : type === 'inactive' ? '離線' : type === 'training' ? '訓練中' : '異常')}
      </span>
   );
};

// 宏觀大盤儀表板組件
const MacroOverviewPanel = ({ apiConfig }) => {
   const [aiInsight, setAiInsight] = useState("");
   const [isGenerating, setIsGenerating] = useState(false);

   const handleGenerateInsight = async () => {
      setIsGenerating(true);
      const prompt = "Act as a Wall Street Chief Strategist. Analyze the following macro data: Fear & Greed Index 68 (Greed), US 10Y Yield 4.25% (Inverted Yield Curve -35bps), VIX 14.8, Headline: 'Fed pause signal'. Provide a concise market regime assessment and one actionable trading advice in Traditional Chinese.";
      const result = await callLocalGeminiProxy(prompt, apiConfig.apiAddress, apiConfig.apiKey);
      setAiInsight(result);
      setIsGenerating(false);
   };

   return (
      <div className="col-span-12 mb-4 bg-white rounded-xl border border-gray-200 overflow-hidden flex flex-col flex-shrink-0 shadow-sm">
         <div className="flex items-center h-9 bg-gray-50 border-b border-gray-200 px-3 flex-shrink-0">
            <div className="flex items-center mr-4 flex-shrink-0">
               <Globe className="mr-2 text-indigo-600" size={14} />
               <span className="text-xs font-bold text-gray-700">宏觀態勢感知</span>
            </div>
            <div className="flex-1 overflow-hidden relative h-full flex items-center">
               <div className="flex items-center text-[10px] text-gray-600 whitespace-nowrap animate-marquee space-x-8">
                  <span className="flex items-center"><span className="text-yellow-600 mr-1 font-bold">BREAKING:</span> 聯準會會議紀要暗示暫停加息，那指期貨夜盤大漲 1.2%</span>
                  <span className="flex items-center"><span className="text-indigo-600 mr-1 font-bold">INFO:</span> 10年期美債收益率回落至 4.25% 下方，創兩週新低</span>
               </div>
               <div className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-gray-50 to-transparent"></div>
               <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-gray-50 to-transparent"></div>
            </div>
            <div className="flex items-center space-x-2 pl-4 border-l border-gray-200 ml-2">
               <div className="flex items-center space-x-1 bg-emerald-100 px-2 py-0.5 rounded">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
                  <span className="text-[10px] text-emerald-700 font-mono font-bold">LIVE</span>
               </div>
            </div>
         </div>

         <div className="p-4 grid grid-cols-1 md:grid-cols-4 gap-4 bg-white">
            <div className="bg-white border border-gray-200 rounded-lg p-3 flex flex-col justify-between h-[150px] relative overflow-hidden group hover:border-gray-300 transition-colors shadow-sm">
               <div className="flex justify-between items-start z-10">
                  <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider flex items-center"><Gauge size={12} className="mr-1" /> 市場情緒</span>
                  <span className="text-[10px] bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded border border-gray-200">Contra</span>
               </div>
               <div className="flex flex-col items-center justify-center z-10">
                  <span className="text-4xl font-mono font-bold text-emerald-600">68</span>
                  <span className="text-xs font-bold text-emerald-700 mt-1">貪婪 (Greed)</span>
               </div>
               <div className="mt-auto z-10">
                  <div className="w-full h-1 bg-gray-200 rounded-full overflow-hidden">
                     <div className="h-full bg-gradient-to-r from-rose-500 via-amber-400 to-emerald-500 w-[68%]"></div>
                  </div>
                  <div className="flex justify-between text-[8px] text-gray-400 mt-1">
                     <span>極恐</span>
                     <span>中性</span>
                     <span>極貪</span>
                  </div>
               </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-3 flex flex-col justify-between h-[150px] group hover:border-gray-300 transition-colors shadow-sm">
               <div className="flex justify-between items-start">
                  <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider flex items-center"><TrendingDown size={12} className="mr-1" /> 利率與波動</span>
               </div>
               <div className="flex-1 flex flex-col justify-center space-y-3">
                  <div className="flex justify-between items-center border-b border-gray-100 pb-2">
                     <div>
                        <div className="text-[9px] text-gray-400 uppercase">US 10Y Yield</div>
                        <div className="text-lg font-mono text-gray-800 leading-none">4.25%</div>
                     </div>
                     <div className="text-right">
                        <div className="text-[9px] text-gray-400 uppercase">10Y-2Y Spread</div>
                        <div className="text-sm font-mono text-rose-600 font-bold">-35 bps</div>
                     </div>
                  </div>
                  <div className="flex justify-between items-center">
                     <div>
                        <div className="text-[9px] text-gray-400 uppercase">VIX Index</div>
                        <div className="text-lg font-mono text-emerald-600 leading-none">14.8</div>
                     </div>
                     <div className="text-right">
                        <div className="text-[9px] text-gray-400 uppercase">Term Structure</div>
                        <div className="text-[10px] text-emerald-700 bg-emerald-50 px-1 rounded border border-emerald-100">Contango</div>
                     </div>
                  </div>
               </div>
            </div>

            <div className="bg-gradient-to-br from-indigo-50 to-white border border-indigo-100 rounded-lg p-3 flex flex-col justify-between h-[150px] relative overflow-hidden shadow-md group">
               <div className="flex justify-between items-start z-10">
                  <span className="text-[10px] text-indigo-700 font-bold uppercase tracking-wider flex items-center"><CalendarClock size={12} className="mr-1" /> 下一個超級事件</span>
                  <span className="text-[9px] bg-indigo-600 text-white px-1.5 py-0.5 rounded font-bold animate-pulse">HIGH IMPACT</span>
               </div>
               <div className="z-10 mt-2">
                  <h3 className="text-lg font-bold text-gray-900 leading-tight flex items-center group-hover:text-indigo-700 transition-colors">
                     FOMC 利率決議 <ArrowRight size={14} className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </h3>
                  <p className="text-[10px] text-indigo-500 mt-0.5">聯邦公開市場委員會</p>
               </div>
               <div className="grid grid-cols-2 gap-2 mt-auto z-10">
                  <div className="bg-white/60 rounded p-1.5 backdrop-blur-sm border border-indigo-200">
                     <div className="text-[8px] text-indigo-500 uppercase">倒數計時</div>
                     <div className="text-sm font-mono font-bold text-indigo-900">12<span className="text-[9px] font-normal text-gray-500 ml-0.5">D</span> 04<span className="text-[9px] font-normal text-gray-500 ml-0.5">H</span></div>
                  </div>
                  <div className="bg-white/60 rounded p-1.5 backdrop-blur-sm border border-indigo-200">
                     <div className="text-[8px] text-indigo-500 uppercase">市場預期</div>
                     <div className="text-sm font-bold text-indigo-900">暫停升息</div>
                  </div>
               </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-3 flex flex-col justify-between h-[150px] group hover:border-gray-300 transition-colors shadow-sm">
               <div className="flex justify-between items-start">
                  <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider flex items-center"><BarChart4 size={12} className="mr-1" /> 市場廣度 (Breadth)</span>
                  <span className="text-[10px] text-emerald-600 font-bold flex items-center">RISK ON <Zap size={8} className="ml-1 fill-current" /></span>
               </div>
               <div className="flex-1 flex flex-col justify-center mt-2 space-y-2">
                  <div>
                     <div className="flex justify-between text-[9px] text-gray-500 mb-1">
                        <span>上漲家數 (Adv)</span>
                        <span>下跌家數 (Dec)</span>
                     </div>
                     <div className="flex w-full h-2 rounded-full overflow-hidden bg-gray-100">
                        <div className="w-[65%] bg-emerald-500"></div>
                        <div className="w-[35%] bg-rose-500"></div>
                     </div>
                     <div className="text-[9px] text-right mt-0.5 text-emerald-600 font-mono">Ratio: 1.85</div>
                  </div>
                  <div className="grid grid-cols-2 gap-1 text-[9px]">
                     <div className="flex justify-between items-center bg-emerald-50 px-1.5 py-1 rounded border border-emerald-100">
                        <span className="text-emerald-700">XLK (科技)</span>
                        <span className="font-mono text-emerald-600 font-bold">+1.2%</span>
                     </div>
                     <div className="flex justify-between items-center bg-rose-50 px-1.5 py-1 rounded border border-rose-100">
                        <span className="text-rose-700">XLU (公用)</span>
                        <span className="font-mono text-rose-600 font-bold">-0.4%</span>
                     </div>
                  </div>
               </div>
            </div>
         </div>

         {/* AI Analysis Section */}
         <div className="px-4 pb-4">
            <AIAnalysisCard
               title="AI 首席策略師觀點 (AI Macro Insight)"
               content={aiInsight}
               isLoading={isGenerating}
               onGenerate={handleGenerateInsight}
               buttonText="生成 AI 宏觀解讀"
            />
         </div>
      </div>
   );
};

export default function QuantDashboard() {
   const [activeTab, setActiveTab] = useState('dashboard');
   const [chartData, setChartData] = useState(generateKLineData());
   const [drawdownData, setDrawdownData] = useState(generateDrawdownData());
   const [arenaData, setArenaData] = useState(initialArenaData);
   const [isRunning, setIsRunning] = useState(false);
   const [valuationModel, setValuationModel] = useState('DCF');

   // Settings Configuration State
   const [config, setConfig] = useState({
      apiAddress: "http://localhost:8080/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent",
      apiKey: "", // Default empty
      systemPort: "3000",
      username: "admin",
      password: ""
   });

   // AI States for other tabs
   const [arenaAnalysis, setArenaAnalysis] = useState("");
   const [isArenaAnalyzing, setIsArenaAnalyzing] = useState(false);
   const [valuationReport, setValuationReport] = useState("");
   const [isValuating, setIsValuating] = useState(false);

   // 模擬 K 線實時更新
   useEffect(() => {
      if (!isRunning) return;
      const interval = setInterval(() => {
         // K線更新邏輯
      }, 1000);
      return () => clearInterval(interval);
   }, [isRunning]);

   // 模擬 AI 競技場自動 PK
   useEffect(() => {
      const pkInterval = setInterval(() => {
         setArenaData(prevData => {
            const newData = prevData.map(model => {
               const change = (Math.random() - 0.45) * 0.5;
               const newReturn = parseFloat((model.return + change).toFixed(1));
               const newSharpe = parseFloat((model.sharpe + (change / 10)).toFixed(2));
               return { ...model, return: newReturn, sharpe: newSharpe };
            });
            return newData.sort((a, b) => b.return - a.return).map((m, i) => ({ ...m, rank: i + 1 }));
         });
      }, 3000);
      return () => clearInterval(pkInterval);
   }, []);

   const handleGenerateArenaAnalysis = async () => {
      setIsArenaAnalyzing(true);
      const topModel = arenaData[0];
      const prompt = `Analyze the current AI Alpha Arena leaderboard. The top model is ${topModel.name} (Type: ${topModel.type}) with a return of ${topModel.return}% and Sharpe Ratio of ${topModel.sharpe}. Compare it with traditional models. Provide a commentary on why AI models might be outperforming in the current volatility. Respond in Traditional Chinese.`;
      const result = await callLocalGeminiProxy(prompt, config.apiAddress, config.apiKey);
      setArenaAnalysis(result);
      setIsArenaAnalyzing(false);
   };

   const handleGenerateValuationReport = async () => {
      setIsValuating(true);
      const prompt = `Generate a professional stock valuation report for Apple Inc. (AAPL). Current Price: $178.35. Intrinsic Value (${valuationModel}): $205.10. Margin of Safety: +15.2%. Sensitivity shows high resilience to WACC changes. Provide an investment recommendation (Buy/Hold/Sell) and rationale based on value investing principles. Respond in Traditional Chinese.`;
      const result = await callLocalGeminiProxy(prompt, config.apiAddress, config.apiKey);
      setValuationReport(result);
      setIsValuating(false);
   };

   // --- Views ---

   // New: Settings Panel
   const renderSettings = () => (
      <div className="h-full flex flex-col gap-6 animate-in fade-in duration-500 overflow-y-auto max-w-4xl mx-auto w-full pt-4">
         <div className="mb-2">
            <h2 className="text-xl font-bold text-gray-800 flex items-center">
               <Settings className="mr-3 text-gray-600" /> 系統設置 (Configuration)
            </h2>
            <p className="text-sm text-gray-500 mt-1">管理 API 連接、系統端口及帳戶安全</p>
         </div>

         {/* 1. AI Connection */}
         <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-gray-800 flex items-center mb-4 border-b border-gray-100 pb-2">
               <Bot className="mr-2 text-indigo-500" size={16} /> AI 模型連接配置 (Gemini Local Proxy)
            </h3>
            <div className="space-y-4">
               <div>
                  <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">API 地址 (URL)</label>
                  <div className="relative">
                     <Network className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={14} />
                     <input
                        type="text"
                        value={config.apiAddress}
                        onChange={(e) => setConfig({ ...config, apiAddress: e.target.value })}
                        className="w-full bg-gray-50 border border-gray-200 rounded-lg py-2 pl-9 pr-4 text-xs focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-200 text-gray-700 font-mono"
                        placeholder="http://localhost:8080/..."
                     />
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1">請輸入本地代理的完整端點地址 (Endpoint URL)</p>
               </div>
               <div>
                  <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">API Key (Optional)</label>
                  <div className="relative">
                     <Key className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={14} />
                     <input
                        type="password"
                        value={config.apiKey}
                        onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
                        className="w-full bg-gray-50 border border-gray-200 rounded-lg py-2 pl-9 pr-4 text-xs focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-200 text-gray-700 font-mono"
                        placeholder="本地代理通常無需 Key，若有請輸入"
                     />
                  </div>
               </div>
            </div>
         </div>

         {/* 2. System Config */}
         <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-gray-800 flex items-center mb-4 border-b border-gray-100 pb-2">
               <Server className="mr-2 text-emerald-500" size={16} /> 系統運行參數
            </h3>
            <div className="grid grid-cols-2 gap-4">
               <div>
                  <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">系統端口 (Port)</label>
                  <input
                     type="number"
                     value={config.systemPort}
                     onChange={(e) => setConfig({ ...config, systemPort: e.target.value })}
                     className="w-full bg-gray-50 border border-gray-200 rounded-lg py-2 px-3 text-xs focus:outline-none focus:border-indigo-500 text-gray-700 font-mono"
                  />
               </div>
               <div>
                  <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">最大並發請求數</label>
                  <input
                     type="number"
                     defaultValue={50}
                     className="w-full bg-gray-50 border border-gray-200 rounded-lg py-2 px-3 text-xs focus:outline-none focus:border-indigo-500 text-gray-700 font-mono"
                  />
               </div>
            </div>
         </div>

         {/* 3. Account Config */}
         <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-gray-800 flex items-center mb-4 border-b border-gray-100 pb-2">
               <User className="mr-2 text-rose-500" size={16} /> 帳戶安全 (Admin)
            </h3>
            <div className="space-y-4">
               <div>
                  <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">管理員帳號</label>
                  <input
                     type="text"
                     value={config.username}
                     onChange={(e) => setConfig({ ...config, username: e.target.value })}
                     className="w-full bg-gray-50 border border-gray-200 rounded-lg py-2 px-3 text-xs focus:outline-none focus:border-indigo-500 text-gray-700"
                  />
               </div>
               <div>
                  <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">新密碼</label>
                  <div className="relative">
                     <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={14} />
                     <input
                        type="password"
                        value={config.password}
                        onChange={(e) => setConfig({ ...config, password: e.target.value })}
                        className="w-full bg-gray-50 border border-gray-200 rounded-lg py-2 pl-9 pr-4 text-xs focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-200 text-gray-700"
                        placeholder="••••••••"
                     />
                  </div>
               </div>
            </div>
         </div>

         {/* Save Button */}
         <div className="flex justify-end pb-8">
            <button
               onClick={() => alert("配置已保存並生效！(模擬)")}
               className="flex items-center bg-gray-900 hover:bg-black text-white px-6 py-2 rounded-lg text-sm font-bold transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
               <Save size={16} className="mr-2" /> 保存配置
            </button>
         </div>
      </div>
   );

   const renderDashboard = () => (
      <div className="grid grid-cols-12 gap-4 w-full animate-in fade-in duration-500 pb-20">

         <MacroOverviewPanel apiConfig={config} />

         <div className="col-span-12 grid grid-cols-4 gap-4 mb-2">
            <MetricCard title="累積收益 (Cum. Return)" value="+24.5%" subValue="vs SPY +12.1%" isPositive={true} icon={DollarSign} />
            <MetricCard title="年化夏普比率 (Sharpe)" value="2.84" subValue="排名前 5%" isPositive={true} icon={ShieldAlert} />
            <MetricCard title="盈虧比 (Profit Factor)" value="1.65" subValue="穩健" isPositive={true} icon={TrendingUp} />
            <MetricCard title="最大回撤 (Max Drawdown)" value="-8.2%" subValue="恢復期: 14天" isPositive={false} icon={Activity} />
         </div>

         {/* Main Chart Area (Line Chart + RSI) - 優化：使用線型圖適應長週期回測 */}
         <div className="col-span-12 lg:col-span-8 bg-white border border-gray-200 rounded-lg p-4 flex flex-col h-[600px] shadow-sm">
            <div className="flex justify-between items-center mb-2">
               <div className="flex items-center space-x-4">
                  <h2 className="text-sm font-semibold text-gray-700">模型回測: 價格走勢與 RSI 指標</h2>
                  <div className="flex space-x-1 bg-gray-100 rounded p-0.5 border border-gray-200">
                     {['M1', 'M5', 'M30', '1H', '1D'].map(t => (
                        <button key={t} className={`px-2 py-0.5 text-[10px] rounded ${t === '1D' ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-500 hover:text-gray-900'}`}>{t}</button>
                     ))}
                  </div>
               </div>
               <div className="flex items-center space-x-4 text-xs">
                  <div className="flex items-center space-x-2">
                     <span className="w-2 h-2 rounded-full bg-emerald-500"></span> <span className="text-gray-500">買入信號</span>
                     <span className="w-2 h-2 rounded-full bg-rose-500 ml-2"></span> <span className="text-gray-500">賣出信號</span>
                  </div>
               </div>
            </div>

            {/* Top: 價格走勢線型圖 (替代 K 線圖以適應長週期) */}
            <div className="flex-[3] min-h-0 relative mb-1">
               <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData} syncId="quantChart" margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                     <defs>
                        <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                           <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                           <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                        </linearGradient>
                     </defs>
                     <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                     <XAxis dataKey="time" stroke="#94a3b8" fontSize={10} tick={false} axisLine={false} />
                     <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} domain={['auto', 'auto']} orientation="right" />
                     <RechartsTooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', fontSize: '12px', color: '#1e293b' }} itemStyle={{ color: '#475569' }} cursor={{ stroke: '#94a3b8', strokeWidth: 1, strokeDasharray: '3 3' }} />
                     {/* 價格線型圖 */}
                     <Area type="monotone" dataKey="close" stroke="#6366f1" strokeWidth={2} fill="url(#priceGradient)" dot={false} name="收盤價" />
                     {/* 買賣信號標記 - 保留 */}
                     <Scatter dataKey="signalPrice" shape={<SignalMarker />} />
                  </ComposedChart>
               </ResponsiveContainer>
               <div className="absolute top-2 left-2 text-[10px] text-gray-400 font-mono">收盤價: <span className="text-indigo-600 font-bold">{chartData.length > 0 ? chartData[chartData.length - 1]?.close?.toFixed(2) : '--'}</span></div>
            </div>

            {/* Bottom: RSI Chart */}
            <div className="flex-1 min-h-0 border-t border-gray-100 pt-2">
               <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} syncId="quantChart" margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
                     <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                     <XAxis dataKey="time" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                     <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} domain={[0, 100]} ticks={[30, 70]} orientation="right" />
                     <RechartsTooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', fontSize: '12px' }} cursor={{ stroke: '#94a3b8', strokeWidth: 1, strokeDasharray: '3 3' }} wrapperStyle={{ display: 'none' }} />
                     <ReferenceLine y={70} stroke="#f43f5e" strokeDasharray="3 3" strokeOpacity={0.5} />
                     <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" strokeOpacity={0.5} />
                     <Line type="monotone" dataKey="rsi" stroke="#c084fc" strokeWidth={1.5} dot={false} activeDot={{ r: 4, fill: '#fff' }} />
                  </LineChart>
               </ResponsiveContainer>
               <div className="absolute bottom-8 left-2 text-[10px] text-purple-500 font-mono">RSI (14)</div>
            </div>
         </div>

         <div className="col-span-12 lg:col-span-4 flex flex-col gap-4">
            {/* Backtest Configuration */}
            <div className="bg-white border border-gray-200 rounded-lg p-4 flex-1 shadow-sm">
               <div className="flex justify-between items-center mb-4">
                  <h2 className="text-sm font-semibold text-gray-700 flex items-center">
                     <Sliders size={14} className="mr-2 text-indigo-600" /> 回測參數配置
                  </h2>
               </div>

               <div className="space-y-3 mb-4">
                  <div className="grid grid-cols-2 gap-2">
                     <div>
                        <label className="text-[10px] text-gray-500 uppercase font-semibold">開始日期</label>
                        <div className="bg-gray-50 border border-gray-200 rounded px-2 py-1.5 text-xs text-gray-600 flex items-center justify-between mt-1">
                           2022-01-01 <Calendar size={12} className="text-gray-400" />
                        </div>
                     </div>
                     <div>
                        <label className="text-[10px] text-gray-500 uppercase font-semibold">結束日期</label>
                        <div className="bg-gray-50 border border-gray-200 rounded px-2 py-1.5 text-xs text-gray-600 flex items-center justify-between mt-1">
                           2023-10-31 <Calendar size={12} className="text-gray-400" />
                        </div>
                     </div>
                  </div>
                  <div>
                     <label className="text-[10px] text-gray-500 uppercase font-semibold">初始資金</label>
                     <div className="bg-gray-50 border border-gray-200 rounded px-2 py-1.5 text-xs text-gray-600 flex items-center mt-1">
                        <span className="text-gray-400 mr-1">$</span> 1,000,000
                     </div>
                  </div>
                  <div>
                     <label className="text-[10px] text-gray-500 uppercase font-semibold">標的資產 (Universe)</label>
                     <div className="bg-gray-50 border border-gray-200 rounded px-2 py-1.5 text-xs text-gray-600 flex items-center mt-1">
                        SPY, QQQ, IWM, TLT
                     </div>
                  </div>
               </div>

               <button className="w-full flex items-center justify-center py-2 px-4 rounded text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white transition-all shadow-lg shadow-indigo-500/20">
                  <Play size={14} className="mr-2" /> 開始回測 (Run Backtest)
               </button>
            </div>

            {/* Key Stats */}
            <div className="bg-white border border-gray-200 rounded-lg p-4 flex-1 flex flex-col min-h-0 shadow-sm">
               <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                  <Hash size={14} className="mr-2 text-gray-400" /> 核心統計指標
               </h2>
               <div className="grid grid-cols-2 gap-y-3 gap-x-2 flex-1">
                  <div className="flex flex-col justify-center p-2 bg-gray-50 rounded border border-gray-100">
                     <span className="text-[10px] text-gray-500">勝率 (Win Rate)</span>
                     <span className="text-lg font-mono font-bold text-emerald-600">58.4%</span>
                  </div>
                  <div className="flex flex-col justify-center p-2 bg-gray-50 rounded border border-gray-100">
                     <span className="text-[10px] text-gray-500">凱利公式 (Kelly)</span>
                     <span className="text-lg font-mono font-bold text-indigo-600">12.5%</span>
                  </div>
                  <div className="flex flex-col justify-center p-2 bg-gray-50 rounded border border-gray-100">
                     <span className="text-[10px] text-gray-500">平均盈利 (Avg Win)</span>
                     <span className="text-sm font-mono text-gray-700">+$240.50</span>
                  </div>
                  <div className="flex flex-col justify-center p-2 bg-gray-50 rounded border border-gray-100">
                     <span className="text-[10px] text-gray-500">平均虧損 (Avg Loss)</span>
                     <span className="text-sm font-mono text-gray-700">-$115.20</span>
                  </div>
                  <div className="flex flex-col justify-center p-2 bg-gray-50 rounded border border-gray-100 col-span-2">
                     <span className="text-[10px] text-gray-500">總交易次數 (Total Trades)</span>
                     <span className="text-sm font-mono text-gray-700">1,245 筆</span>
                  </div>
               </div>
            </div>
         </div>

         <div className="col-span-12 lg:col-span-8 bg-white border border-gray-200 rounded-lg p-4 overflow-hidden flex flex-col shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center">
               <TrendingDown size={14} className="mr-2 text-rose-500" /> 回撤分析 (Underwater Plot)
               <span className="ml-2 text-xs text-gray-400 font-normal">可視化歷史最大虧損幅度與恢復時間</span>
            </h2>
            <div className="flex-1 min-h-[180px]">
               <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={drawdownData}>
                     <defs>
                        <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
                           <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                           <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                        </linearGradient>
                     </defs>
                     <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                     <XAxis dataKey="time" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                     <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                     <RechartsTooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', fontSize: '12px', color: '#1e293b' }} itemStyle={{ color: '#f43f5e' }} formatter={(value) => [`${value}%`, 'Drawdown']} />
                     <Area type="step" dataKey="drawdown" stroke="#f43f5e" strokeWidth={2} fill="url(#colorDrawdown)" />
                  </AreaChart>
               </ResponsiveContainer>
            </div>
         </div>

         <div className="col-span-12 lg:col-span-4 bg-white border border-gray-200 rounded-lg p-4 flex flex-col shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center">
               <BarChart2 size={14} className="mr-2 text-indigo-600" /> 收益分佈直方圖
            </h2>
            <div className="flex-1 min-h-[180px]">
               <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={distributionData} layout="vertical" margin={{ left: 10 }}>
                     <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
                     <XAxis type="number" stroke="#94a3b8" fontSize={10} hide />
                     <YAxis dataKey="range" type="category" stroke="#64748b" fontSize={10} width={60} tickLine={false} axisLine={false} />
                     <RechartsTooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0' }} />
                     <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} barSize={16}>
                        {distributionData.map((entry, index) => (
                           <Cell key={`cell-${index}`} fill={index === 3 || index === 4 ? '#6366f1' : '#cbd5e1'} />
                        ))}
                     </Bar>
                  </BarChart>
               </ResponsiveContainer>
            </div>
            <div className="text-center text-[10px] text-gray-500 mt-2">
               偏度 (Skew): <span className="text-emerald-600 font-bold">+0.42</span> (正偏態)
            </div>
         </div>
      </div>
   );

   // 2. AI 模型競技場 (AI Model Arena) - Integrated Gemini
   const renderAIArena = () => (
      <div className="h-full flex flex-col gap-6 animate-in fade-in duration-500">
         {/* Top Header Area */}
         <div className="flex justify-between items-end">
            <div>
               <h2 className="text-xl font-bold text-gray-800 flex items-center">
                  <Swords className="mr-3 text-rose-500" /> AI 模型競技場 (Alpha Arena)
               </h2>
               <p className="text-xs text-gray-500 mt-1">實時監控 AI 與傳統計量模型的績效對決 (Live Tournament)</p>
            </div>
            <div className="flex space-x-2">
               <div className="px-3 py-1 bg-white border border-gray-200 rounded text-xs text-gray-600 shadow-sm">
                  本賽季: <span className="text-gray-900 font-bold">Season 4</span>
               </div>
               <div className="px-3 py-1 bg-indigo-50 border border-indigo-200 rounded text-xs text-indigo-600 animate-pulse">
                  PK 進行中...
               </div>
            </div>
         </div>

         {/* AI Commentary Section */}
         <AIAnalysisCard
            title="AI 賽事解說 (Tournament Commentary)"
            content={arenaAnalysis}
            isLoading={isArenaAnalyzing}
            onGenerate={handleGenerateArenaAnalysis}
            buttonText="生成戰況分析"
         />

         {/* Leaderboard Table */}
         <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
            <div className="grid grid-cols-12 bg-gray-50 p-3 text-xs font-bold text-gray-500 uppercase tracking-wider border-b border-gray-200">
               <div className="col-span-1 text-center">排名</div>
               <div className="col-span-3">模型名稱 (Model)</div>
               <div className="col-span-2">類型 (Type)</div>
               <div className="col-span-2 text-right">年化回報 (Ann. Ret)</div>
               <div className="col-span-2 text-right">夏普比率 (Sharpe)</div>
               <div className="col-span-2 text-center">狀態 (Status)</div>
            </div>
            <div className="divide-y divide-gray-100">
               {arenaData.map((model) => (
                  <div key={model.id} className={`grid grid-cols-12 p-4 items-center hover:bg-gray-50 transition-all duration-300 ${model.rank === 1 ? 'bg-indigo-50/50' : ''}`}>
                     <div className="col-span-1 flex justify-center">
                        {model.rank === 1 ? (
                           <div className="w-6 h-6 rounded-full bg-yellow-400 text-white flex items-center justify-center font-bold text-xs shadow-md shadow-yellow-200">1</div>
                        ) : model.rank === 2 ? (
                           <div className="w-6 h-6 rounded-full bg-gray-400 text-white flex items-center justify-center font-bold text-xs">2</div>
                        ) : model.rank === 3 ? (
                           <div className="w-6 h-6 rounded-full bg-amber-700 text-white flex items-center justify-center font-bold text-xs">3</div>
                        ) : (
                           <span className="text-gray-400 font-mono">{model.rank}</span>
                        )}
                     </div>
                     <div className="col-span-3">
                        <div className="font-bold text-gray-700 flex items-center">
                           {model.type.includes('AI') ? <Bot size={14} className="mr-2 text-indigo-500" /> : <Activity size={14} className="mr-2 text-gray-400" />}
                           {model.name}
                        </div>
                     </div>
                     <div className="col-span-2">
                        <span className={`text-[10px] px-2 py-0.5 rounded border ${model.type.includes('AI') ? 'border-indigo-200 text-indigo-600 bg-indigo-50' : 'border-gray-200 text-gray-500 bg-gray-100'}`}>
                           {model.type}
                        </span>
                     </div>
                     <div className="col-span-2 text-right">
                        <span className="font-mono text-emerald-600 font-bold">+{model.return.toFixed(1)}%</span>
                        <div className="w-full bg-gray-100 h-1 mt-1 rounded-full overflow-hidden">
                           <div className="bg-emerald-500 h-full transition-all duration-1000" style={{ width: `${Math.min(100, model.return * 3)}%` }}></div>
                        </div>
                     </div>
                     <div className="col-span-2 text-right font-mono text-gray-600">{model.sharpe.toFixed(2)}</div>
                     <div className="col-span-2 flex justify-center">
                        <Badge type={model.status}></Badge>
                     </div>
                  </div>
               ))}
            </div>
         </div>

         {/* Performance Detail Cards */}
         <div className="grid grid-cols-3 gap-6">
            <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
               <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center"><Swords size={14} className="mr-2" /> 頭部模型對決</h3>
               <div className="flex items-center justify-between text-xs mt-4">
                  <div className="text-center">
                     <div className="text-indigo-600 font-bold mb-1">DeepSeek-V3</div>
                     <div className="text-2xl font-mono text-gray-900">18.5%</div>
                  </div>
                  <div className="text-gray-400 font-bold">VS</div>
                  <div className="text-center">
                     <div className="text-gray-500 font-bold mb-1">AlphaZero</div>
                     <div className="text-2xl font-mono text-gray-500">15.8%</div>
                  </div>
               </div>
               <div className="mt-4 text-[10px] text-center text-gray-400">勝率預測: DeepSeek 領先 12%</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
               <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center"><ShieldAlert size={14} className="mr-2" /> 風險控制MVP</h3>
               <div className="mt-2">
                  <div className="flex justify-between text-xs mb-1">
                     <span className="text-gray-500">Classic-MeanRev</span>
                     <span className="text-emerald-600">-2.1% DD</span>
                  </div>
                  <div className="w-full bg-gray-100 h-1.5 rounded-full">
                     <div className="bg-emerald-500 h-full w-[10%]"></div>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-2">傳統模型在極端行情下展現了極佳的抗跌性。</p>
               </div>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4 flex flex-col justify-center items-center text-center shadow-sm">
               <Bot size={32} className="text-indigo-500 mb-2" />
               <div className="text-sm font-bold text-gray-700">訓練新模型?</div>
               <button className="mt-2 px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs rounded transition-colors shadow-sm">
                  進入訓練場
               </button>
            </div>
         </div>
      </div>
   );

   // 3. 股票內在價值估值 (Intrinsic Valuation) - Integrated Gemini
   const renderValuation = () => (
      <div className="h-full flex flex-col gap-6 animate-in fade-in duration-500 overflow-y-auto">
         <div className="flex justify-between items-center mb-2">
            <h2 className="text-xl font-bold text-gray-800 flex items-center">
               <Calculator className="mr-3 text-emerald-600" /> 真實內在價值估值 (Intrinsic Value)
            </h2>
            <div className="flex bg-white rounded-lg p-1 border border-gray-200 shadow-sm">
               {['DCF', 'Graham', 'DDM'].map(m => (
                  <button
                     key={m}
                     onClick={() => setValuationModel(m)}
                     className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-all ${valuationModel === m ? 'bg-emerald-600 text-white shadow-md' : 'text-gray-500 hover:text-gray-900'}`}
                  >
                     {m} 模型
                  </button>
               ))}
            </div>
         </div>

         {/* Main Valuation Gauge/Chart */}
         <div className="grid grid-cols-12 gap-6">
            <div className="col-span-8 bg-white border border-gray-200 rounded-xl p-6 relative overflow-hidden shadow-sm">
               <div className="absolute top-0 right-0 p-4 opacity-5">
                  <DollarSign size={120} className="text-emerald-500" />
               </div>

               <div className="flex justify-between items-end mb-8">
                  <div>
                     <h3 className="text-3xl font-bold text-gray-900 font-mono">AAPL <span className="text-lg text-gray-400 font-sans">Apple Inc.</span></h3>
                     <div className="flex items-center mt-2 space-x-4">
                        <div>
                           <div className="text-[10px] text-gray-400 uppercase">當前市價</div>
                           <div className="text-xl font-mono text-gray-700">$178.35</div>
                        </div>
                        <div className="h-8 w-px bg-gray-200"></div>
                        <div>
                           <div className="text-[10px] text-gray-400 uppercase">內在價值 ({valuationModel})</div>
                           <div className="text-xl font-mono text-emerald-600 font-bold">$205.10</div>
                        </div>
                     </div>
                  </div>
                  <div className="text-right">
                     <div className="text-xs text-gray-400 mb-1">安全邊際 (Margin of Safety)</div>
                     <div className="text-2xl font-bold text-emerald-600">+15.2%</div>
                     <div className="text-[10px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded mt-1 inline-block border border-emerald-200">UNDERVALUED (低估)</div>
                  </div>
               </div>

               {/* Visual Bar */}
               <div className="relative h-12 bg-gray-50 rounded-full border border-gray-200 mt-6">
                  {/* Zones */}
                  <div className="absolute left-0 top-0 bottom-0 w-[40%] bg-emerald-100 border-r border-gray-200 first-letter:rounded-l-full"></div> {/* Undervalued Zone */}
                  <div className="absolute left-[40%] top-0 bottom-0 w-[20%] bg-amber-50 border-r border-gray-200"></div> {/* Fair Zone */}
                  <div className="absolute right-0 top-0 bottom-0 w-[40%] bg-rose-50 rounded-r-full"></div> {/* Overvalued Zone */}

                  {/* Current Price Marker */}
                  <div className="absolute top-0 bottom-0 w-1 bg-gray-800 shadow-md z-10" style={{ left: '35%' }}>
                     <div className="absolute -top-7 left-1/2 transform -translate-x-1/2 text-[10px] font-bold text-white bg-gray-800 px-1.5 py-0.5 rounded">
                        現價 $178
                     </div>
                  </div>

                  {/* Fair Value Marker */}
                  <div className="absolute top-0 bottom-0 w-1 bg-emerald-500 shadow-md z-10" style={{ left: '50%' }}>
                     <div className="absolute -bottom-7 left-1/2 transform -translate-x-1/2 text-[10px] font-bold text-emerald-600 bg-emerald-100 border border-emerald-200 px-1.5 py-0.5 rounded">
                        估值 $205
                     </div>
                  </div>
               </div>
               <div className="flex justify-between text-[10px] text-gray-400 mt-2 px-1">
                  <span>$100 (極度低估)</span>
                  <span>$200 (合理價值)</span>
                  <span>$300 (極度高估)</span>
               </div>
            </div>

            <div className="col-span-4 space-y-4">
               <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                  <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center"><Table2 size={14} className="mr-2" /> 敏感度分析 (Sensitivity)</h4>
                  <p className="text-[10px] text-gray-500 mb-2">假設終值增長率 (g) 與 WACC 變化對股價的影響：</p>
                  <table className="w-full text-xs text-center">
                     <thead>
                        <tr className="text-gray-500">
                           <th className="pb-2">WACC \ g</th>
                           <th className="pb-2">2.0%</th>
                           <th className="pb-2 text-indigo-600">2.5%</th>
                           <th className="pb-2">3.0%</th>
                        </tr>
                     </thead>
                     <tbody className="divide-y divide-gray-100 text-gray-700">
                        {sensitivityData.map((row, i) => (
                           <tr key={i}>
                              <td className="py-2 text-gray-500 font-mono">{row.wacc}</td>
                              <td className="py-2 font-mono">{row.g2}</td>
                              <td className={`py-2 font-mono font-bold ${i === 1 ? 'text-emerald-700 border border-emerald-200 rounded bg-emerald-50' : ''}`}>{row.g25}</td>
                              <td className="py-2 font-mono">{row.g3}</td>
                           </tr>
                        ))}
                     </tbody>
                  </table>
               </div>

               <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center"><FileText size={14} className="mr-2" /> 模型邏輯</h4>
                  <div className="text-[10px] text-gray-500 space-y-1 font-mono bg-gray-50 p-2 rounded border border-gray-200">
                     <p>Model: 2-Stage DCF</p>
                     <p>Growth (5y): 12.0%</p>
                     <p>Terminal Growth: 2.5%</p>
                     <p>Discount Rate (WACC): 8.0%</p>
                     <p className="text-emerald-600 pt-1"> Formula: Σ(FCF / (1+r)^t) + TV</p>
                  </div>
               </div>
            </div>

            <div className="col-span-12">
               <AIAnalysisCard
                  title="智能估值報告 (Smart Valuation Report)"
                  content={valuationReport}
                  isLoading={isValuating}
                  onGenerate={handleGenerateValuationReport}
                  buttonText="生成投資評級"
               />
            </div>
         </div>
      </div>
   );

   // 4. 數據層 (Data Layer)
   const renderDataLayer = () => (
      <div className="h-full bg-white border border-gray-200 rounded-lg p-6 animate-in fade-in duration-500 shadow-sm">
         <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-gray-800 flex items-center">
               <Database className="mr-3 text-indigo-600" /> 數據源管理 (Data Feeds)
            </h2>
            <button className="flex items-center text-xs bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded transition-colors shadow-sm">
               <RefreshCw size={14} className="mr-2" /> 刷新狀態
            </button>
         </div>

         <div className="grid grid-cols-1 gap-4">
            {dataFeeds.map((feed, idx) => (
               <div key={idx} className="bg-gray-50 border border-gray-200 rounded p-4 flex items-center justify-between hover:border-gray-300 transition-colors">
                  <div className="flex items-center space-x-4">
                     <div className={`p-2 rounded-lg ${feed.status === 'active' ? 'bg-emerald-100 text-emerald-600' : feed.status === 'inactive' ? 'bg-gray-200 text-gray-500' : 'bg-amber-100 text-amber-600'}`}>
                        <Server size={20} />
                     </div>
                     <div>
                        <div className="text-sm font-bold text-gray-700">{feed.name}</div>
                        <div className="text-xs text-gray-500 font-mono">Source: {feed.source}</div>
                     </div>
                  </div>
                  <div className="flex items-center space-x-8">
                     <div className="text-right">
                        <div className="text-[10px] text-gray-400 uppercase">Latency</div>
                        <div className="text-sm font-mono text-gray-600">{feed.latency}</div>
                     </div>
                     <Badge type={feed.status}></Badge>
                     <button className="text-gray-400 hover:text-gray-900"><Settings size={16} /></button>
                  </div>
               </div>
            ))}
         </div>

         <div className="mt-8 p-4 border border-rose-200 bg-rose-50 rounded flex items-start gap-3">
            <AlertTriangle className="text-rose-600 flex-shrink-0" size={20} />
            <div>
               <h4 className="text-sm font-bold text-rose-700">異常檢測報告</h4>
               <p className="text-xs text-rose-600 mt-1">Crypto Aggregate Feed 延遲超過 100ms 閾值。自動切換至備用線路中。</p>
            </div>
         </div>
      </div>
   );

   return (
      <div className="flex h-screen bg-gray-50 text-gray-900 font-sans overflow-hidden selection:bg-indigo-100 selection:text-indigo-900">

         {/* Sidebar */}
         <div className="w-18 bg-white border-r border-gray-200 flex flex-col items-center py-6 z-20 px-2 shadow-sm">
            <div className="mb-8 p-2.5 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-200">
               <Activity size={26} className="text-white" />
            </div>
            <nav className="flex-1 w-full flex flex-col items-center space-y-1">
               <IconButton icon={Layout} label="總覽儀表板" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
               <IconButton icon={Swords} label="AI 模型競技場" active={activeTab === 'aiarena'} onClick={() => setActiveTab('aiarena')} />
               <IconButton icon={Calculator} label="內在價值估值" active={activeTab === 'valuation'} onClick={() => setActiveTab('valuation')} />
               <IconButton icon={Layers} label="數據源管理" active={activeTab === 'data'} onClick={() => setActiveTab('data')} />
            </nav>
            <div className="mb-4 w-full flex justify-center">
               <IconButton icon={Settings} label="系統設置" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
            </div>
         </div>

         {/* Main Content */}
         <div className="flex-1 flex flex-col min-w-0">

            {/* Header */}
            <header className="h-14 bg-white/80 backdrop-blur-md border-b border-gray-200 flex items-center justify-between px-6 z-10">
               <div className="flex items-center space-x-4">
                  <h1 className="text-lg font-bold tracking-tight text-gray-900">量化分析系統 <span className="text-gray-500 font-normal">V1</span></h1>
                  <div className="h-4 w-px bg-gray-300 mx-2"></div>
                  <div className="flex items-center space-x-2 text-xs font-mono text-gray-500">
                     <span className="flex items-center"><span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>系統在線</span>
                     <span className="px-2">核心: <span className="text-indigo-600 font-semibold">DeepSeek-V3</span></span>
                  </div>
               </div>

               <div className="flex items-center space-x-4">
                  <div className="relative group">
                     <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-indigo-600 transition-colors" />
                     <input
                        type="text"
                        placeholder="指令 / 搜尋..."
                        className="bg-gray-50 border border-gray-200 rounded-full py-1.5 pl-9 pr-4 text-xs focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-200 text-gray-700 w-64 transition-all shadow-sm"
                     />
                     <div className="absolute right-2 top-1.5 text-[10px] text-gray-400 border border-gray-200 rounded px-1.5 bg-gray-50">⌘K</div>
                  </div>
                  <button className="relative p-2 text-gray-400 hover:text-gray-900 transition-colors">
                     <Bell size={18} />
                     <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full border border-white"></span>
                  </button>
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-xs font-bold border border-white shadow-md text-white">Q</div>
               </div>
            </header>

            {/* Dynamic Content Area */}
            <main className="flex-1 p-4 overflow-y-auto custom-scrollbar relative">
               {activeTab === 'dashboard' && renderDashboard()}
               {activeTab === 'aiarena' && renderAIArena()}
               {activeTab === 'valuation' && renderValuation()}
               {activeTab === 'data' && renderDataLayer()}
               {activeTab === 'settings' && renderSettings()}
            </main>
         </div>

         <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #f9fafb;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
        @keyframes marquee {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-100%); }
        }
        .animate-marquee {
          animation: marquee 30s linear infinite;
        }
        .animate-in {
          animation: fadeIn 0.3s ease-out forwards;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
      </div>
   );
}