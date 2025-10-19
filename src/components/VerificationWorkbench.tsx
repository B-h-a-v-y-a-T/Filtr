import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import useAletheia from "@/hooks/useAletheia";

type Result = {
  summary?: string;
  verdict?: string;
  evidence?: Array<{ source: string; confidence: number }>;
};

const VerificationWorkbench = () => {
  const { analyze, connect, disconnect, lastMessage, isConnected } = useAletheia();
  const [logs, setLogs] = useState<any[]>([]);
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [showVeracity, setShowVeracity] = useState(false);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  // Append websocket log messages to local logs array
  useEffect(() => {
    if (!lastMessage || typeof lastMessage !== 'object') return;
    if (lastMessage.type === 'log' && lastMessage.payload) {
      setLogs((prev) => [lastMessage.payload, ...prev].slice(0, 200));
    }
  }, [lastMessage]);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const type = url ? "url" : "text";
      const payload = url ? { url } : { text };
      const res = await analyze({ type, payload });
      setResult(res as Result);
    } catch (e) {
      setResult({ summary: "Request failed.", verdict: "Unknown", evidence: [] });
    } finally {
      setLoading(false);
    }
  };

  const threatBanner = useMemo(() => {
    if (!lastMessage || typeof lastMessage !== "object") return null;
    if (lastMessage.type !== "threat") return null;
    return (
      <div className="rounded-md border border-yellow-400 bg-yellow-50 text-yellow-900 px-4 py-2">
        <div className="text-sm font-medium">Live Threat Alert</div>
        <div className="text-xs opacity-80">{lastMessage.message} (Level {lastMessage.level})</div>
      </div>
    );
  }, [lastMessage]);

  return (
    <div className="space-y-4">
      {threatBanner}

      <Card>
        <CardHeader>
          <CardTitle>Verification Workbench</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Input
            placeholder="Paste a URL to verify (optional)"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <Textarea
            placeholder="Or paste text content to verify"
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={4}
          />
          <div className="flex items-center gap-2">
            <Button onClick={handleSubmit} disabled={loading} className="bg-gradient-primary">
              {loading ? "Analyzing..." : "Analyze"}
            </Button>
            <Button variant="outline" onClick={() => setShowVeracity(true)} disabled={!result}>
              View Veracity Chain
            </Button>
            <span className="text-xs text-muted-foreground ml-auto">
              WS: {isConnected ? "connected" : "disconnected"}
            </span>
          </div>
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Verification Result</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="text-sm"><span className="font-medium">Verdict:</span> {result.verdict}</div>
            <div className="text-sm whitespace-pre-wrap">
              <span className="font-medium">Summary:</span> {result.summary}
            </div>
            <div className="text-sm">
              <div className="font-medium mb-1">Evidence</div>
              <ul className="list-disc pl-5">
                {(result.evidence || []).map((e, i) => (
                  <li key={i} className="text-sm">
                    {e.source} — confidence {(e.confidence * 100).toFixed(0)}%
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}

      {showVeracity && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card border rounded-lg w-full max-w-3xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="font-semibold">Veracity Chain (D3 stub)</div>
              <Button size="sm" variant="outline" onClick={() => setShowVeracity(false)}>Close</Button>
            </div>
            <div className="h-64 rounded-md border flex items-center justify-center text-sm text-muted-foreground">
              D3 graph placeholder
            </div>
          </div>
        </div>
      )}

      {/* Live logs pane */}
      <Card>
        <CardHeader>
          <CardTitle>Live Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-48 overflow-y-auto font-mono text-xs bg-black text-white p-2 rounded">
            {logs.length === 0 && <div className="text-sm text-muted-foreground">No logs yet</div>}
            {logs.map((l, i) => (
              <div key={i} className="mb-1">
                <div className="text-[10px] opacity-70">{l.ts} • {l.level}</div>
                <div>{l.message} {l.payload ? <span className="text-[10px] opacity-60">{JSON.stringify(l.payload)}</span> : null}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VerificationWorkbench;


