import { useEffect, useRef, useState } from 'react';
import { Modal } from 'antd';
import {
  ScissorOutlined,
  ReloadOutlined,
  RotateRightOutlined,
  ZoomInOutlined,
  ZoomOutOutlined,
} from '@ant-design/icons';
import { backendUrl } from '../../api/base';
import type { ScanFile } from './types';

interface PreviewModalProps {
  file: ScanFile | null;
  zoom: number;
  onZoomChange: (zoom: number) => void;
  onCrop: (file: ScanFile, position?: [number, number, number, number]) => void;
  onRotate: (file: ScanFile) => void;
  onClose: () => void;
}

export default function PreviewModal({
  file,
  zoom,
  onZoomChange,
  onCrop,
  onRotate,
  onClose,
}: PreviewModalProps) {
  const imageRef = useRef<HTMLImageElement | null>(null);
  const [isManualCrop, setIsManualCrop] = useState(false);
  const [selection, setSelection] = useState<{
    topRight: { x: number; y: number };
    bottomLeft: { x: number; y: number };
  } | null>(null);
  const [draggingPoint, setDraggingPoint] = useState<'topRight' | 'bottomLeft' | null>(null);

  useEffect(() => {
    setIsManualCrop(false);
    setSelection(null);
  }, [file]);

  const getImagePoint = (event: React.PointerEvent<HTMLElement>) => {
    const image = imageRef.current;
    if (!image) return null;
    const bounds = image.getBoundingClientRect();
    return {
      x: Math.max(0, Math.min(bounds.width, event.clientX - bounds.left)),
      y: Math.max(0, Math.min(bounds.height, event.clientY - bounds.top)),
    };
  };

  const getSelectionStyle = () => {
    if (!selection) return undefined;
    return {
      left: selection.bottomLeft.x,
      top: selection.topRight.y,
      width: selection.topRight.x - selection.bottomLeft.x,
      height: selection.bottomLeft.y - selection.topRight.y,
    };
  };

  const handleManualCrop = () => {
    if (!file || !selection || !imageRef.current) return;
    const image = imageRef.current;
    const bounds = image.getBoundingClientRect();
    const left = selection.bottomLeft.x;
    const top = selection.topRight.y;
    const right = selection.topRight.x;
    const bottom = selection.bottomLeft.y;
    const position: [number, number, number, number] = [
      Math.round(left * image.naturalWidth / bounds.width),
      Math.round(top * image.naturalHeight / bounds.height),
      Math.round(right * image.naturalWidth / bounds.width),
      Math.round(bottom * image.naturalHeight / bounds.height),
    ];
    if (position[2] <= position[0] || position[3] <= position[1]) return;
    onCrop(file, position);
    onClose();
  };

  return (
    <Modal
      open={file !== null}
      footer={null}
      centered
      width="90vw"
      onCancel={onClose}
      title="Xem chi tiết page"
    >
      {file && (
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-center gap-2">
            <button
              type="button"
              onClick={() => onZoomChange(Math.max(0.5, zoom - 0.25))}
              className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-600 transition hover:bg-slate-100"
              title="Thu nhỏ"
              aria-label="Thu nhỏ ảnh"
            >
              <ZoomOutOutlined />
            </button>
            <span className="min-w-16 text-center text-sm font-semibold text-slate-600">
              {Math.round(zoom * 100)}%
            </span>
            <button
              type="button"
              onClick={() => onZoomChange(Math.min(4, zoom + 0.25))}
              className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-600 transition hover:bg-slate-100"
              title="Phóng to"
              aria-label="Phóng to ảnh"
            >
              <ZoomInOutlined />
            </button>
            <button
              type="button"
              onClick={() => onZoomChange(1)}
              className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-600 transition hover:bg-slate-100"
              title="Đặt lại kích thước"
              aria-label="Đặt lại kích thước ảnh"
            >
              <ReloadOutlined />
            </button>
            <button
              type="button"
              onClick={() => onRotate(file)}
              className="inline-flex h-9 items-center justify-center gap-1 rounded-lg border border-slate-200 px-3 text-sm font-medium text-slate-600 transition hover:bg-slate-100"
              title="Xoay ảnh 90 độ theo chiều kim đồng hồ và lưu vào file gốc"
              aria-label="Xoay ảnh 90 độ theo chiều kim đồng hồ"
            >
              <RotateRightOutlined />
              Xoay phải
            </button>
            <button
              type="button"
              onClick={() => {
                if (file) {
                  onCrop(file);
                  onClose();
                }
              }}
              className="inline-flex h-9 items-center justify-center gap-1 rounded-lg border border-slate-200 px-3 text-sm font-medium text-slate-600 transition hover:bg-slate-100"
              title="Căt tự động ảnh này"
              aria-label="Cắt tự động ảnh này"
            >
              <ScissorOutlined />
              Cắt tự động
            </button>
            <button
              type="button"
              onClick={() => {
                setIsManualCrop(true);
                const image = imageRef.current;
                if (image) {
                  const bounds = image.getBoundingClientRect();
                  setSelection({
                    topRight: { x: bounds.width * 0.9, y: bounds.height * 0.1 },
                    bottomLeft: { x: bounds.width * 0.1, y: bounds.height * 0.9 },
                  });
                }
              }}
              className={`inline-flex h-9 items-center justify-center gap-1 rounded-lg border px-3 text-sm font-medium transition ${isManualCrop ? 'border-[#28a9a9] bg-[#e8f8f7] text-[#168888]' : 'border-slate-200 text-slate-600 hover:bg-slate-100'}`}
              title="Chọn vùng để cắt thủ công"
              aria-label="Chọn vùng để cắt thủ công"
            >
              <ScissorOutlined />
              Cắt thủ công
            </button>
            {isManualCrop && (
              <>
                <button
                  type="button"
                  onClick={handleManualCrop}
                  disabled={!selection}
                  className="inline-flex h-9 items-center justify-center gap-1 rounded-lg bg-[#28a9a9] px-3 text-sm font-medium text-white transition hover:bg-[#219a9a] disabled:cursor-not-allowed disabled:opacity-40"
                  title="Gửi vùng đã chọn để cắt"
                >
                  Xác nhận vùng cắt
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const image = imageRef.current;
                    if (image) {
                      const bounds = image.getBoundingClientRect();
                      setSelection({
                        topRight: { x: bounds.width * 0.9, y: bounds.height * 0.1 },
                        bottomLeft: { x: bounds.width * 0.1, y: bounds.height * 0.9 },
                      });
                    }
                  }}
                  className="inline-flex h-9 items-center justify-center rounded-lg border border-slate-200 px-3 text-sm font-medium text-slate-600 transition hover:bg-slate-100"
                  title="Chọn lại vùng cắt"
                >
                  Chọn lại
                </button>
              </>
            )}
          </div>

          {isManualCrop && (
            <p className="text-center text-sm text-slate-500">
              Kéo chấm trên-phải và dưới-trái để chọn vùng cần cắt.
            </p>
          )}

          <div className="relative max-h-[70vh] overflow-auto rounded-xl bg-slate-100 p-3 text-center">
            <div className="relative mx-auto w-fit leading-[0]">
              <img
                ref={imageRef}
                src={`${backendUrl}${file.link}`}
                alt="Xem chi tiết scanned file"
                className={`h-auto max-w-none origin-top object-contain transition-transform duration-200 ${isManualCrop ? 'cursor-crosshair' : ''}`}
                draggable={false}
                style={{ width: `${zoom * 100}%` }}
              />
              {isManualCrop && selection && (
                <>
                  <div className="pointer-events-none absolute border-2 border-[#28a9a9] bg-[#28a9a9]/20" style={getSelectionStyle()} />
                  {(['topRight', 'bottomLeft'] as const).map(pointName => {
                    const point = selection[pointName];
                    return (
                      <button
                        key={pointName}
                        type="button"
                        aria-label={pointName === 'topRight' ? 'Điểm góc trên phải' : 'Điểm góc dưới trái'}
                        className="absolute z-10 h-5 w-5 -translate-x-1/2 -translate-y-1/2 cursor-move rounded-full border-2 border-white bg-[#168888] shadow-md touch-none"
                        style={{ left: point.x, top: point.y }}
                        onPointerDown={event => {
                          event.preventDefault();
                          event.stopPropagation();
                          event.currentTarget.setPointerCapture(event.pointerId);
                          setDraggingPoint(pointName);
                        }}
                        onPointerMove={event => {
                          if (draggingPoint !== pointName || !imageRef.current) return;
                          const nextPoint = getImagePoint(event);
                          if (!nextPoint) return;
                          const bounds = imageRef.current.getBoundingClientRect();
                          const minimumSize = 8;
                          setSelection(previous => {
                            if (!previous) return previous;
                            if (pointName === 'topRight') {
                              return {
                                ...previous,
                                topRight: {
                                  x: Math.max(previous.bottomLeft.x + minimumSize, Math.min(bounds.width, nextPoint.x)),
                                  y: Math.max(0, Math.min(previous.bottomLeft.y - minimumSize, nextPoint.y)),
                                },
                              };
                            }
                            return {
                              ...previous,
                              bottomLeft: {
                                x: Math.max(0, Math.min(previous.topRight.x - minimumSize, nextPoint.x)),
                                y: Math.max(previous.topRight.y + minimumSize, Math.min(bounds.height, nextPoint.y)),
                              },
                            };
                          });
                        }}
                        onPointerUp={event => {
                          if (draggingPoint !== pointName) return;
                          event.currentTarget.releasePointerCapture(event.pointerId);
                          setDraggingPoint(null);
                        }}
                        onPointerCancel={() => setDraggingPoint(null)}
                      />
                    );
                  })}
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </Modal>
  );
}
