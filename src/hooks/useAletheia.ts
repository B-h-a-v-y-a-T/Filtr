import { useCallback, useEffect, useRef, useState } from "react";

type AnalysisType = "url" | "text" | "image" | "video";

type AnalyzePayload = {
  type: AnalysisType;
  payload: Record<string, any>;
};

type AnalyzeResponse = {
  status?: string;
  summary?: string;
  verdict?: string;
  evidence?: Array<{ source: string; confidence: number }>;
};

export function useAletheia() {
  const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const wsUrl = import.meta.env.VITE_API_WS || "ws://localhost:8000/ws/threats";

  const [lastMessage, setLastMessage] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => setIsConnected(true);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      } catch {
        setLastMessage(event.data);
      }
    };
    ws.onclose = () => {
      setIsConnected(false);
      wsRef.current = null;
    };
    ws.onerror = () => {
      setIsConnected(false);
    };
    wsRef.current = ws;
  }, [wsUrl]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  const analyze = useCallback(
    async ({ type, payload }: AnalyzePayload): Promise<AnalyzeResponse> => {
      const res = await fetch(`${apiBase}/api/v1/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type, payload }),
      });
      if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
      }
      return (await res.json()) as AnalyzeResponse;
    },
    [apiBase]
  );

  return { analyze, connect, disconnect, isConnected, lastMessage };
}

export default useAletheia;


