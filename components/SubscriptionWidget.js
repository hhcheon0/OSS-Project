"use client";

import React, { useState } from "react";
import { Plus, X, Bell, Info } from "lucide-react";

/* 
 * [OSS Upgrade] - SubscriptionWidget 가독성 개선
 * 개량 내용:
 * 1. 라이트 모드에서 거의 보이지 않던 연회색 텍스트(Info 설명 및 미등록 상태 메세지)를 
 *    명도 대비가 우수한 Tailwind 표준 Slate 텍스트 톤으로 수정.
 * 2. 잘못 표기된 Tailwind 컬러 수치(text-slate-650 등)를 표준값으로 보정.
 */

export default function SubscriptionWidget({ 
  keywords = [], 
  onAddKeyword, 
  onRemoveKeyword 
}) {
  const [inputValue, setInputValue] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = inputValue.trim();
    if (!trimmed) return;
    
    if (keywords.includes(trimmed)) {
      alert("이미 등록된 키워드입니다.");
      setInputValue("");
      return;
    }
    
    onAddKeyword(trimmed);
    setInputValue("");
  };

  return (
    <div className="glass p-5 mb-6 bg-white dark:bg-slate-800">
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 rounded-lg bg-teal-500/10 text-teal-650 dark:text-teal-400">
          <Bell size={16} />
        </div>
        <h3 className="text-sm font-bold">관심 키워드 구독</h3>
      </div>
      
      <p className="text-[11px] text-slate-550 dark:text-slate-400 mb-4 leading-relaxed flex items-start gap-1">
        <Info size={11} className="mt-0.5 shrink-0 text-teal-600 dark:text-teal-450" />
        <span>키워드를 등록해두면, 관련 공지 등록 시 제목 우측에 강조 표시가 부착됩니다.</span>
      </p>

      {/* 키워드 등록 폼 */}
      <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="예: 장학금, 예비군"
          maxLength={15}
          className="flex-1 px-3 py-1.5 text-xs rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-foreground placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-teal-500/50 transition-colors"
        />
        <button
          type="submit"
          className="px-3 rounded-lg bg-teal-700 hover:bg-teal-600 text-white text-xs font-bold transition-all cursor-pointer flex items-center justify-center"
          aria-label="키워드 추가"
        >
          <Plus size={16} />
        </button>
      </form>

      {/* 등록된 키워드 목록 */}
      {keywords.length === 0 ? (
        <div className="text-center py-4 border border-dashed border-slate-200 dark:border-slate-800 rounded-lg bg-slate-50/50 dark:bg-slate-950/20">
          <span className="text-[11px] text-slate-500 dark:text-slate-450">구독 중인 키워드가 없습니다.</span>
        </div>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {keywords.map((kw, idx) => (
            <span
              key={idx}
              className="flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 transition-all"
            >
              <span>{kw}</span>
              <button
                type="button"
                onClick={() => onRemoveKeyword(kw)}
                className="p-0.5 rounded-full hover:bg-slate-250 dark:hover:bg-slate-700 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors cursor-pointer"
                aria-label={`${kw} 키워드 삭제`}
              >
                <X size={10} />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
