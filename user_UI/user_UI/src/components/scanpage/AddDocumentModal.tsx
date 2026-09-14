interface AddDocumentModalProps {
  open: boolean;
  supplementalTitles: { srID: string; title: string }[];
  extensionDocumentTypes: string[];
  newDocumentType: string | undefined;
  onClose: () => void;
  onSelectSupplemental: (srID: string) => void;
  onAddDocument: (type: string) => void;
  onNewDocumentTypeChange: (value: string) => void;
}

export default function AddDocumentModal({
  open,
  supplementalTitles,
  extensionDocumentTypes,
  newDocumentType,
  onClose,
  onSelectSupplemental,
  onAddDocument,
  onNewDocumentTypeChange,
}: AddDocumentModalProps) {
  if (!open) {
    return null;
  }

  const documentNameSuggestions = Array.from(
    new Set([
      ...extensionDocumentTypes,
      ...supplementalTitles.map(document => document.title),
    ])
  ).filter(type => {
    const searchText = newDocumentType?.trim().toLocaleLowerCase() ?? '';
    return searchText.length > 0 &&
      type.toLocaleLowerCase().includes(searchText) &&
      type.toLocaleLowerCase() !== searchText;
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
      <div className="w-full max-w-md rounded-[24px] bg-white p-6 shadow-[0_30px_80px_rgba(15,23,42,0.2)]">
        <div className="mb-5 flex items-center justify-between">
          <h3 className="text-xl font-bold text-slate-800">Chọn loại giấy tờ</h3>
          <button
            type="button"
            onClick={onClose}
            className="text-xl font-medium text-slate-400 transition hover:text-slate-600"
          >
            ×
          </button>
        </div>

        <div className="space-y-3">
          <div>
            <h4 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Giấy tờ gốc bổ sung
            </h4>
            {supplementalTitles.length === 0 ? (
              <p className="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-400">
                Không có giấy tờ gốc bổ sung
              </p>
            ) : (
              <div className="space-y-2">
                {supplementalTitles.map(document => (
                  <button
                    key={document.srID}
                    type="button"
                    onClick={() => onSelectSupplemental(document.srID)}
                    className="flex w-full items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-left text-base font-medium text-slate-700 transition hover:border-[#32b5b8] hover:bg-[#f0fbfb]"
                  >
                    <span>{document.title}</span>
                    <span className="text-sm text-slate-400">→</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="border-t border-slate-200 pt-3">
            <h4 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Giấy tờ bổ sung
            </h4>
            <div className="relative mt-2">
              <input
                type="text"
                placeholder="Tên giấy tờ"
                value={newDocumentType}
                onChange={event => onNewDocumentTypeChange(event.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm outline-none transition focus:border-[#32b5b8]"
              />
              {documentNameSuggestions.length > 0 && (
                <div className="absolute inset-x-0 top-full z-10 mt-1 max-h-40 overflow-y-auto rounded-lg border border-slate-200 bg-white py-1 shadow-lg">
                  {documentNameSuggestions.map(type => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => onNewDocumentTypeChange(type)}
                      className="block w-full px-3 py-2 text-left text-sm text-slate-700 transition hover:bg-[#f0fbfb]"
                    >
                      {type}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <button
              className="mt-2 w-full rounded-lg bg-[#32b5b8] px-3 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1e7bd8]"
              type="button"
              onClick={() => {
                const type = newDocumentType?.trim();
                if (type) {
                  onAddDocument(type);
                }
              }}
            >
              + Thêm giấy tờ
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}