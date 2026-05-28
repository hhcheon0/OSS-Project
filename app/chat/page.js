"use client";

import { useEffect, useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
const QUICK_QUESTIONS = [
  "이번 주 신청 가능한 장학금 공지 있어?",
  "수강신청 정정 기간 관련 공지 알려줘",
  "졸업요건 관련 최신 공지 찾아줘",
  "예비군 훈련 일정 공지 있어?"
];

const isCasualChat = (text) => {
  const q = (text || "").trim().toLowerCase();
  if (!q) return false;
  const keywords = ["안녕", "하이", "hello", "hi", "반가", "고마", "감사", "잘가", "bye", "누구", "이름", "뭐해", "help"];
  return (q.length <= 30 && keywords.some((k) => q.includes(k))) || q.length <= 6;
};

export default function ChatPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState([]);
  const [lastMatches, setLastMatches] = useState([]);
  const [noticeCount, setNoticeCount] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/health`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data && typeof data.notice_count === "number") {
          setNoticeCount(data.notice_count);
        }
      })
      .catch(() => setNoticeCount(null));
  }, []);

  const getSourceLabel = (source) => {
    if (source === "db") return "공지 DB 기반 답변";
    if (source === "llm") return "LLM 일반 답변";
    if (source === "chat") return "일반 대화";
    if (source === "empty_db") return "공지 미수집 안내";
    if (source === "rag") return "RAG 근거 기반 답변";
    if (source === "rag_fallback") return "RAG 검색 요약(폴백)";
    return "응답";
  };

  const askQuestion = async (rawText) => {
    const userText = rawText.trim();
    if (!userText) return;

    setLoading(true);
    setError("");
    setQuery("");
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    try {
      const primaryUrl = isCasualChat(userText)
        ? `${API_BASE_URL}/chat?q=${encodeURIComponent(userText)}&use_db_first=true`
        : `${API_BASE_URL}/chat/rag?q=${encodeURIComponent(userText)}&top_k=5`;

      const ragUrl = `${API_BASE_URL}/chat/rag?q=${encodeURIComponent(userText)}&top_k=5`;
      let res = await fetch(ragUrl);

      // /chat/rag 실패 시 기존 /chat으로 자동 폴백
      if (!res.ok) {
        const fallbackUrl = primaryUrl;
        const fallbackRes = await fetch(fallbackUrl);
        if (fallbackRes.ok) {
          res = fallbackRes;
        }
      }

      if (!res.ok) {
        let message = `요청 실패 (${res.status})`;
        try {
          const errBody = await res.json();
          if (errBody?.detail) {
            message = `${message}: ${errBody.detail}`;
          }
        } catch (_ignored) {}
        throw new Error(message);
      }
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer || "응답이 없습니다.",
          source: data.source,
        },
      ]);
      setLastMatches(Array.isArray(data.matches) ? data.matches : []);
      if (typeof data.notice_count === "number") {
        setNoticeCount(data.notice_count);
      }
    } catch (err) {
      setError(err.message || "요청 중 오류가 발생했습니다.");
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "오류가 발생했습니다. 잠시 후 다시 시도해 주세요.", source: "error" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const submit = async (e) => {
    e.preventDefault();
    await askQuestion(query);
  };

  return (
    <main className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-2xl font-bold">Campus Notice AI 챗봇</h1>
        <a href="/" className="text-sm text-teal-700 hover:underline">
          메인으로 돌아가기
        </a>
      </div>
      <p className="text-sm text-slate-500 mb-4">
        수집된 공지 데이터 기반으로 질의합니다. 답변 아래에 관련 공지 출처를 확인할 수 있습니다.
      </p>

      {noticeCount === 0 && (
        <div className="mb-4 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          <strong>공지 DB가 비어 있습니다.</strong> 메인에서 새로고침(크롤링)을 실행하거나 백엔드에서{" "}
          <code className="text-xs bg-amber-100 px-1 rounded">POST /crawl</code> 후 다시 질문해 주세요.
          인사·일반 질문은 그동안 답변 가능합니다.
        </div>
      )}
      {noticeCount !== null && noticeCount > 0 && (
        <p className="text-xs text-slate-500 mb-4">현재 DB 공지 {noticeCount}건 기준으로 검색합니다.</p>
      )}

      <div className="rounded-xl border border-slate-200 p-4 mb-4 bg-white shadow-sm">
        {messages.length === 0 ? (
          <p className="text-sm text-slate-500">질문을 입력하면 대화가 시작됩니다.</p>
        ) : (
          <div className="space-y-3 h-[460px] overflow-y-auto pr-1">
            {messages.map((m, idx) => (
              <div key={idx} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] rounded-xl px-3 py-2 text-sm whitespace-pre-wrap ${
                    m.role === "user"
                      ? "bg-teal-700 text-white"
                      : "bg-slate-100 text-slate-800 border border-slate-200"
                  }`}
                >
                  {m.role === "assistant" && m.source && m.source !== "error" && (
                    <div className="text-[11px] text-slate-500 mb-1">{getSourceLabel(m.source)}</div>
                  )}
                  {m.text}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {QUICK_QUESTIONS.map((question) => (
          <button
            key={question}
            type="button"
            disabled={loading}
            onClick={() => askQuestion(question)}
            className="px-3 py-1.5 rounded-full text-xs border border-slate-300 bg-slate-50 hover:bg-slate-100 text-slate-700 disabled:opacity-60"
          >
            {question}
          </button>
        ))}
      </div>

      <form onSubmit={submit} className="flex gap-2 mb-6">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="예: 이번 주 신청 가능한 장학금 공지 있어?"
          rows={3}
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm resize-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-teal-700 text-white px-5 py-2 text-sm font-semibold disabled:opacity-60 self-end"
        >
          {loading ? "질의 중..." : "질문하기"}
        </button>
      </form>

      {error && (
        <div className="mb-4 rounded border border-rose-300 bg-rose-50 text-rose-700 px-3 py-2 text-sm">
          {error}
        </div>
      )}

      {lastMatches.length > 0 && (
        <section className="space-y-4">
          <div className="rounded border border-slate-200 p-4">
            <h2 className="font-semibold mb-3">관련 공지 출처 (최근 답변 기준)</h2>
            <ul className="space-y-3">
              {lastMatches.map((m) => (
                <li key={m.notice_id} className="text-sm">
                  <div className="font-medium">{m.title}</div>
                  {m.snippet && <div className="text-slate-600 mt-1">{m.snippet}</div>}
                  {m.url && (
                    <a
                      href={m.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-teal-700 underline text-xs"
                    >
                      원문 링크
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}
    </main>
  );
}
