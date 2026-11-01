import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export default function LiveStatusBadge() {
  const [liveData, setLiveData] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let ws = null;
    let timer = null;

    function connect() {
      try {
        const wsUrl = api.getWsUrl();
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          setConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setLiveData(data);
          } catch (e) {
            console.error('WebSocket parse error', e);
          }
        };

        ws.onclose = () => {
          setConnected(false);
          timer = setTimeout(connect, 5000);
        };

        ws.onerror = () => {
          setConnected(false);
        };
      } catch (err) {
        setConnected(false);
        timer = setTimeout(connect, 5000);
      }
    }

    connect();

    return () => {
      if (ws) ws.close();
      if (timer) clearTimeout(timer);
    };
  }, []);

  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 10,
      padding: '6px 12px',
      backgroundColor: '#f1f5f9',
      border: '1px solid #cbd5e1',
      borderRadius: 20,
      fontSize: 12,
      fontWeight: 600,
      color: '#334155'
    }}>
      <span style={{
        width: 8,
        height: 8,
        borderRadius: '50%',
        backgroundColor: connected ? '#10b981' : '#f59e0b',
        boxShadow: connected ? '0 0 6px #10b981' : 'none',
      }} />
      <span>{connected ? 'Simulated Live Stream Active' : 'Connecting to Stream...'}</span>
      {liveData && (
        <span style={{ color: '#0f766e', fontWeight: 700 }}>
          ({liveData.occupied_beds}/{liveData.total_beds} beds • {liveData.occupancy_rate}%)
        </span>
      )}
    </div>
  );
}
