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
  onCrop: (file: ScanFile) => void;
  onClose: () => void;
}

export default function PreviewModal({
  file,
  zoom,
  onZoomChange,
  onCrop,
  onClose,
}: PreviewModalProps) {
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
              title="Crop ảnh này"
              aria-label="Crop ảnh này"
            >
              <ScissorOutlined />
              Crop
            </button>
          </div>

          <div className="relative max-h-[70vh] overflow-auto rounded-xl bg-slate-100 p-3 text-center">
            <img
              src={`${backendUrl}${file.link}`}
              alt="Xem chi tiết scanned file"
              className="mx-auto h-auto max-w-none origin-top object-contain transition-transform duration-200"
              style={{ width: `${zoom * 100}%` }}
            />
          </div>
        </div>
      )}
    </Modal>
  );
}