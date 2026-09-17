import { backendUrl } from '../../api/base';
import { DeleteOutlined } from '@ant-design/icons';
import type { ScanFile } from './types';

interface ScannedFilesProps {
  files: ScanFile[];
  selectedFileUrls: string[];
  selectedFileColor: string | null;
  onSelectFile: (file: ScanFile) => void;
  onDeleteFile: (file: ScanFile) => void;
  onPreviewFile: (file: ScanFile) => void;
}

export default function ScannedFiles({
  files,
  selectedFileUrls,
  selectedFileColor,
  onSelectFile,
  onDeleteFile,
  onPreviewFile,
}: ScannedFilesProps) {
  return (
    <section className="scanned-files-panel rounded-[24px] bg-[#fff7f0] p-5 ring-1 ring-[#f7c7b5]">
      <div className="scanned-files-header mb-5 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-slate-800">File quét</h2>
      </div>

      {files.length === 0 ? (
        <div className="scanned-files-items">
          <div className="flex min-h-[250px] items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white/60 text-sm text-slate-400">
            Chưa có file quét
          </div>
        </div>
      ) : (
        <div className="scanned-files-items grid gap-4 sm:grid-cols-2">
          {files.map((file, index) => {
            const isSelected = selectedFileUrls.includes(file.url);

            return (
              <div
                key={file.url}
                onClick={() => onSelectFile(file)}
                className={`cursor-pointer rounded-[18px] border bg-gray-300 p-4 shadow-[0_8px_20px_rgba(15,23,42,0.16)] transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_12px_28px_rgba(15,23,42,0.24)] ${
                  isSelected
                    ? 'border-[#bd2517] bg-[#fff0eb] shadow-[0_10px_30px_rgba(189,37,23,0.25)] ring-2 ring-[#e63a12]/50'
                      : 'border-[#f2d8cc]'
                }`}
              >
                <div className="mb-3 flex items-center justify-around gap-3 w-full">
                  {isSelected && selectedFileColor && (
                    <span
                      className={`h-4 w-4 shrink-0 rounded-full ring-2 ring-white shadow-md ${selectedFileColor}`}
                      aria-label="Page đã được chọn cho tài liệu hiện tại"
                    />
                  )}
                  <span className="truncate text-sm font-medium text-slate-600">
                    {index + 1}
                  </span>
                  <span className="shrink-0 font-bold text-xs text-black hover:text-blue-500 text-center">
                    Chọn page
                  </span>
                  <button
                    type="button"
                    onClick={event => {
                      event.stopPropagation();
                      onDeleteFile(file);
                    }}
                    className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-red-600 text-white shadow-sm ring-1 ring-red-100 transition hover:bg-red-50 hover:text-red-600 hover:ring-red-200"
                    title={`Xóa Page ${index + 1}`}
                    aria-label={`Xóa Page ${index + 1}`}
                  >
                    <DeleteOutlined />
                  </button>
                </div>

                <div
                  className="overflow-hidden rounded-2xl bg-gradient-to-br from-[#fff1e8] via-[#fffaf7] to-[#ffe8de]"
                  onClick={event => {
                    event.stopPropagation();
                    onPreviewFile(file);
                  }}
                  role="button"
                  tabIndex={0}
                  onKeyDown={event => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault();
                      event.stopPropagation();
                      onPreviewFile(file);
                    }
                  }}
                  aria-label={`Xem phóng to Page ${index + 1}`}
                >
                  <img
                    className="h-auto w-full cursor-zoom-in object-contain"
                    src={`${backendUrl}${file.link}`}
                    alt={`Scanned File Page ${index + 1}`}
                  />

                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
