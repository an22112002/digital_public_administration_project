import { useEffect, useRef, useState } from 'react';
import { useLocation } from 'react-router-dom';
import homeAudio from '../assets/audio/1.mp3';
import scanAudio from '../assets/audio/2.mp3';
import scannedAudio from '../assets/audio/3.mp3';
import followUpAudio from '../assets/audio/4.mp3';

const SCAN_AUDIO_COMPLETE_EVENT = 'hub:scan-audio-complete';

/**
 * Báo cho UserAudioGuide rằng lượt quét hiện tại đã hoàn tất.
 *
 * Cách dùng:
 * 1. Render <UserAudioGuide /> một lần ở cấp router/layout, bên trong
 *    BrowserRouter để component có thể đọc pathname hiện tại.
 * 2. Tại nơi nhận được kết quả quét thành công, gọi
 *    notifyScanAudioComplete().
 *
 * Component sẽ chuyển từ audio hướng dẫn quét (track 2) sang audio đã quét
 * (track 3). Audio được thử phát một lần sau 4 giây kể từ khi tải trang.
 * Nếu trình duyệt chặn autoplay, thao tác click hoặc nhấn phím đầu tiên sẽ
 * mở khóa lần phát duy nhất đó.
 */
export function notifyScanAudioComplete() {
  window.dispatchEvent(new Event(SCAN_AUDIO_COMPLETE_EVENT));
}

/**
 * Audio guide dùng chung cho các trang /desktop và /kiosk.
 *
 * Component không hiển thị giao diện; chỉ quản lý một thẻ <audio> và tự chọn
 * nội dung dựa trên pathname:
 * - Trang chủ: track 1.
 * - Trang scan trước khi quét xong: track 2.
 * - Sau khi gọi notifyScanAudioComplete(): track 3.
 * Audio không tự phát lại khi route, trạng thái quét hoặc source thay đổi.
 * Thời gian chờ 4 giây giúp trang hoàn tất tải trước lần phát đầu tiên.
 */
export default function UserAudioGuide() {
  const { pathname } = useLocation();
  const audioRef = useRef<HTMLAudioElement>(null);
  const hasStartedRef = useRef(false);
  const revisionRef = useRef(0);
  const [scanCompletion, setScanCompletion] = useState<{
    pathname: string;
    revision: number;
  } | null>(null);

  const isScanPage = /^\/(desktop|kiosk)\/scan\/[^/]+/.test(pathname);
  const completedOnCurrentPage = scanCompletion?.pathname === pathname;
  const currentTrack = !isScanPage
    ? 1
    : completedOnCurrentPage
      ? 3
      : 2;
  const currentSource = [homeAudio, scanAudio, scannedAudio, followUpAudio][currentTrack - 1];

  useEffect(() => {
    setScanCompletion(null);
  }, [pathname]);

  useEffect(() => {
    const handleScanComplete = () => {
      if (!isScanPage) return;

      setScanCompletion({ pathname, revision: ++revisionRef.current });
    };

    window.addEventListener(SCAN_AUDIO_COMPLETE_EVENT, handleScanComplete);
    return () => window.removeEventListener(SCAN_AUDIO_COMPLETE_EVENT, handleScanComplete);
  }, [isScanPage, pathname]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const playOnce = () => {
      if (hasStartedRef.current) return;

      void audio.play()
        .then(() => {
          hasStartedRef.current = true;
        })
        .catch(() => {
          // Autoplay may require a user gesture; the listeners below retry once.
        });
    };
    const playTimer = window.setTimeout(() => {
      playOnce();
    }, 4_000);
    const unlockAudio = () => playOnce();

    window.addEventListener('pointerdown', unlockAudio, true);
    window.addEventListener('keydown', unlockAudio, true);

    return () => {
      window.clearTimeout(playTimer);
      window.removeEventListener('pointerdown', unlockAudio, true);
      window.removeEventListener('keydown', unlockAudio, true);
      audio.pause();
    };
  }, []);

  return <audio ref={audioRef} src={currentSource} preload="auto" />;
}