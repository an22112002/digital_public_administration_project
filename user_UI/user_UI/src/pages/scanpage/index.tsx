import { useState, useEffect, useRef } from 'react';
import Header from '../../header/header';
import aiBootsImage from '../../assets/ai boots.png';
import { useParams } from 'react-router-dom';
import { getScannerOptions } from '../../api/scannerAPI';
import type { ScannerOption } from '../../api/scannerAPI';
import { Modal } from 'antd';
import {
  ArrowDownOutlined,
  FilePdfOutlined,
  ScanOutlined,
  ArrowRightOutlined,
} from "@ant-design/icons";
import { websocketUrl } from '../../api/base';
import AddDocumentModal from '../../components/scanpage/AddDocumentModal';
import DocumentList from '../../components/scanpage/DocumentList';
import PreviewModal from '../../components/scanpage/PreviewModal';
import ScannedFiles from '../../components/scanpage/ScannedFiles';
import type { DocumentItem, ScanFile, SendFile } from '../../components/scanpage/types';

export default function ScanPage({ kiosk = false }: { kiosk?: boolean }) {
  const websocket = useRef<WebSocket | null>(null);
  const fileInput = useRef<HTMLInputElement | null>(null);

  const { serviceID } = useParams<{ serviceID: string }>();

  console.log('Service ID:', serviceID);

  // =========================================================
  // STATE
  // =========================================================

  const [serviceName, setServiceName] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [scannedFiles, setScannedFiles] = useState<ScanFile[]>([]);
  const [deletedFileUrls, setDeletedFileUrls] = useState<string[]>([]);

  // Chỉ lưu ID của document đang focus
  const [focusDocumentId, setFocusDocumentId] = useState<string | null>(
    null
  );

  const [scannerOptions, setScannerOptions] =
    useState<ScannerOption[]>([]);

  const [selectedScannerId, setSelectedScannerId] =
    useState('');

  const [actionHint, setActionHint] = useState<'scan' | 'import' | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);

  const [isInProcess, setIsInProcess] = useState(false);

  const [previewFile, setPreviewFile] = useState<ScanFile | null>(null);

  const [previewZoom, setPreviewZoom] = useState(1);

  const [selectedSupplementalDocumentIds, setSelectedSupplementalDocumentIds] =
    useState<string[]>([]);

  const [scanError, setScanError] = useState<string | null>(null);

  const [processError, setProcessError] = useState<string | null>(null);

  const extensionDocumentTypes = [
    'Căn cước công dân',
    'Giấy phép lái xe',
    'Thẻ bảo hiểm y tế',
  ];

  const [newExtensionDocumentTypes, setNewExtensionDocumentTypes] = useState<string>();

  const supplementalDocuments = documents.filter(
    doc =>
      !doc.required &&
      !doc.srID.startsWith('ADD:') &&
      !selectedSupplementalDocumentIds.includes(doc.srID)
  );

  const visibleDocuments = documents.filter(
    doc =>
      doc.required ||
      selectedSupplementalDocumentIds.includes(doc.srID)
  );

  useEffect(() => {
    if (processError) {
      setIsInProcess(false);
    }
  }, [processError]);

  // Document đang được chọn
  const focusDocument =
    documents.find(doc => doc.srID === focusDocumentId) ?? null;

  const visibleScannedFiles = scannedFiles.filter(
    file => !deletedFileUrls.includes(file.url)
  );

  // =========================================================
  // WEBSOCKET RECEIVE
  // =========================================================

  const handleWebSocketReceive = (data: any) => {
    if (data['code'] === '0') {
      // Load danh sách document lần đầu
      setServiceName(data["service"]["title"] ?? null);
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
        const firstVisibleDocument =
          newDocuments.find(doc => doc.required) ??
          newDocuments[0];

        setFocusDocumentId(firstVisibleDocument.srID);
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

    const isCropMessage = data['type'] === 'crop_status';

    if (isCropMessage) {
      if (data['status'] === 'error' || data['error']) {
        setProcessError(String(data['message'] ?? data['error'] ?? 'Không thể crop ảnh'));
        return;
      }

      const croppedImages: ScanFile[] = (data['cropped_images'] ?? [])
        .map((imagePath: string) => createScanFileFromPath(imagePath))
        .filter((file: ScanFile | null): file is ScanFile => file !== null);
      if (croppedImages.length > 0) {
        setScannedFiles(previousFiles => {
          const existingUrls = new Set(previousFiles.map(file => file.url));
          return [
            ...previousFiles,
            ...croppedImages.filter(file => !existingUrls.has(file.url)),
          ];
        });
      }
      return;
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

    setSelectedSupplementalDocumentIds(prev => [
      ...prev,
      newDocumentItem.srID,
    ]);

    // Focus document mới
    setFocusDocumentId(newDocumentItem.srID);

    setIsModalOpen(false);

    setNewExtensionDocumentTypes("");
  };

  const handleSelectSupplementalDocument = (srID: string) => {
    setSelectedSupplementalDocumentIds(prev =>
      prev.includes(srID) ? prev : [...prev, srID]
    );
    setFocusDocumentId(srID);
    setIsModalOpen(false);
  };

  const openFilePreview = (file: ScanFile) => {
    setPreviewFile(file);
    setPreviewZoom(1);
  };

  const closeFilePreview = () => {
    setPreviewFile(null);
    setPreviewZoom(1);
  };

  const handleCropFile = (file: ScanFile) => {
    const ws = websocket.current;

    if (ws?.readyState !== WebSocket.OPEN) {
      setProcessError('WebSocket chưa kết nối');
      return;
    }

    setProcessError(null);
    ws.send(JSON.stringify({
      type: 'crop_image',
      request: {
        image: file.url,
      },
    }));
  };

  // =========================================================
  // START SCAN
  // =========================================================

  const startScan = () => {
    setActionHint(null);

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
      alert('Có tài liệu bắt buộc chưa có file');

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
    setActionHint(null);

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

  const handleDeleteFile = (file: ScanFile) => {
    setDeletedFileUrls(previousUrls =>
      previousUrls.includes(file.url)
        ? previousUrls
        : [...previousUrls, file.url]
    );

    setDocuments(previousDocuments =>
      previousDocuments.map(document => ({
        ...document,
        files: (document.files ?? []).filter(fileUrl => fileUrl !== file.url),
      }))
    );

    if (previewFile?.url === file.url) {
      closeFilePreview();
    }
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
        setActionHint(options.length > 0 ? 'scan' : 'import');

        if (data.default?.id) {
          setSelectedScannerId(data.default.id);
          return;
        }

        if (options.length > 0) {
          setSelectedScannerId(options[0].id);
        }
      } catch (error) {
        setActionHint('import');
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
      `${websocketUrl}/process/service/${serviceID}`
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
    <div className="min-h-screen bg-[#fff7f0] px-4 py-8 text-slate-800">
      <Modal 
        open={isInProcess} footer={null} closable={false} centered>
        <div className="flex flex-col items-center gap-4">
          <svg
            className="h-12 w-12 animate-spin text-[#bd2517]"
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

        {kiosk && (
          <section className="kiots-scan-ai" aria-label="Trợ lý AI hỗ trợ dịch vụ công">
            <img src={aiBootsImage} alt="Trợ lý AI hỗ trợ dịch vụ công" />
          </section>
        )}

        {serviceName && (
          <div className="px-6">
            Dịch vụ: <span className="font-semibold">{serviceName}</span>
          </div>
        )}

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

        <main className="rounded-[30px] bg-white p-5 shadow-[0_30px_70px_rgba(146,21,7,0.1)] ring-1 ring-[#f7c7b5] md:p-8">

          <div className="flex flex-col gap-4 border-t border-slate-200 pb-5 sm:flex-row sm:items-center sm:justify-between">

            {/* SCANNER */}

            <div className="flex items-center gap-3 justify-center rounded-[16px] bg-[#bd2517] px-6 py-4 text-sm font-medium text-white shadow-[0_12px_30px_rgba(189,37,23,0.3)] transition hover:bg-[#a51f13] sm:justify-start">

              <label
                className="text-sm font-lg text-white"
                htmlFor="scanner-select"
              >
                CHỌN MÁY QUÉT
              </label>

              <select
                id="scanner-select"
                value={selectedScannerId}
                onChange={event =>
                  setSelectedScannerId(
                    event.target.value
                  )
                }
                className="rounded-xl border border-[#f2c7b8] bg-white px-3 py-2.5 text-sm font-medium text-slate-700 shadow-sm outline-none transition focus:border-[#bd2517]"
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

              <div className="relative">
                {actionHint === 'import' && (
                  <ArrowDownOutlined
                    className="absolute -top-8 left-0 right-0 z-10 mx-auto w-fit animate-bounce text-2xl text-[#e63a12]"
                    aria-label="Mũi tên hướng dẫn nộp file"
                  />
                )}
                <button
                  type="button"
                  className="inline-flex items-center justify-center rounded-[16px] bg-[#e63a12] px-8 py-3.5 text-base font-semibold text-white shadow-[0_12px_30px_rgba(230,58,18,0.28)] transition hover:bg-[#c92f0d]"
                  onClick={() => {
                    setActionHint(null);
                    fileInput.current?.click();
                  }}
                >
                  <FilePdfOutlined />&nbsp;
                  Nộp file
                </button>
              </div>

              <div className="relative">
                {actionHint === 'scan' && (
                  <ArrowDownOutlined
                    className="absolute -top-8 left-0 right-0 z-10 mx-auto w-fit animate-bounce text-2xl text-[#bd2517]"
                    aria-label="Mũi tên hướng dẫn quét"
                  />
                )}
                <button
                  type="button"
                  className="inline-flex items-center justify-center rounded-[16px] bg-[#bd2517] px-8 py-3.5 text-base font-semibold text-white shadow-[0_12px_30px_rgba(189,37,23,0.3)] transition hover:bg-[#a51f13]"
                  onClick={startScan}
                >
                  <ScanOutlined />&nbsp;
                  Quét
                </button>
              </div>

              <button
                type="button"
                className="inline-flex items-center justify-center rounded-[16px] bg-[#921507] px-8 py-3.5 text-base font-semibold text-white shadow-[0_12px_30px_rgba(146,21,7,0.3)] transition hover:bg-[#781105]"
                onClick={
                  handleSubmitDocuments
                }
              >
                <ArrowRightOutlined />&nbsp;
                Nộp hồ sơ
              </button>

            </div>

          </div>
          {/* ================================================= */}
          {/* FILE + DOCUMENT */}
          {/* ================================================= */}
          <div className="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">

            {/* ================================================= */}
            {/* SCANNED FILES */}
            {/* ================================================= */}

            <ScannedFiles
              files={visibleScannedFiles}
              selectedFileUrls={focusDocument?.files ?? []}
              selectedFileColor={focusDocument?.color ?? null}
              onSelectFile={handleSetFileSelectForDocument}
              onDeleteFile={handleDeleteFile}
              onPreviewFile={openFilePreview}
            />

            {/* ================================================= */}
            {/* DOCUMENTS */}
            {/* ================================================= */}

            <DocumentList
              documents={visibleDocuments}
              scannedFiles={visibleScannedFiles}
              focusDocumentId={focusDocumentId}
              onSelectDocument={setFocusDocumentId}
              onOpenAddDocument={() => setIsModalOpen(true)}
            />

          </div>

        </main>

      </div>

      <PreviewModal
        file={previewFile}
        zoom={previewZoom}
        onZoomChange={setPreviewZoom}
        onCrop={handleCropFile}
        onClose={closeFilePreview}
      />

      <AddDocumentModal
        open={isModalOpen}
        supplementalTitles={supplementalDocuments}
        extensionDocumentTypes={extensionDocumentTypes}
        newDocumentType={newExtensionDocumentTypes}
        onClose={() => setIsModalOpen(false)}
        onSelectSupplemental={handleSelectSupplementalDocument}
        onAddDocument={handleAddDocument}
        onNewDocumentTypeChange={setNewExtensionDocumentTypes}
      />

    </div>
  );
}

// =========================================================
// GET DOCUMENT COLOR
// =========================================================

function getFileColorFromIndex(
  index: number
): string {
  // màu sáng, nổi bật, dễ phân biệt, không quá chói
  const colors = [
    'bg-blue-700',
    'bg-purple-700',
    'bg-pink-700',
    'bg-orange-700',
    'bg-green-700',
    'bg-yellow-700',
    'bg-red-700',
  ];

  return colors[
    index % colors.length
  ];
}

function createScanFileFromPath(
  imagePath: string
): ScanFile | null {
  const normalizedPath = imagePath.replace(/\\/g, '/');
  const match = normalizedPath.match(/\/patch_([^/]+)\/images\/([^/]+)$/);

  if (!match) {
    console.error('Đường dẫn ảnh crop không hợp lệ:', imagePath);
    return null;
  }

  return {
    url: imagePath,
    link: `/scanned-files/patch_${match[1]}/images/${match[2]}`,
  };
}