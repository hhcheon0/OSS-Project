import React, { useState, useRef, useEffect } from "react";
import { MessageSquare, X, Send, Bot, Sparkles, Link2, HelpCircle } from "lucide-react";

export default function ChatWidget({ onOpenNoticeDetail }) {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      role: "assistant",
      text: "안녕하세요! Campus Notice AI 학사비서입니다. 수집된 공지사항에 대해 궁금한 점을 질문해 주세요! (예: '장학금 신청 자격이 어떻게 돼?', '졸업 자격 요건은?')",
      citations: []
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    setInput("");
    
    // 1. Add User Message
    const userMsg = {
      id: Date.now().toString(),
      role: "user",
      text: userText
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // API Port and Host check, fallback to 8080 or local URL
      const response = await fetch("http://127.0.0.1:8080/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: userText })
      });

      if (response.ok) {
        const data = await response.json();
        
        // 2. Add Assistant Message with citations
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            text: data.answer,
            citations: data.citations || []
          }
        ]);
      } else {
        throw new Error("API request failed");
      }
    } catch (err) {
      console.error("Chat API error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          text: "죄송합니다. 백엔드 AI 서비스에 일시적인 오류가 발생했거나 서버 연결이 차단되었습니다. 다시 시도해 주세요.",
          citations: []
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper to fetch full notice details and open the modal
  const handleCitationClick = async (citation) => {
    try {
      const res = await fetch(`http://127.0.0.1:8080/notices/${citation.id}`);
      if (res.ok) {
        const item = await res.json();
        // Map to client schema
        const mapped = {
          id: item.notice_id,
          title: item.title,
          category: item.category || "행정안내",
          date: item.created_at || new Date().toISOString().split('T')[0],
          views: item.view_count || 0,
          writer: item.author || "학사지원팀",
          content: item.content || "",
          summary: item.summary && item.summary.length > 0 ? item.summary : [
            "상세 정보는 원본 링크를 참고하세요."
          ],
          keyPoints: item.keyPoints || [],
          attachments: item.attachments || [],
          originalUrl: item.url
        };
        onOpenNoticeDetail(mapped);
      } else {
        // Fallback with minimal info
        onOpenNoticeDetail({
          id: citation.id,
          title: citation.title,
          category: citation.category || "행정안내",
          date: citation.date || "",
          writer: "학사지원팀",
          content: "원문을 보시려면 오른쪽 위 원본 링크 버튼을 눌러주세요.",
          summary: [citation.title],
          originalUrl: citation.url
        });
      }
    } catch (err) {
      console.error("Failed to fetch citation detail", err);
    }
  };

  // Helper function to render text with bold syntax and line breaks
  const formatMessageText = (text) => {
    return text.split("\n").map((line, lineIdx) => {
      // Regex search for markdown bold like **text**
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <p key={lineIdx} className={line.trim() === "" ? "h-2" : "min-h-[1rem] leading-relaxed mb-1.5"}>
          {parts.map((part, partIdx) => {
            if (part.startsWith("**") && part.endsWith("**")) {
              return (
                <strong key={partIdx} className="font-extrabold text-teal-800 dark:text-teal-400">
                  {part.slice(2, -2)}
                </strong>
              );
            }
            return part;
          })}
        </p>
      );
    });
  };

  return (
    <>
      {/* Floating Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 p-4 bg-teal-700 hover:bg-teal-650 text-white rounded-full shadow-2xl hover:scale-110 active:scale-95 transition-all duration-300 z-50 flex items-center justify-center cursor-pointer border border-teal-500/30 group"
      >
        {isOpen ? (
          <X size={24} className="transform rotate-0 transition-transform duration-300" />
        ) : (
          <div className="relative">
            <MessageSquare size={24} className="transform scale-100 transition-transform duration-300" />
            <span className="absolute -top-2.5 -right-2.5 flex h-4 w-4">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-4 w-4 bg-amber-500 text-[9px] text-teal-950 font-black items-center justify-center">
                AI
              </span>
            </span>
          </div>
        )}
      </button>

      {/* Chat Window Panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-[380px] sm:w-[420px] h-[550px] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden transition-all duration-300 z-50 animate-in fade-in slide-in-from-bottom-6">
          {/* Header */}
          <div className="px-4 py-4 bg-gradient-to-r from-teal-800 to-teal-950 text-white flex items-center justify-between shadow-md">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 bg-teal-700/60 rounded-lg">
                <Bot size={20} className="text-teal-200 animate-pulse" />
              </div>
              <div>
                <h3 className="font-extrabold text-sm tracking-wide flex items-center gap-1.5">
                  Campus Notice AI
                  <Sparkles size={12} className="text-amber-400 fill-amber-400" />
                </h3>
                <p className="text-[10px] text-teal-200 font-medium">대구대 통합 학사공지 Q&A</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 text-teal-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors cursor-pointer"
            >
              <X size={16} />
            </button>
          </div>

          {/* Messages Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 dark:bg-slate-950/40">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2.5 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
              >
                {/* Avatar */}
                {msg.role === "assistant" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-teal-850 dark:bg-teal-950 border border-teal-500/20 flex items-center justify-center text-teal-200 shadow-sm font-bold text-xs">
                    AI
                  </div>
                )}

                {/* Bubble Container */}
                <div className="flex flex-col max-w-[78%] gap-1.5">
                  {/* Bubble */}
                  <div
                    className={`px-3.5 py-2.5 rounded-2xl text-xs shadow-sm font-medium ${
                      msg.role === "user"
                        ? "bg-teal-700 text-white rounded-tr-none"
                        : "bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-850 dark:text-slate-100 rounded-tl-none"
                    }`}
                  >
                    {formatMessageText(msg.text)}
                  </div>

                  {/* Assistant Citations */}
                  {msg.role === "assistant" && msg.citations && msg.citations.length > 0 && (
                    <div className="mt-1 space-y-1 bg-white/70 dark:bg-slate-900/50 p-2 rounded-xl border border-slate-200 dark:border-slate-800">
                      <div className="text-[10px] font-bold text-teal-700 dark:text-teal-400 flex items-center gap-1 mb-1">
                        <Link2 size={10} />
                        <span>참고한 공지사항 ({msg.citations.length})</span>
                      </div>
                      <div className="flex flex-col gap-1">
                        {msg.citations.map((cit, cidx) => (
                          <button
                            key={cit.id}
                            onClick={() => handleCitationClick(cit)}
                            className="w-full text-left p-1.5 rounded bg-white dark:bg-slate-900 hover:bg-teal-50 dark:hover:bg-slate-800 border border-slate-250 dark:border-slate-800 text-[10px] text-slate-800 dark:text-slate-200 transition-colors flex items-center justify-between cursor-pointer group"
                          >
                            <span className="font-extrabold truncate max-w-[85%]">
                              [{cidx + 1}] {cit.title}
                            </span>
                            <span className="text-[9px] text-slate-400 dark:text-slate-500 group-hover:text-teal-700 font-bold shrink-0">
                              열기 &gt;
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex gap-2.5">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-teal-850 dark:bg-teal-950 border border-teal-500/20 flex items-center justify-center text-teal-200 shadow-sm font-bold text-xs">
                  AI
                </div>
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-850 dark:text-slate-100 px-3.5 py-2.5 rounded-2xl rounded-tl-none text-xs flex items-center gap-1.5 shadow-sm">
                  <span className="w-1.5 h-1.5 bg-teal-600 rounded-full animate-bounce"></span>
                  <span className="w-1.5 h-1.5 bg-teal-600 rounded-full animate-bounce delay-100"></span>
                  <span className="w-1.5 h-1.5 bg-teal-600 rounded-full animate-bounce delay-200"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Footer Input */}
          <form
            onSubmit={handleSend}
            className="p-3 border-t border-slate-200 dark:border-slate-850 bg-white dark:bg-slate-900 flex gap-2 items-center"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="학사 질문을 입력하세요..."
              className="flex-1 px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-950 text-xs border border-transparent focus:border-teal-500/50 text-slate-850 dark:text-slate-100 focus:outline-none placeholder-slate-400 dark:placeholder-slate-500"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="p-2 bg-teal-700 hover:bg-teal-650 disabled:bg-slate-200 dark:disabled:bg-slate-800 text-white disabled:text-slate-400 dark:disabled:text-slate-650 rounded-xl transition-all cursor-pointer shadow-sm shrink-0"
            >
              <Send size={14} />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
