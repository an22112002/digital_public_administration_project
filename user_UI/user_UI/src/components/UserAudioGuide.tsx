import { useEffect, useRef, useState } from 'react';
import { useLocation } from 'react-router-dom';
import homeAudio from '../assets/audio/1.mp3';
import scanAudio from '../assets/audio/2.mp3';
import scannedAudio from '../assets/audio/3.mp3';

const SCAN_AUDIO_COMPLETE_EVENT = 'hub:scan-audio-complete';

export function notifyScanAudioComplete() {
  window.dispatchEvent(new Event(SCAN_AUDIO_COMPLETE_EVENT));
}

export default function UserAudioGuide() {
  const { pathname } = useLocation();
  const audioRef = useRef<HTMLAudioElement>(null);
  const previousPathnameRef = useRef(pathname);
  const revisionRef = useRef(0);
  const [scanCompletion, setScanCompletion] = useState<{
    pathname: string;
    revision: number;
  } | null>(null);

  const isScanPage = /^\/(desktop|kiosk)\/scan\/[^/]+/.test(pathname);
  const isHomePage = /^\/(desktop|kiosk)\/?$/.test(pathname);
  const completedOnCurrentPage = scanCompletion?.pathname === pathname;
  const activeScanCompletionRevision = completedOnCurrentPage ? scanCompletion.revision : 0;
  const currentTrack = !isScanPage ? 1 : completedOnCurrentPage ? 3 : 2;
  const currentSource = [homeAudio, scanAudio, scannedAudio][currentTrack - 1];

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

    audio.pause();
    audio.currentTime = 0;
    if (completedOnCurrentPage) {
      void audio.play().catch((error: unknown) => {
        console.error('Unable to play scan completion audio:', error);
      });
    }

    return () => audio.pause();
  }, [currentSource, currentTrack, completedOnCurrentPage, activeScanCompletionRevision]);

  useEffect(() => {
    const previousPathname = previousPathnameRef.current;
    previousPathnameRef.current = pathname;

    const cameFromHomePage = /^\/(desktop|kiosk)\/?$/.test(previousPathname);
    if (!cameFromHomePage || !isScanPage || currentTrack !== 2) return;

    const audio = audioRef.current;
    if (!audio) return;

    audio.currentTime = 0;
    void audio.play().catch((error: unknown) => {
      console.error('Unable to play scan introduction audio:', error);
    });
  }, [currentTrack, isScanPage, pathname]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handlePointerDown = (event: PointerEvent) => {
      const target = event.target;
      if (
        target instanceof Element &&
        target.closest(
          'button, a, input, select, textarea, summary, [role="button"], [role="link"], [tabindex], [contenteditable="true"], audio[controls], video[controls]',
        )
      ) {
        return;
      }

      if (!isHomePage) return;

      audio.pause();
      audio.currentTime = 0;

      void audio.play().catch((error: unknown) => {
        console.error('Unable to play audio guide:', error);
      });
    };

    window.addEventListener('pointerdown', handlePointerDown, true);
    return () => window.removeEventListener('pointerdown', handlePointerDown, true);
  }, [isHomePage]);

  return <audio ref={audioRef} src={currentSource} preload="auto" />;
}
