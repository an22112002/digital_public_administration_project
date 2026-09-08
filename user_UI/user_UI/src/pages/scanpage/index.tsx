import { useState, useEffect, useRef } from 'react';
import Header from '../../header/header';
import { useParams } from 'react-router-dom';
import { getScannerOptions } from '../../api/scannerAPI';
import type { ScannerOption } from '../../api/scannerAPI';
import { Modal } from 'antd';

interface DocumentItem {
  srID: string;
  serviceID: number;
  code: string;
  title: string;
  description: string;
  required: boolean;
  ocr_enabled: boolean;
  color: string | null;
  files: string[] | null;
}

interface ScanFile {
  url: string;
  link: string;
}

interface SendFile {
  srID: string;
  files: string[];
}

export default function ScanPage() {
  const websocket = useRef<WebSocket | null>(null);
  const fileInput = useRef<HTMLInputElement | null>(null);

  const { serviceID } = useParams<{ serviceID: string }>();

  console.log('Service ID:', serviceID);

  // =========================================================
  // STATE
  // =========================================================

  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [scannedFiles, setScannedFiles] = useState<ScanFile[]>([]);

  // Chỉ lưu ID của document đang focus
  const [focusDocumentId, setFocusDocumentId] = useState<string | null>(
    null
  );

  const [scannerOptions, setScannerOptions] =
    useState<ScannerOption[]>([]);

  const [selectedScannerId, setSelectedScannerId] =
    useState('');

  const [isModalOpen, setIsModalOpen] = useState(false);

  const [isInProcess, setIsInProcess] = useState(false);

  const [hiddenDescriptions, setHiddenDescriptions] = useState<Record<string, boolean>>({});

  const [scanError, setScanError] = useState<string | null>(null);

  const [processError, setProcessError] = useState<string | null>(null);

  const extensionDocumentTypes = [
    'Căn cước công dân',
    'Giấy phép lái xe',
    'Thẻ bảo hiểm y tế',
  ];

  const [newExtensionDocumentTypes, setNewExtensionDocumentTypes] = useState<string>();

  useEffect(() => {
    if (processError) {
      setIsInProcess(false);
    }
  }, [processError]);

  // Document đang được chọn
  const focusDocument =
    documents.find(doc => doc.srID === focusDocumentId) ?? null;

  // =========================================================
  // WEBSOCKET RECEIVE
  // =========================================================

  const handleWebSocketReceive = (data: any) => {
    if (data['code'] === '0') {
      // Load danh sách document lần đầu
      const receivedDocuments: DocumentItem[] = data['documents'] ?? [];

      const newDocuments = receivedDocuments.map(
        (doc, index) => ({
          ...doc,
          color: getFileColorFromIndex(index),
          files: doc.files ?? [],
        })
      );

      setDocuments(newDocuments);

      // Nếu chưa có document nào được chọn
      // thì chọn document đầu tiên
      if (newDocuments.length > 0 && !focusDocumentId) {
        setFocusDocumentId(newDocuments[0].srID);
      }

      return;
    }

    // =======================================================
    // ERROR
    // =======================================================

    if (data['error'] !== null && data['error'] !== undefined) {
      console.error(
        'Error from WebSocket:',
        data['error']
      );
    }

    // =======================================================
    // SCAN STATUS
    // =======================================================

    if (data['type'] === 'scan_status') {
      const errorMessage =
        data['message'] ??
        data['error'] ??
        'Có lỗi xảy ra khi quét';

      switch (data['status']) {
        case 'started':
          setScanError(null);
          console.log('Scan started');
          break;

        case 'success': {
          setScanError(null);
          const images: ScanFile[] = data['images'] ?? [];

          // Không thêm colors vào scannedFiles nữa.
          // Màu sẽ được tính dựa trên documents.
          setScannedFiles(images);

          console.log('Scan successful');
          break;
        }

        case 'error':
          setScanError(String(errorMessage));
          console.error(
            'Scan error:',
            errorMessage
          );
          break;

        default:
          break;
      }
    }

    if (data['type'] === 'webview') {
      const errorMessage =
          data['message'] ??
          data['error'] ??
          'Có lỗi xảy ra khi nộp hồ sơ';

      switch (data['status']) {

        case 'success': {
          setProcessError(null);
          const images: ScanFile[] = data['images'] ?? [];

          // Không thêm colors vào scannedFiles nữa.
          // Màu sẽ được tính dựa trên documents.
          setScannedFiles(images);

          console.log('Scan successful');
          break;
        }

        case 'start data processing':
          setIsInProcess(true);
          console.log('Start data processing');
          break;

        case 'started':
          setIsInProcess(false);
          console.log('Done process data, start to open webview');
          break;

        case 'error':
          setProcessError(String(errorMessage));
          console.error(
            'Process error:',
            errorMessage
          );
          break;

        default:
          break;
      }
    }
  };

  // =========================================================
  // ADD DOCUMENT
  // =========================================================

  const handleAddDocument = (type: string) => {
    const newDocumentItem: DocumentItem = {
      srID: `ADD:${type}:${Date.now()}`,
      serviceID: 0,
      code: '',
      title: type,
      description: '',
      required: false,
      ocr_enabled: false,
      files: [],
      color: getFileColorFromIndex(documents.length),
    };

    setDocuments(prev => [
      ...prev,
      newDocumentItem,
    ]);

    setHiddenDescriptions(prev => ({
      ...prev,
      [newDocumentItem.srID]: false,
    }));

    // Focus document mới
    setFocusDocumentId(newDocumentItem.srID);

    setIsModalOpen(false);

    setNewExtensionDocumentTypes("");
  };

  const updateDocumentDescription = (
    srID: string,
    description: string
  ) => {
    setDocuments(prevDocuments =>
      prevDocuments.map(doc =>
        doc.srID === srID
          ? { ...doc, description }
          : doc
      )
    );
  };

  const toggleDescriptionVisibility = (
    srID: string
  ) => {
    setHiddenDescriptions(prev => ({
      ...prev,
      [srID]: !(prev[srID] ?? false),
    }));
  };

  // =========================================================
  // START SCAN
  // =========================================================

  const startScan = () => {
    const selectedOption =
      scannerOptions.find(
        option => option.id === selectedScannerId
      ) ?? null;

    if (!selectedOption) {
      console.error(
        'Chưa có máy quét hợp lệ được chọn'
      );
      alert('Chưa có máy quét hợp lệ được chọn');

      return;
    }

    const requestData = {
      type: 'start_scan',
      request: {
        scanner: selectedOption.scanner,
        driver: selectedOption.driver,
      },
    };

    const ws = websocket.current;

    if (ws?.readyState === WebSocket.OPEN) {
      console.log(
        'Sending scan request:',
        requestData
      );

      ws.send(JSON.stringify(requestData));
    } else {
      console.error(
        'WebSocket is not connected'
      );
    }
  };

  // =========================================================
  // CHECK REQUIRED DOCUMENT
  // =========================================================

  const handleSubmitDocuments = () => {
    const missingRequiredDocs = documents.filter(
      doc =>
        doc.required &&
        (!doc.files || doc.files.length === 0)
    );

    if (missingRequiredDocs.length > 0) {
      console.error(
        'Có tài liệu bắt buộc chưa có file:',
        missingRequiredDocs
      );

      return;
    }

    const sendFiles: SendFile[] = documents.map(
      doc => ({
        srID: doc.srID,
        files: doc.files ?? [],
      })
    );

    const requestData = {
      type: 'start_webview',
      request: {
        files: sendFiles,
      },
    };

    console.log(
      'Sending request to submit documents:',
      requestData
    );

    const ws = websocket.current;

    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(requestData));
    } else {
      console.error(
        'WebSocket is not connected'
      );
    }
  };

  const handleImportFile = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    event.target.value = '';

    if (!file) {
      return;
    }

    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      alert('Vui lòng chọn file PDF');
      return;
    }

    const ws = websocket.current;

    if (ws?.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected');
      alert('WebSocket chưa kết nối');
      return;
    }

    const reader = new FileReader();

    reader.onload = () => {
      if (typeof reader.result !== 'string') {
        alert('Không thể đọc file PDF');
        return;
      }

      const requestData = {
        type: 'import_file',
        request: {
          filename: file.name,
          file: reader.result,
        },
      };

      ws.send(JSON.stringify(requestData));
    };

    reader.onerror = () => {
      alert('Không thể đọc file PDF');
    };

    reader.readAsDataURL(file);
  };

  // =========================================================
  // SELECT / UNSELECT FILE
  // =========================================================

  const handleSetFileSelectForDocument = (
    file: ScanFile
  ) => {
    if (!focusDocumentId) {
      console.warn(
        'Chưa chọn tài liệu'
      );

      return;
    }

    setDocuments(prevDocuments =>
      prevDocuments.map(doc => {
        // Không phải document đang focus
        if (doc.srID !== focusDocumentId) {
          return doc;
        }

        const currentFiles = doc.files ?? [];

        const isSelected =
          currentFiles.includes(file.url);

        // =============================================
        // CLICK LẠI
        // =============================================

        if (isSelected) {
          return {
            ...doc,

            files: currentFiles.filter(
              fileUrl => fileUrl !== file.url
            ),
          };
        }

        // =============================================
        // CLICK LẦN ĐẦU
        // =============================================

        return {
          ...doc,

          files: [
            ...currentFiles,
            file.url,
          ],
        };
      })
    );
  };

  // =========================================================
  // GET COLORS OF FILE
  // =========================================================

  const getFileColors = (
    fileUrl: string
  ): string[] => {
    const colors: string[] = [];

    for (const doc of documents) {
      if (
        doc.files?.includes(fileUrl) &&
        doc.color
      ) {
        colors.push(doc.color);
      }
    }

    return colors;
  };

  // =========================================================
  // CHECK FILE BELONGS TO CURRENT DOCUMENT
  // =========================================================

  const isFileSelectedForFocusDocument = (
    fileUrl: string
  ): boolean => {
    if (!focusDocument) {
      return false;
    }

    return (
      focusDocument.files?.includes(fileUrl) ??
      false
    );
  };

  // =========================================================
  // WEBSOCKET
  // =========================================================

  useEffect(() => {
    const loadScannerOptions = async () => {
      try {
        const data = await getScannerOptions();
        const options = data.options ?? [];

        setScannerOptions(options);

        if (data.default?.id) {
          setSelectedScannerId(data.default.id);
          return;
        }

        if (options.length > 0) {
          setSelectedScannerId(options[0].id);
        }
      } catch (error) {
        console.error(
          'Không tải được danh sách máy quét:',
          error
        );
      }
    };

    loadScannerOptions();
  }, []);

  useEffect(() => {
    if (!serviceID) {
      return;
    }

    const ws = new WebSocket(
      `ws://localhost:8000/process/service/${serviceID}`
    );

    websocket.current = ws;

    ws.onopen = () => {
      console.log(
        'WebSocket connection established'
      );
    };

    ws.onmessage = event => {
      try {
        console.log(
          'Received message:',
          event.data
        );

        const data = JSON.parse(event.data);

        handleWebSocketReceive(data);
      } catch (error) {
        console.error(
          'Error handling WebSocket message:',
          error
        );
      }
    };

    ws.onerror = error => {
      console.error(
        'WebSocket error:',
        error
      );
    };

    ws.onclose = () => {
      console.log(
        'WebSocket connection closed'
      );

      if (websocket.current === ws) {
        websocket.current = null;
      }
    };

    // Cleanup
    return () => {
      console.log(
        'Closing WebSocket'
      );

      if (
        ws.readyState ===
          WebSocket.OPEN ||
        ws.readyState ===
          WebSocket.CONNECTING
      ) {
        ws.close();
      }

      if (websocket.current === ws) {
        websocket.current = null;
      }
    };
  }, [serviceID]);

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="min-h-screen bg-[#eef5f4] px-4 py-8 text-slate-800">
      <Modal 
        open={isInProcess} footer={null} closable={false} centered>
        <div className="flex flex-col items-center gap-4">
          <svg
            className="h-12 w-12 animate-spin text-[#32b5b8]"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v8H4z"
            ></path>
          </svg>
          <p className="text-lg font-medium text-slate-800">
            Đang xử lý...
          </p>
        </div>
      </Modal>

      <div className="mx-auto max-w-6xl">

        <Header />

        {scanError && (
          <div className="mb-4 flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 shadow-sm">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="mt-0.5 h-5 w-5 shrink-0"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="9" />
              <path d="M12 7v6" />
              <path d="M12 16h.01" />
            </svg>
            <div>
              <p className="font-semibold">Lỗi quét</p>
              <p className="mt-0.5 text-red-600">{scanError}</p>
            </div>
          </div>
        )}

        {processError && (
          <div className="mb-4 flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 shadow-sm">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="mt-0.5 h-5 w-5 shrink-0"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="9" />
              <path d="M12 7v6" />
              <path d="M12 16h.01" />
            </svg>
            <div>
              <p className="font-semibold">Lỗi xử lý</p>
              <p className="mt-0.5 text-red-600">{processError}</p>
            </div>
          </div>
        )}

        <main className="rounded-[30px] bg-white p-5 shadow-[0_30px_70px_rgba(15,23,42,0.08)] ring-1 ring-slate-100 md:p-8">

          {/* ================================================= */}
          {/* FILE + DOCUMENT */}
          {/* ================================================= */}

          <div className="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">

            {/* ================================================= */}
            {/* SCANNED FILES */}
            {/* ================================================= */}

            <section className="rounded-[24px] bg-[#f4fbfb] p-5 ring-1 ring-[#dfeff1]">

              <div className="mb-5 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-800">
                  File quét
                </h2>

                {focusDocument && (
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <div
                      className={`h-3 w-3 rounded-full ${
                        focusDocument.color ??
                        'bg-slate-400'
                      }`}
                    />

                    <span>
                      Đang chọn: {focusDocument.title}
                    </span>
                  </div>
                )}
              </div>

              {scannedFiles.length === 0 ? (
                <div className="flex min-h-[250px] items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white/60 text-sm text-slate-400">
                  Chưa có file quét
                </div>
              ) : (
                <div className="grid gap-4 sm:grid-cols-2">

                  {scannedFiles.map((file, index) => {

                    const colors =
                      getFileColors(file.url);

                    const isSelected =
                      isFileSelectedForFocusDocument(
                        file.url
                      );

                    return (
                      <div
                        key={file.url}
                        onClick={() =>
                          handleSetFileSelectForDocument(
                            file
                          )
                        }
                        className={`
                          cursor-pointer
                          rounded-[18px]
                          border
                          bg-white/80
                          p-4
                          shadow-[0_12px_28px_rgba(15,23,42,0.04)]
                          transition-all
                          duration-200
                          hover:-translate-y-0.5
                          hover:shadow-[0_15px_35px_rgba(15,23,42,0.08)]

                          ${
                            isSelected
                              ? 'border-[#32b5b8] ring-2 ring-[#32b5b8]/30'
                              : 'border-[#dfecef]'
                          }
                        `}
                      >

                        {/* FILE HEADER */}

                        <div className="mb-3 flex items-center justify-between gap-3">

                          <span className="min-w-0 truncate text-sm font-medium text-slate-600">
                            page {index + 1}
                          </span>

                          {/* COLORS */}

                          <div className="flex shrink-0 items-center gap-1.5">

                            {colors.map(
                              (
                                color,
                                colorIndex
                              ) => (
                                <div
                                  key={`${file.url}-${colorIndex}`}
                                  className={`
                                    h-3.5
                                    w-3.5
                                    rounded-full
                                    ring-1
                                    ring-white
                                    shadow-sm
                                    ${color}
                                  `}
                                />
                              )
                            )}

                          </div>

                        </div>

                        {/* IMAGE */}

                        <div className="overflow-hidden rounded-2xl bg-gradient-to-br from-[#effaf7] via-[#f4fbfb] to-[#edf5ff]">

                          <img
                            className="h-auto w-full object-contain"
                            src={`http://localhost:8000${file.link}`}
                            alt="Scanned File"
                          />

                        </div>

                      </div>
                    );
                  })}

                </div>
              )}

            </section>

            {/* ================================================= */}
            {/* DOCUMENTS */}
            {/* ================================================= */}

            <aside className="rounded-[24px] bg-[#f4fbfb] p-5 ring-1 ring-[#dfeff1]">

              <div className="mb-5 flex items-center justify-between gap-3">

                <h2 className="text-2xl font-bold text-slate-800">
                  Tài liệu
                </h2>

                <button
                  type="button"
                  onClick={() =>
                    setIsModalOpen(true)
                  }
                  className="rounded-full bg-[#eafaf6] px-3 py-2 text-sm font-semibold text-[#118a67] transition hover:bg-[#dff7f0]"
                >
                  Thêm tài liệu
                </button>

              </div>

              <div className="space-y-3">

                {documents.map(doc => {

                  const isFocus =
                    focusDocumentId ===
                    doc.srID;

                  const fileCount =
                    doc.files?.length ?? 0;

                  const isDescriptionVisible =
                    !(hiddenDescriptions[doc.srID] ?? true);

                  const descriptionPreview =
                    doc.description?.trim()
                      ? doc.description.trim().length > 48
                        ? `${doc.description.trim().slice(0, 48)}...`
                        : doc.description.trim()
                      : 'Chưa có mô tả';

                  return (
                    <div
                      key={doc.srID}
                      onClick={() =>
                        setFocusDocumentId(
                          doc.srID
                        )
                      }
                      className={`
                        cursor-pointer
                        rounded-2xl
                        border
                        bg-white/90
                        px-4
                        py-3
                        text-sm
                        font-medium
                        text-slate-700
                        shadow-sm
                        transition-all

                        ${
                          isFocus
                            ? 'border-[#32b5b8] ring-2 ring-[#32b5b8]/30'
                            : 'border-[#dfecef] hover:border-[#32b5b8]/50'
                        }
                      `}
                    >

                      <div className="flex flex-wrap items-center gap-2">

                        {/* COLOR */}

                        <div
                          className={`
                            h-3.5
                            w-3.5
                            shrink-0
                            rounded-full
                            ${
                              doc.color ??
                              'bg-slate-400'
                            }
                          `}
                        />

                        {/* TITLE */}

                        <span className="flex-1">
                          {doc.title}
                        </span>

                        {/* FILE COUNT */}

                        {fileCount > 0 && (
                          <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-500">
                            {fileCount} file
                            {fileCount > 1
                              ? 's'
                              : ''}
                          </span>
                        )}

                        {/* REQUIRED */}

                        {doc.required && (
                          <span className="rounded-full bg-[#ffebee] px-2 py-1 text-xs text-[#c62828]">
                            Bắt buộc
                          </span>
                        )}

                      </div>

                      {isFocus && (
                        <div className="mt-3 border-t border-slate-200 pt-3">
                          <div className="mb-2 flex items-center justify-between gap-3">
                            <span className="text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">
                              Mô tả
                            </span>

                            <button
                              type="button"
                              onClick={event => {
                                event.stopPropagation();
                                toggleDescriptionVisibility(doc.srID);
                              }}
                              className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600 transition hover:bg-slate-200"
                            >
                              {isDescriptionVisible ? (
                                <svg
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  stroke="currentColor"
                                  strokeWidth="1.8"
                                  className="h-3.5 w-3.5"
                                  aria-hidden="true"
                                >
                                  <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/>
                                  <circle cx="12" cy="12" r="3"/>
                                </svg>
                              ) : (
                                <svg
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  stroke="currentColor"
                                  strokeWidth="1.8"
                                  className="h-3.5 w-3.5"
                                  aria-hidden="true"
                                >
                                  <path d="M3 3l18 18"/>
                                  <path d="M10.6 10.6A3 3 0 0 0 13.4 13.4"/>
                                  <path d="M9.1 5.5A11.3 11.3 0 0 1 12 5c6.5 0 10 7 10 7a16.8 16.8 0 0 1-4.5 5.5"/>
                                  <path d="M6.2 6.2A16.8 16.8 0 0 0 2 12s3.5 7 10 7a10.8 10.8 0 0 0 4.4-1"/>
                                </svg>
                              )}
                              {isDescriptionVisible ? 'Ẩn' : 'Hiện'}
                            </button>
                          </div>

                          {isDescriptionVisible ? (
                            <textarea
                              value={doc.description ?? ''}
                              onClick={event =>
                                event.stopPropagation()
                              }
                              onChange={event =>
                                updateDocumentDescription(
                                  doc.srID,
                                  event.target.value
                                )
                              }
                              rows={4}
                              placeholder="Nhập mô tả cho tài liệu..."
                              className="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-[#32b5b8] focus:bg-white focus:ring-2 focus:ring-[#32b5b8]/15"
                            />
                          ) : (
                            <div className="rounded-xl border border-slate-200 bg-slate-50 px-2.5 py-2 text-xs text-slate-500">
                              <div className="truncate">
                                {descriptionPreview}
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                    </div>
                  );
                })}

              </div>

            </aside>

          </div>

          {/* ================================================= */}
          {/* FOOTER */}
          {/* ================================================= */}

          <div className="mt-8 flex flex-col gap-4 border-t border-slate-200 pt-5 sm:flex-row sm:items-center sm:justify-between">

            {/* SCANNER */}

            <div className="flex items-center gap-3">

              <label
                className="text-sm font-medium text-slate-600"
                htmlFor="scanner-select"
              >
                Máy quét
              </label>

              <select
                id="scanner-select"
                value={selectedScannerId}
                onChange={event =>
                  setSelectedScannerId(
                    event.target.value
                  )
                }
                className="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-700 shadow-sm outline-none transition focus:border-[#32b5b8]"
              >
                {scannerOptions.length === 0 ? (
                  <option value="">
                    Không có máy quét
                  </option>
                ) : (
                  scannerOptions.map(option => (
                    <option
                      key={option.id}
                      value={option.id}
                    >
                      {option.label}
                    </option>
                  ))
                )}
              </select>

            </div>

            {/* BUTTONS */}

            <div className="flex items-center gap-3">

              <input
                ref={fileInput}
                type="file"
                accept=".pdf,application/pdf"
                className="hidden"
                onChange={handleImportFile}
              />

              <button
                type="button"
                className="inline-flex items-center justify-center rounded-[16px] bg-[#3978c7] px-8 py-3.5 text-base font-semibold text-white shadow-[0_12px_30px_rgba(57,120,199,0.28)] transition hover:bg-[#2f68b1]"
                onClick={() => fileInput.current?.click()}
              >
                Nộp file
              </button>

              <button
                type="button"
                className="inline-flex items-center justify-center rounded-[16px] bg-[#28a9a9] px-8 py-3.5 text-base font-semibold text-white shadow-[0_12px_30px_rgba(40,169,169,0.35)] transition hover:bg-[#219a9a]"
                onClick={startScan}
              >
                Quét
              </button>

              <button
                type="button"
                className="inline-flex items-center justify-center rounded-[16px] bg-[#1ea56d] px-8 py-3.5 text-base font-semibold text-white shadow-[0_12px_30px_rgba(30,165,109,0.3)] transition hover:bg-[#17945f]"
                onClick={
                  handleSubmitDocuments
                }
              >
                Nộp hồ sơ
              </button>

            </div>

          </div>

        </main>

      </div>

      {/* ===================================================== */}
      {/* ADD DOCUMENT MODAL */}
      {/* ===================================================== */}

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">

          <div className="w-full max-w-md rounded-[24px] bg-white p-6 shadow-[0_30px_80px_rgba(15,23,42,0.2)]">

            {/* HEADER */}

            <div className="mb-5 flex items-center justify-between">

              <h3 className="text-xl font-bold text-slate-800">
                Chọn loại giấy tờ
              </h3>

              <button
                type="button"
                onClick={() =>
                  setIsModalOpen(false)
                }
                className="text-xl font-medium text-slate-400 transition hover:text-slate-600"
              >
                ×
              </button>

            </div>

            {/* DOCUMENT TYPES */}

            <div className="space-y-3">

              {extensionDocumentTypes.map(
                type => (
                  <button
                    key={type}
                    type="button"
                    onClick={() =>
                      handleAddDocument(
                        type
                      )
                    }
                    className="flex w-full items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-left text-base font-medium text-slate-700 transition hover:border-[#32b5b8] hover:bg-[#f0fbfb]"
                  >

                    <span>
                      {type}
                    </span>

                    <span className="text-sm text-slate-400">
                      →
                    </span>

                  </button>
                )
              )}
              <div>
                <span className="text-sm text-slate-400 mt-2 block">
                  Nếu loại giấy tờ bạn cần không có trong danh sách, vui lòng điền tên giấy tờ xuống dưới và ấn "Thêm giấy tờ" để thêm vào danh sách.
                </span>

                <input
                  type="text"
                  placeholder="Tên giấy tờ"
                  value={newExtensionDocumentTypes}
                  onChange={(e) => setNewExtensionDocumentTypes(e.target.value)}
                  className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm outline-none transition focus:border-[#32b5b8]"
                />
                <button
                  className="mt-2 w-full rounded-lg bg-[#32b5b8] px-3 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1e7bd8]"
                  type="button"
                  onClick={() => {
                    if (newExtensionDocumentTypes && newExtensionDocumentTypes.trim() !== "") {
                      handleAddDocument(newExtensionDocumentTypes.trim());
                      setNewExtensionDocumentTypes("");
                    }
                  }}
                >
                  Thêm giấy tờ
                </button>
              </div>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}

// =========================================================
// GET DOCUMENT COLOR
// =========================================================

function getFileColorFromIndex(
  index: number
): string {
  const colors = [
    'bg-slate-400',
    'bg-teal-400',
    'bg-blue-400',
    'bg-purple-400',
    'bg-pink-400',
    'bg-orange-400',
    'bg-green-400',
    'bg-yellow-400',
    'bg-red-400',
  ];

  return colors[
    index % colors.length
  ];
}