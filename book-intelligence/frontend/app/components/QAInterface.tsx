"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { askQuestion, ChatHistoryItem, fetchHistory, QAResponse } from "@/lib/api";

type ChatMessage = QAResponse & { id: string };

export function QAInterface() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [history, setHistory] = useState<ChatHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        const items = await fetchHistory();
        setHistory(items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not load chat history");
      } finally {
        setLoadingHistory(false);
      }
    };
    run();
  }, []);

  const handleAsk = async () => {
    if (!question.trim() || loading) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await askQuestion(question.trim());
      setMessages((prev) => [
        ...prev,
        { ...response, id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}` },
      ]);
      setQuestion("");

      const updatedHistory = await fetchHistory();
      setHistory(updatedHistory);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Question request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <section className="space-y-4 lg:col-span-2">
        <Card className="space-y-3 p-4">
          <h1 className="font-[var(--font-heading)] text-2xl font-black text-gold">Book Q&A</h1>
          <p className="text-sm text-ink/70">
            Ask natural language questions and get answers grounded in scraped book content.
          </p>
          <Textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Example: Which books discuss personal growth and resilience?"
            className="min-h-28"
          />
          <Button onClick={handleAsk} disabled={loading || !question.trim()}>
            {loading ? "Generating answer..." : "Send"}
          </Button>
          {error ? <p className="text-sm text-rose-300">{error}</p> : null}
        </Card>

        <div className="space-y-3">
          {messages.length === 0 ? (
            <Card className="text-sm text-ink/70">Your new answers will appear here.</Card>
          ) : (
            messages.map((message) => (
              <Card key={message.id} className="space-y-3 p-4">
                <div className="rounded-lg bg-gold/10 p-3">
                  <p className="text-xs uppercase tracking-wide text-gold-soft">Question</p>
                  <p className="mt-1 text-sm">{message.question}</p>
                </div>
                <div className="rounded-lg bg-white/5 p-3">
                  <p className="text-xs uppercase tracking-wide text-gold-soft">Answer</p>
                  <p className="mt-1 whitespace-pre-wrap text-sm leading-relaxed">{message.answer}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {message.sources.map((source, idx) => (
                    <Link key={`${source.book_id}-${idx}`} href={`/books/${source.book_id}`}>
                      <Badge className="cursor-pointer hover:bg-gold/25">{source.book_title}</Badge>
                    </Link>
                  ))}
                </div>
              </Card>
            ))
          )}
        </div>
      </section>

      <aside>
        <Card className="h-full p-4">
          <h2 className="mb-3 text-lg font-semibold text-gold">Chat History</h2>
          <div className="space-y-2">
            {loadingHistory ? (
              <p className="text-sm text-ink/60">Loading history...</p>
            ) : history.length === 0 ? (
              <p className="text-sm text-ink/60">No previous questions yet.</p>
            ) : (
              history.map((entry) => (
                <div key={entry.id} className="rounded-lg border border-white/10 bg-white/5 p-3">
                  <p className="line-clamp-2 text-sm font-medium">{entry.question}</p>
                  <p className="mt-1 text-xs text-ink/60">
                    {new Date(entry.created_at).toLocaleString()}
                  </p>
                </div>
              ))
            )}
          </div>
        </Card>
      </aside>
    </div>
  );
}
