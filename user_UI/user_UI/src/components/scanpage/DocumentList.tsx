import type { DocumentItem, ScanFile } from './types';
import { FolderOpenOutlined } from "@ant-design/icons";

interface DocumentListProps {
  documents: DocumentItem[];
  scannedFiles: ScanFile[];
  focusDocumentId: string | null;
  submissionSetIndex: number;
  submissionSetCount: number;
  onSelectDocument: (srID: string) => void;
  onPreviousSubmissionSet: () => void;
  onNextSubmissionSet: () => void;
  onOpenAddDocument: () => void;
}

export default function DocumentList({
  documents,
  scannedFiles,
  focusDocumentId,
  submissionSetIndex,
  submissionSetCount,
  onSelectDocument,
  onOpenAddDocument,
  onPreviousSubmissionSet,
  onNextSubmissionSet,
}: DocumentListProps) {
  return (
    <aside className="document-list-panel rounded-[24px] bg-[#fff7f0] p-5 ring-1 ring-[#f7c7b5] xl:sticky xl:top-6 xl:self-start xl:max-h-[calc(100vh-3rem)]">
      <div className="document-list-header mb-5 flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2">
          <FolderOpenOutlined />
          <h2 className="text-2xl font-bold text-slate-800">Hồ sơ {submissionSetIndex + 1}</h2>
        </div>
        {submissionSetCount > 1 && (
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={onPreviousSubmissionSet}
              disabled={submissionSetIndex === 0}
              className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-[#f2c7b8] bg-white text-[#921507] transition hover:bg-[#fff0e8] disabled:cursor-not-allowed disabled:opacity-40"
              aria-label="Hồ sơ trước"
              title="Hồ sơ trước"
            >
              ‹
            </button>
            <span className="min-w-12 text-center text-xs font-semibold text-slate-500">
              {submissionSetIndex + 1}/{submissionSetCount}
            </span>
            <button
              type="button"
              onClick={onNextSubmissionSet}
              disabled={submissionSetIndex === submissionSetCount - 1}
              className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-[#f2c7b8] bg-white text-[#921507] transition hover:bg-[#fff0e8] disabled:cursor-not-allowed disabled:opacity-40"
              aria-label="Hồ sơ tiếp theo"
              title="Hồ sơ tiếp theo"
            >
              ›
            </button>
          </div>
        )}
      </div>
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="text-sm font-semibold text-slate-500">Tài liệu</div>
        <button
          type="button"
          onClick={onOpenAddDocument}
          className="rounded-full bg-[#ffe1d5] px-3 py-2 text-sm font-semibold text-[#a21608] transition hover:bg-[#ffd0c1]"
        >
          + Thêm tài liệu
        </button>
      </div>

      <div className="document-list-items min-h-0 space-y-3 overflow-y-auto pr-1.5 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-[#e63a12]/40 scrollbar-thumb-rounded-full">
        {documents.map(doc => {
          const isFocus = focusDocumentId === doc.srID;
          const selectedPageNumbers = scannedFiles
            .map((file, index) =>
              doc.files?.includes(file.url) ? index + 1 : null
            )
            .filter((page): page is number => page !== null);

          return (
            <div
              key={doc.srID}
              onClick={() => onSelectDocument(doc.srID)}
              className={`cursor-pointer rounded-2xl border bg-white/90 px-4 py-3 text-sm font-medium text-slate-700 shadow-sm transition-all ${
                isFocus
                  ? 'border-[#bd2517] bg-[#fff0e8] shadow-[0_0_0_3px_rgba(255,255,255,0.95),0_0_0_6px_rgba(230,58,18,0.38),0_12px_28px_rgba(189,37,23,0.28)]'
                  : 'border-[#f2d8cc] hover:border-[#e63a12]/60'
              }`}
            >
              <div className="flex flex-wrap items-center gap-2">
                <div
                  className={`h-3.5 w-3.5 shrink-0 rounded-full ${doc.color ?? 'bg-slate-400'}`}
                />
                <span className="flex-1">{doc.title}</span>
                {doc.files && doc.files.length > 0 && (
                  <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-500">
                    {doc.files.length} page{doc.files.length > 1 ? 's' : ''}
                  </span>
                )}
              </div>

              <div className="mt-2 flex flex-wrap items-center gap-1.5">
                <span className="text-xs text-slate-400">Page đã chọn:</span>
                {selectedPageNumbers.length > 0 ? (
                  selectedPageNumbers.map(page => (
                    <span
                      key={`${doc.srID}-page-${page}`}
                      className="rounded-full bg-[#ffe9df] px-2 py-0.5 text-xs font-semibold text-[#a21608]"
                    >
                      Page {page}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-400">Chưa có</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
