import { useState, useEffect, useCallback, useRef } from 'react';

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected';
type Message = {
  type: string;
  data: any;
};

interface WebSocketHook {
  sendMessage: (message: Message) => void;
  lastMessage: Message | null;
  connectionStatus: ConnectionStatus;
  reconnect: () => void;
}

export const useWebSocket = (url: string): WebSocketHook => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting');
  const [lastMessage, setLastMessage] = useState<Message | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const baseReconnectDelay = 1000;

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        setConnectionStatus('connected');
        reconnectAttempts.current = 0;
        if (reconnectTimeout.current) {
          clearTimeout(reconnectTimeout.current);
        }
      };

      ws.current.onclose = () => {
        setConnectionStatus('disconnected');
        
        // Implement exponential backoff for reconnection
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(
            baseReconnectDelay * Math.pow(2, reconnectAttempts.current),
            30000
          );
          reconnectTimeout.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setLastMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

    } catch (error) {
      console.error('WebSocket connection error:', error);
      setConnectionStatus('disconnected');
    }
  }, [url]);

  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttempts.current = 0;
    connect();
  }, [connect, disconnect]);

  const sendMessage = useCallback((message: Message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      throw new Error('WebSocket is not connected');
    }
  }, []);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Implement ping/pong to keep connection alive
  useEffect(() => {
    const pingInterval = setInterval(() => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // Send ping every 30 seconds

    return () => {
      clearInterval(pingInterval);
    };
  }, []);

  // Handle browser online/offline events
  useEffect(() => {
    const handleOnline = () => {
      if (connectionStatus === 'disconnected') {
        reconnect();
      }
    };

    const handleOffline = () => {
      setConnectionStatus('disconnected');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [connectionStatus, reconnect]);

  return {
    sendMessage,
    lastMessage,
    connectionStatus,
    reconnect,
  };
};
