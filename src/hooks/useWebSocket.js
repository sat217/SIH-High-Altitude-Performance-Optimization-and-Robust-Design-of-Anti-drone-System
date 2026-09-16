import { useEffect, useRef } from 'react';
import { useSentinelStore } from '../store/useSentinelStore';

export const useWebSocket = (url = 'ws://localhost:8000/ws/stream') => {
  const wsRef = useRef(null);
  const { setConnectionStatus, updateFrame } = useSentinelStore();

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ Connected to SKY SENTINEL Backend');
        setConnectionStatus(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'frame') {
            updateFrame(
              `data:image/jpeg;base64,${data.frame}`, 
              data.detections, 
              data.mode
            );
          }
        } catch (error) {
          console.error('Error parsing WS message:', error);
        }
      };

      ws.onclose = () => {
        console.log('🔌 Disconnected. Reconnecting in 3s...');
        setConnectionStatus(false);
        setTimeout(connect, 3000);
      };

      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        ws.close();
      };
    };

    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url, setConnectionStatus, updateFrame]);
};