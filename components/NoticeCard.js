"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Calendar, Eye, Bookmark, FileText, ChevronDown, ChevronUp, CheckSquare } from "lucide-react";

/* 
 * [OSS Upgrade] - NoticeCard 가독성 개선
 * 개량 내용:
 * 1. 라이트 모드에서 거의 인식이 불가하던 연회색 메타 텍스트(조회수, 날짜, 태그 라벨 등)를 
 *    명도 대비가 보장된 slate-500/slate-600 표준 클래스로 대체.
 * 2. 카테고리 맵핑 중 발견된 Tailwind 수치 오류(text-slate-650)를 표준값으로 교정.
 */

export default function NoticeCard({ 
  notice, 
  isBookmarked, 
  onToggleBookmark, 
  onOpenDetail,
  subscribedKeywords = []
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  // 관심 키워드 매칭 검사
  const matchedKeywords = subscribedKeywords.filter(keyword => 
    keyword.trim() !== "" && (
      notice.title.includes(keyword) || 
      notice.content.includes(keyword) || 
      (notice.keyPoints && notice.keyPoints.some(kp => kp.includes(keyword)))
    )
  );
  
  const isHighlighted = matchedKeywords.length > 0;

  // 신규 9대 학사공지 카테고리별 차분한 톤 색상 매핑
  const categoryColors = {
    "수업학적": "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
    "장학": "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
    "등록": "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
    "복지": "bg-pink-500/10 text-pink-600 dark:text-pink-400 border-pink-500/20",
    "교육봉사": "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20",
    "도서관": "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/20",
    "학생모집": "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20",
    "예비군": "bg-lime-500/10 text-lime-650 dark:text-lime-400 border-lime-500/20",
    "행정안내": "bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20"
  };

  const getCategoryClass = (cat) => categoryColors[cat] || "bg-teal-500/10 text-teal-600 dark:text-teal-400 border-teal-500/20";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className={`glass p-5 mb-4 relative overflow-hidden transition-all duration-205 bg-white dark:bg-slate-800 ${
        isHighlighted 
          ? "matched-border bg-teal-500/[0.01]" 
          : "hover:border-slate-400/30"
      }`}
    >
      {/* 관심 키워드 감지 배지 */}
      {isHighlighted && (
        <div className="absolute top-0 right-0 bg-teal-700 text-white text-[10px] font-bold px-2.5 py-1 rounded-bl-lg flex items-center gap-1 shadow-sm">
          <span>키워드 감지: {matchedKeywords[0]}</span>
        </div>
      )}

      {/* 카드 헤더 영역 */}
      <div className="flex justify-between items-start gap-4 mb-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className={`text-[11px] px-2 py-0.5 rounded font-bold border ${getCategoryClass(notice.category)}`}>
            {notice.category}
          </span>
          <span className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-1">
            <Calendar size={11} />
            {notice.date}
          </span>
        </div>
        <button 
          onClick={(e) => {
            e.stopPropagation();
            onToggleBookmark(notice.id);
          }}
          className={`p-1.5 rounded-lg border transition-all duration-150 cursor-pointer ${
            isBookmarked 
              ? "bg-teal-500/15 border-teal-500/30 text-teal-600 dark:text-teal-400" 
              : "border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 hover:text-foreground"
          }`}
          aria-label="북마크 토글"
        >
          <Bookmark size={14} fill={isBookmarked ? "currentColor" : "none"} />
        </button>
      </div>

      {/* 제목 및 작성자 정보 */}
      <h3 className="text-base font-bold leading-snug mb-2 cursor-pointer hover:text-accent transition-colors"
          onClick={() => setIsExpanded(!isExpanded)}>
        {notice.title}
      </h3>
      
      <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
        <span>{notice.writer}</span>
        <span className="flex items-center gap-1">
          <Eye size={11} />
          {notice.views}회 조회
        </span>
      </div>

      {/* 펼침 및 요약 정보 영역 */}
      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex flex-col">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center justify-center gap-1.5 w-full py-2 text-xs text-teal-600 dark:text-teal-400 font-bold rounded-lg bg-teal-500/5 hover:bg-teal-500/10 border border-teal-500/10 transition-all duration-150 cursor-pointer"
        >
          <FileText size={12} className="text-teal-600 dark:text-teal-400" />
          <span>{isExpanded ? "요약 닫기" : "핵심 3줄 요약 보기"}</span>
          {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2, ease: "easeInOut" }}
              className="overflow-hidden"
            >
              <div className="mt-3.5 p-4 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-150 dark:border-slate-800 relative">
                <h4 className="text-[11px] font-bold text-teal-600 dark:text-teal-400 mb-2.5 flex items-center gap-1 uppercase tracking-wide">
                  <CheckSquare size={11} />
                  주요 공지 내용 요약
                </h4>
                
                <ul className="text-xs md:text-sm space-y-2.5 text-slate-700 dark:text-slate-200">
                  {notice.summary.map((sum, index) => (
                    <li key={index} className="flex items-start gap-2 leading-relaxed">
                      <span className="text-teal-600 dark:text-teal-400 mt-1 select-none font-black">•</span>
                      <span>{sum}</span>
                    </li>
                  ))}
                </ul>

                {/* 핵심 키워드 목록 */}
                {notice.keyPoints && notice.keyPoints.length > 0 && (
                  <div className="mt-3.5 pt-3 border-t border-slate-200 dark:border-slate-800/80 flex flex-wrap gap-1.5 items-center">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 mr-1">태그:</span>
                    {notice.keyPoints.map((kp, idx) => (
                      <span 
                        key={idx} 
                        className={`text-[10px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-650 dark:text-slate-300 border border-slate-200 dark:border-slate-700 ${
                          subscribedKeywords.includes(kp) ? "border-teal-500/40 text-teal-600 dark:text-teal-300 font-bold" : ""
                        }`}
                      >
                        #{kp}
                      </span>
                    ))}
                  </div>
                )}

                {/* 하단 행동 버튼 */}
                <div className="mt-3.5 flex gap-2 justify-end">
                  <button
                    onClick={() => onOpenDetail(notice)}
                    className="px-3 py-1.5 text-xs font-bold rounded bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-foreground transition-all duration-100 cursor-pointer"
                  >
                    본문 및 첨부파일 전체 보기
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
