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
    startX: number;
    startY: number;
    endX: number;
    endY: number;
  } | null>(null);
  const [isSelecting, setIsSelecting] = useState(false);
  const [touchCropStep, setTouchCropStep] = useState<0 | 1 | 2>(0);

  useEffect(() => {
    setIsManualCrop(false);
    setSelection(null);
    setIsSelecting(false);
    setTouchCropStep(0);
  }, [file]);

  const getImagePoint = (event: React.PointerEvent<HTMLImageElement>) => {
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
      left: Math.min(selection.startX, selection.endX),
      top: Math.min(selection.startY, selection.endY),
      width: Math.abs(selection.endX - selection.startX),
      height: Math.abs(selection.endY - selection.startY),
    };
  };

  const handleManualCrop = () => {
    if (!file || !selection || !imageRef.current) return;
    const image = imageRef.current;
    const bounds = image.getBoundingClientRect();
    const left = Math.min(selection.startX, selection.endX);
    const top = Math.min(selection.startY, selection.endY);
    const right = Math.max(selection.startX, selection.endX);
    const bottom = Math.max(selection.startY, selection.endY);
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
                setSelection(null);
                setTouchCropStep(0);
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
                  disabled={!selection || touchCropStep === 1}
                  className="inline-flex h-9 items-center justify-center gap-1 rounded-lg bg-[#28a9a9] px-3 text-sm font-medium text-white transition hover:bg-[#219a9a] disabled:cursor-not-allowed disabled:opacity-40"
                  title="Gửi vùng đã chọn để cắt"
                >
                  Xác nhận vùng cắt
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setSelection(null);
                    setTouchCropStep(0);
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
              Trên màn hình cảm ứng: chạm góc trên-trái, sau đó chạm góc dưới-phải của vùng cần cắt.
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
                style={{ width: `${zoom * 100}%`, touchAction: isManualCrop ? 'none' : 'auto' }}
                onPointerDown={event => {
                  if (!isManualCrop) return;
                  const point = getImagePoint(event);
                  if (!point) return;

                  if (event.pointerType === 'touch') {
                    if (touchCropStep === 0 || touchCropStep === 2) {
                      setSelection({ startX: point.x, startY: point.y, endX: point.x, endY: point.y });
                      setTouchCropStep(1);
                    } else {
                      setSelection(previous => previous ? { ...previous, endX: point.x, endY: point.y } : null);
                      setTouchCropStep(2);
                    }
                    return;
                  }

                  event.currentTarget.setPointerCapture(event.pointerId);
                  setIsSelecting(true);
                  setSelection({ startX: point.x, startY: point.y, endX: point.x, endY: point.y });
                }}
                onPointerMove={event => {
                  if (!isSelecting) return;
                  const point = getImagePoint(event);
                  if (!point) return;
                  setSelection(previous => previous ? { ...previous, endX: point.x, endY: point.y } : null);
                }}
                onPointerUp={event => {
                  if (!isSelecting) return;
                  event.currentTarget.releasePointerCapture(event.pointerId);
                  setIsSelecting(false);
                }}
              />
              {isManualCrop && selection && (
                <div className="pointer-events-none absolute border-2 border-[#28a9a9] bg-[#28a9a9]/20" style={getSelectionStyle()} />
              )}
            </div>
          </div>
        </div>
      )}
    </Modal>
  );
}
