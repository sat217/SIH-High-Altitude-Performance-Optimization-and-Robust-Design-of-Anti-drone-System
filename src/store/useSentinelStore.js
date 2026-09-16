import { create } from 'zustand';

export const useSentinelStore = create((set) => ({
  isConnected: false,
  frame: null,
  detections: [],
  mode: 'normal',
  alerts: [],
  
  setConnectionStatus: (status) => set({ isConnected: status }),
  
  updateFrame: (frameData, detections, mode) => set({ 
    frame: frameData, 
    detections, 
    mode 
  }),
  
  // ✅ FIXED: Append new alert, cap at 20, auto-remove after 60s
  addAlert: (newAlert) => set((state) => {
    const now = Date.now() / 1000;
    const freshAlerts = state.alerts.filter(a => (now - a.timestamp) < 60);
    return { 
      alerts: [newAlert, ...freshAlerts].slice(0, 20)
    };
  }),
  
  clearAlerts: () => set({ alerts: [] })
}));