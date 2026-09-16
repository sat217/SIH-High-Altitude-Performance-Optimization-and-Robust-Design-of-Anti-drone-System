import React from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { useSentinelStore } from './store/useSentinelStore';
import { Shield, Thermometer, Eye, Crosshair, BarChart3 } from 'lucide-react';

function App() {
  useWebSocket();
  const { isConnected, frame, mode, detections } = useSentinelStore();

  // Mock tactical metrics (replace with real data later)
  const metrics = {
    precision: 0.92,
    recall: 0.88,
    mAP50: 0.85,
    fps: 30
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-mono selection:bg-green-500/30 flex flex-col">
      {/* Top Bar */}
      <header className="h-16 bg-black/80 border-b border-slate-800 flex items-center justify-between px-6 backdrop-blur-sm sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <Shield className="w-6 h-6 text-blue-500" />
          <h1 className="text-xl font-bold tracking-widest text-blue-100">SKY SENTINEL</h1>
          <span className="text-[10px] bg-blue-900/50 text-blue-300 px-2 py-0.5 rounded border border-blue-700/50">GCS v1.0</span>
        </div>
        
        <div className={`flex items-center gap-2 ${isConnected ? 'text-green-400' : 'text-red-500'}`}>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          <span className="text-sm font-bold">{isConnected ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
      </header>

      <main className="p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 overflow-hidden">
        
        {/* Main Video Feed (Left Side - 8 cols) */}
        <div className="lg:col-span-8 flex flex-col gap-4 h-full">
          <div className="relative flex-1 bg-black rounded-lg overflow-hidden border border-slate-800 shadow-2xl group min-h-[400px]">
            {frame ? (
              <img src={frame} alt="Live Feed" className="w-full h-full object-contain" />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center bg-slate-900">
                <Crosshair className="w-12 h-12 text-slate-700 animate-spin mb-4" style={{ animationDuration: '3s' }} />
                <p className="text-slate-500 text-sm tracking-wider">WAITING FOR VIDEO STREAM...</p>
              </div>
            )}
            
            {/* HUD Overlays */}
            <div className="absolute top-4 left-4 bg-black/60 backdrop-blur px-3 py-1 rounded border border-slate-700/50">
              <span className="text-xs text-slate-400">CAM_01 • </span>
              <span className={`text-xs font-bold ${mode === 'thermal' ? 'text-orange-400' : 'text-green-400'}`}>
                {mode.toUpperCase()} MODE
              </span>
            </div>

            <div className="absolute bottom-4 left-4 right-4 flex justify-between items-end pointer-events-none">
              <div className="bg-black/60 backdrop-blur px-3 py-2 rounded border border-slate-700/50">
                <p className="text-[10px] text-slate-400 uppercase">Objects Detected</p>
                <p className="text-2xl font-bold text-yellow-400">{detections.length}</p>
              </div>
              
              {mode === 'thermal' && (
                <div className="flex items-center gap-2 bg-orange-900/80 px-3 py-1 rounded border border-orange-700/50">
                  <Thermometer className="w-4 h-4 text-orange-400" />
                  <span className="text-xs text-orange-200 font-bold">AUTO-SWITCH ACTIVE</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar (Right Side - 4 cols) */}
        <div className="lg:col-span-4 flex flex-col gap-4 overflow-y-auto pr-1 h-full">
          
          {/* System Status Card */}
          <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4 shrink-0">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <Eye className="w-3 h-3" /> System Telemetry
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-500">Detection Engine</span>
                <span className="text-green-400 text-xs bg-green-900/20 px-2 py-0.5 rounded">YOLOv8n</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-500">Stream Protocol</span>
                <span className="text-blue-400 text-xs bg-blue-900/20 px-2 py-0.5 rounded">WebSocket</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-500">Thermal Threshold</span>
                <span className="text-orange-400 text-xs bg-orange-900/20 px-2 py-0.5 rounded">AUTO</span>
              </div>
            </div>
          </div>

          {/* Tactical Metrics Card */}
          <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4 shrink-0">
            <h3 className="text-xs font-bold text-purple-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <BarChart3 className="w-3 h-3" /> Tactical Metrics
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-purple-900/20 p-2 rounded border border-purple-700/30">
                <p className="text-[10px] text-purple-400 uppercase">Precision</p>
                <p className="text-lg font-bold text-purple-200">{(metrics.precision * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-purple-900/20 p-2 rounded border border-purple-700/30">
                <p className="text-[10px] text-purple-400 uppercase">Recall</p>
                <p className="text-lg font-bold text-purple-200">{(metrics.recall * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-purple-900/20 p-2 rounded border border-purple-700/30">
                <p className="text-[10px] text-purple-400 uppercase">mAP@50</p>
                <p className="text-lg font-bold text-purple-200">{(metrics.mAP50 * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-purple-900/20 p-2 rounded border border-purple-700/30">
                <p className="text-[10px] text-purple-400 uppercase">FPS</p>
                <p className="text-lg font-bold text-purple-200">{metrics.fps}</p>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;