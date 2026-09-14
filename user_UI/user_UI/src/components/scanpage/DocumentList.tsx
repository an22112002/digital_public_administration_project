import type { DocumentItem, ScanFile } from './types';
import { FolderOpenOutlined } from "@ant-design/icons";

interface DocumentListProps {
  documents: DocumentItem[];
  scannedFiles: ScanFile[];
  focusDocumentId: string | null;
  onSelectDocument: (srID: string) => void;
  onOpenAddDocument: () => void;
}

export default function DocumentList({
  documents,
  scannedFiles,
  focusDocumentId,
  onSelectDocument,
  onOpenAddDocument,
}: DocumentListProps) {
  return (
    <aside className="rounded-[24px] bg-[#f4fbfb] p-5 ring-1 ring-[#dfeff1] xl:sticky xl:top-6 xl:self-start xl:max-h-[calc(100vh-3rem)] xl:overflow-y-auto">
      <div className="mb-5 flex items-center justify-between gap-3">
        <h2 className="text-2xl font-bold text-slate-800"><FolderOpenOutlined/>&nbsp;Tài liệu</h2>
        <button
          type="button"
          onClick={onOpenAddDocument}
          className="rounded-full bg-emerald-100 px-3 py-2 text-sm font-semibold text-[#118a67] transition hover:bg-gradient-to-r hover:from-emerald-200 hover:to-emerald-300"
        >
          + Thêm tài liệu
        </button>
      </div>

      <div className="space-y-3">
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
                  ? 'border-[#32b5b8] ring-2 ring-[#32b5b8]/30'
                  : 'border-[#dfecef] hover:border-[#32b5b8]/50'
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
                      className="rounded-full bg-[#e6f7f5] px-2 py-0.5 text-xs font-semibold text-[#168b86]"
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