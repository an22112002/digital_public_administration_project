import { useEffect, useRef, useState } from 'react';
import { Modal } from 'antd';
import {
  ScissorOutlined,
  ReloadOutlined,
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
  onClose: () => void;
}

interface Selection {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
}

export default function PreviewModal({
  file,
  zoom,
  onZoomChange,
  onCrop,
  onClose,
}: PreviewModalProps) {
  const imageRef = useRef<HTMLImageElement | null>(null);
  const [isManualCrop, setIsManualCrop] = useState(false);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [isSelecting, setIsSelecting] = useState(false);

  useEffect(() => {
    setIsManualCrop(false);
    setSelection(null);
    setIsSelecting(false);
  }, [file]);

  const getImagePoint = (event: React.PointerEvent<HTMLImageElement>) => {
    const image = imageRef.current;
    if (!image) {
      return null;
    }

    const bounds = image.getBoundingClientRect();
    return {
      x: Math.max(0, Math.min(bounds.width, event.clientX - bounds.left)),
      y: Math.max(0, Math.min(bounds.height, event.clientY - bounds.top)),
    };
  };

  const getSelectionStyle = () => {
    if (!selection) {
      return undefined;
    }

    return {
      left: Math.min(selection.startX, selection.endX),
      top: Math.min(selection.startY, selection.endY),
      width: Math.abs(selection.endX - selection.startX),
      height: Math.abs(selection.endY - selection.startY),
    };
  };

  const handleManualCrop = () => {
    if (!file || !selection || !imageRef.current) {
      return;
    }

    const image = imageRef.current;
    const bounds = image.getBoundingClientRect();
    const left = Math.min(selection.startX, selection.endX);
    const top = Math.min(selection.startY, selection.endY);
    const right = Math.max(selection.startX, selection.endX);
    const bottom = Math.max(selection.startY, selection.endY);
    const scaleX = image.naturalWidth / bounds.width;
    const scaleY = image.naturalHeight / bounds.height;
    const position: [number, number, number, number] = [
      Math.round(left * scaleX),
      Math.round(top * scaleY),
      Math.round(right * scaleX),
      Math.round(bottom * scaleY),
    ];

    if (position[2] <= position[0] || position[3] <= position[1]) {
      return;
    }

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
              onClick={() => {
                if (file) {
                  onCrop(file);
                  onClose();
                }
              }}
              className="inline-flex h-9 items-center justify-center gap-1 rounded-lg border border-slate-200 px-3 text-sm font-medium text-slate-600 transition hover:bg-slate-100"
              title="Tự động cắt ảnh này"
              aria-label="Tự động cắt ảnh này"
            >
              <ScissorOutlined />
              Tự động cắt
            </button>
            <button
              type="button"
              onClick={() => {
                setIsManualCrop(true);
                setSelection(null);
              }}
              className={`inline-flex h-9 items-center justify-center gap-1 rounded-lg border px-3 text-sm font-medium transition ${isManualCrop
                ? 'border-[#28a9a9] bg-[#e8f8f7] text-[#168888]'
                : 'border-slate-200 text-slate-600 hover:bg-slate-100'
                }`}
              title="Cắt thủ công ảnh này"
              aria-label="Cắt thủ công ảnh này"
            >
              <ScissorOutlined />
              Cắt thủ công
            </button>
            {isManualCrop && (
              <button
                type="button"
                onClick={handleManualCrop}
                disabled={!selection}
                className="inline-flex h-9 items-center justify-center gap-1 rounded-lg bg-[#28a9a9] px-3 text-sm font-medium text-white transition hover:bg-[#219a9a] disabled:cursor-not-allowed disabled:opacity-40"
                title="Gửi vùng đã chọn để cắt"
              >
                Xác nhận vùng cắt
              </button>
            )}
          </div>

          <div className="relative max-h-[70vh] overflow-auto rounded-xl bg-slate-100 p-3 text-center">
            <div className="relative mx-auto w-fit leading-[0]">
              <img
                ref={imageRef}
                src={`${backendUrl}${file.link}`}
                alt="Xem chi tiết scanned file"
                className={`h-auto max-w-none origin-top object-contain transition-transform duration-200 ${isManualCrop ? 'cursor-crosshair' : ''}`}
                style={{ width: `${zoom * 100}%` }}
                draggable={false}
                onPointerDown={event => {
                  if (!isManualCrop) {
                    return;
                  }
                  const point = getImagePoint(event);
                  if (!point) {
                    return;
                  }
                  event.currentTarget.setPointerCapture(event.pointerId);
                  setIsSelecting(true);
                  setSelection({
                    startX: point.x,
                    startY: point.y,
                    endX: point.x,
                    endY: point.y,
                  });
                }}
                onPointerMove={event => {
                  if (!isSelecting) {
                    return;
                  }
                  const point = getImagePoint(event);
                  if (!point || !selection) {
                    return;
                  }
                  setSelection(previous => previous
                    ? { ...previous, endX: point.x, endY: point.y }
                    : null);
                }}
                onPointerUp={event => {
                  if (isSelecting) {
                    event.currentTarget.releasePointerCapture(event.pointerId);
                    setIsSelecting(false);
                  }
                }}
              />
              {isManualCrop && selection && (
                <div
                  className="pointer-events-none absolute border-2 border-[#28a9a9] bg-[#28a9a9]/20"
                  style={getSelectionStyle()}
                />
              )}
            </div>
          </div>
        </div>
      )}
    </Modal>
  );
}