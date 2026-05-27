"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, FileText, Download, ExternalLink, MessageSquare, CheckSquare } from "lucide-react";

/* 
 * [OSS Upgrade] - DetailModal 디자인 정돈
 * 개량 내용:
 * 1. 테마 포인트 컬러를 스카이블루에서 대학교 공식 테마 컬러인 청록색(Teal)으로 변경.
 */

export default function DetailModal({ isOpen, onClose, notice }) {
  const [activeTab, setActiveTab] = useState("summary"); // "summary" | "content"
  const [downloadingFile, setDownloadingFile] = useState(null);

  if (!isOpen || !notice) return null;

  const handleDownload = (fileName) => {
    setDownloadingFile(fileName);
    setTimeout(() => {
      setDownloadingFile(null);
      alert(`[안내] '${fileName}' 파일이 다운로드되었습니다.`);
    }, 1000);
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* 백드롭 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        />

        {/* 모달 박스 */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.98, y: 20 }}
          transition={{ duration: 0.2 }}
          className="glass w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col relative z-10"
        >
          {/* 모달 헤더 */}
          <div className="p-5 pb-4 border-b border-slate-100 dark:border-slate-800 flex justify-between items-start gap-4">
            <div>
              <span className="text-[10px] uppercase font-bold text-teal-600 dark:text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/20 mb-2 inline-block">
                공지사항 상세
              </span>
              <h2 className="text-base md:text-lg font-bold leading-snug">{notice.title}</h2>
              <div className="flex gap-2.5 text-xs text-text-muted mt-1.5">
                <span>{notice.writer}</span>
                <span>•</span>
                <span>{notice.date}</span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-text-muted hover:text-foreground transition-all cursor-pointer shrink-0"
              aria-label="닫기"
            >
              <X size={16} />
            </button>
          </div>

          {/* 탭 네비게이션 */}
          <div className="flex px-5 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-black/10">
            <button
              onClick={() => setActiveTab("summary")}
              className={`py-3 px-4 text-xs font-bold flex items-center gap-1.5 border-b-2 transition-all cursor-pointer ${
                activeTab === "summary"
                  ? "border-teal-500 text-teal-600 dark:text-teal-400 font-extrabold"
                  : "border-transparent text-text-muted hover:text-foreground"
              }`}
            >
              <CheckSquare size={13} />
              핵심 요약 정보
            </button>
            <button
              onClick={() => setActiveTab("content")}
              className={`py-3 px-4 text-xs font-bold flex items-center gap-1.5 border-b-2 transition-all cursor-pointer ${
                activeTab === "content"
                  ? "border-teal-500 text-teal-600 dark:text-teal-400 font-extrabold"
                  : "border-transparent text-text-muted hover:text-foreground"
              }`}
            >
              <FileText size={13} />
              공지 원본 본문
            </button>
          </div>

          {/* 모달 바디 (스크롤) */}
          <div className="p-5 overflow-y-auto flex-1 text-xs md:text-sm leading-relaxed">
            {activeTab === "summary" ? (
              <div className="space-y-4">
                {/* 3줄 요약 카드 */}
                <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-150 dark:border-slate-800/80">
                  <h3 className="text-[11px] font-bold text-teal-600 dark:text-teal-400 mb-2.5 flex items-center gap-1">
                    <CheckSquare size={12} />
                    주요 공지사항 요약
                  </h3>
                  <ul className="space-y-2.5 text-slate-700 dark:text-slate-200">
                    {notice.summary.map((sum, idx) => (
                      <li key={idx} className="flex items-start gap-2 leading-relaxed">
                        <span className="text-teal-600 dark:text-teal-400 font-bold mt-0.5">•</span>
                        <span>{sum}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* 행동 팁 */}
                <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-150 dark:border-slate-800/80">
                  <h3 className="text-[11px] font-bold text-slate-800 dark:text-slate-200 mb-2.5 flex items-center gap-1.5">
                    <MessageSquare size={12} className="text-teal-500" />
                    유의사항 및 신청 가이드
                  </h3>
                  <div className="space-y-2.5 text-xs text-text-muted">
                    <div className="p-2.5 rounded bg-white dark:bg-slate-950 border border-slate-100 dark:border-slate-800/50">
                      <span className="font-bold text-foreground block mb-0.5">📌 마감 기한 엄수</span>
                      <span>신청 마감일 직전에는 홈페이지 접속이 지연될 수 있으므로, 최소 하루 전까지 신청을 마치는 것을 추천합니다.</span>
                    </div>
                    <div className="p-2.5 rounded bg-white dark:bg-slate-950 border border-slate-100 dark:border-slate-800/50">
                      <span className="font-bold text-foreground block mb-0.5">📌 필수 제출 서류 확인</span>
                      <span>제출해야 할 서류의 목록과 파일 확장자가 미리 확인하시기 바랍니다. 기타 문의는 {notice.writer}로 연락 바랍니다.</span>
                    </div>
                  </div>
                </div>

                {/* 태그 */}
                {notice.keyPoints && notice.keyPoints.length > 0 && (
                  <div>
                    <h4 className="text-[10px] font-bold text-text-muted mb-1.5">핵심 키워드</h4>
                    <div className="flex flex-wrap gap-1">
                      {notice.keyPoints.map((kp, idx) => (
                        <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300">
                          #{kp}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="font-sans text-slate-800 dark:text-slate-200 text-xs md:text-sm whitespace-pre-wrap break-all bg-slate-50 dark:bg-slate-900 p-4 rounded-lg border border-slate-150 dark:border-slate-800">
                {notice.content}
              </div>
            )}

            {/* 첨부파일 */}
            {notice.attachments && notice.attachments.length > 0 && (
              <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-800">
                <h3 className="text-[11px] font-bold text-foreground mb-2.5">첨부파일 ({notice.attachments.length})</h3>
                <div className="space-y-1.5">
                  {notice.attachments.map((file, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-800"
                    >
                      <div className="flex items-center gap-2 overflow-hidden">
                        <FileText size={14} className="text-teal-500 shrink-0" />
                        <div className="overflow-hidden">
                          <p className="text-xs text-foreground truncate font-medium">{file.name}</p>
                          <p className="text-[10px] text-text-muted">{file.size}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDownload(file.name)}
                        disabled={downloadingFile === file.name}
                        className="p-1.5 rounded bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 text-text-muted hover:text-teal-500 transition-all cursor-pointer"
                      >
                        {downloadingFile === file.name ? (
                          <div className="w-3 h-3 border-2 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                          <Download size={12} />
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* 모달 푸터 */}
          <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-black/10 flex justify-between items-center gap-3">
            <span className="text-[11px] text-text-muted hidden sm:inline-block">출처: 대학 공식 홈페이지</span>
            <div className="flex gap-2 w-full sm:w-auto ml-auto">
              <a
                href={notice.originalUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-1 px-3 py-1.5 rounded border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-bold transition-all text-foreground w-full sm:w-auto text-center"
              >
                <span>원본 바로가기</span>
                <ExternalLink size={11} />
              </a>
              <button
                onClick={onClose}
                className="px-4 py-1.5 rounded bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold transition-all cursor-pointer w-full sm:w-auto text-center"
              >
                닫기
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
