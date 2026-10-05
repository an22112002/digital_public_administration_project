import { useEffect, useRef, useState } from 'react';
import { useLocation } from 'react-router-dom';
import homeAudio from '../assets/audio/1.mp3';
import scanAudio from '../assets/audio/2.mp3';
import scannedAudio from '../assets/audio/3.mp3';
import followUpAudio from '../assets/audio/4.mp3';

const SCAN_AUDIO_COMPLETE_EVENT = 'hub:scan-audio-complete';

export function notifyScanAudioComplete() {
  window.dispatchEvent(new Event(SCAN_AUDIO_COMPLETE_EVENT));
}

export default function UserAudioGuide() {
  const { pathname } = useLocation();
  const audioRef = useRef<HTMLAudioElement>(null);
  const delayTimerRef = useRef<number | null>(null);
  const revisionRef = useRef(0);
  const [scanCompletion, setScanCompletion] = useState<{
    pathname: string;
    revision: number;
  } | null>(null);
  const [followUpPathname, setFollowUpPathname] = useState<string | null>(null);

  const isScanPage = /^\/(desktop|kiosk)\/scan\/[^/]+/.test(pathname);
  const isHomePage = /^\/(desktop|kiosk)\/?$/.test(pathname);
  const completedOnCurrentPage = scanCompletion?.pathname === pathname;
  const currentTrack = !isScanPage
    ? 1
    : followUpPathname === pathname
      ? 4
      : completedOnCurrentPage
        ? 3
        : 2;
  const currentSource = [homeAudio, scanAudio, scannedAudio, followUpAudio][currentTrack - 1];

  useEffect(() => {
    if (delayTimerRef.current !== null) {
      window.clearTimeout(delayTimerRef.current);
      delayTimerRef.current = null;
    }
    setScanCompletion(null);
    setFollowUpPathname(null);

    return () => {
      if (delayTimerRef.current !== null) {
        window.clearTimeout(delayTimerRef.current);
        delayTimerRef.current = null;
      }
    };
  }, [pathname]);

  useEffect(() => {
    const handleScanComplete = () => {
      if (!isScanPage) return;

      if (delayTimerRef.current !== null) {
        window.clearTimeout(delayTimerRef.current);
        delayTimerRef.current = null;
      }

      setFollowUpPathname(null);
      setScanCompletion({ pathname, revision: ++revisionRef.current });
    };

    window.addEventListener(SCAN_AUDIO_COMPLETE_EVENT, handleScanComplete);
    return () => window.removeEventListener(SCAN_AUDIO_COMPLETE_EVENT, handleScanComplete);
  }, [isScanPage, pathname]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    audio.pause();
    audio.currentTime = 0;
    void audio.play().catch(() => undefined);

    return () => audio.pause();
  }, [currentSource, currentTrack, completedOnCurrentPage ? scanCompletion?.revision : 0]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handlePointerDown = () => {
      if (isHomePage) {
        audio.pause();
        audio.currentTime = 0;
      } else if (!audio.paused) {
        return;
      }
      void audio.play().catch(() => undefined);
    };
    const unlockAudio = () => {
      if (audio.paused) void audio.play().catch(() => undefined);
    };

    window.addEventListener('pointerdown', handlePointerDown, true);
    window.addEventListener('keydown', unlockAudio, true);

    return () => {
      window.removeEventListener('pointerdown', handlePointerDown, true);
      window.removeEventListener('keydown', unlockAudio, true);
    };
  }, [isHomePage]);

  const handleAudioEnded = () => {
    if (currentTrack !== 3) return;

    delayTimerRef.current = window.setTimeout(() => {
      setFollowUpPathname(pathname);
      delayTimerRef.current = null;
    }, 60_000);
  };

  return <audio ref={audioRef} src={currentSource} preload="auto" onEnded={handleAudioEnded} />;
}