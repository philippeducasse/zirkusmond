import type { RefObject } from "react";
import type { Html5Qrcode } from "html5-qrcode";

import type { QRScannerEvent } from "#/interfaces/qr-scanner.ts";

interface UnlockAudioParams {
  audioUnlocked: boolean;
  successSoundRef: RefObject<HTMLAudioElement | null>;
  errorSoundRef: RefObject<HTMLAudioElement | null>;
  setAudioUnlocked: (unlocked: boolean) => void;
}

export const unlockAudio = ({
  audioUnlocked,
  successSoundRef,
  errorSoundRef,
  setAudioUnlocked,
}: UnlockAudioParams) => {
  if (audioUnlocked) return;
  [successSoundRef.current, errorSoundRef.current].forEach((audio) => {
    if (audio) {
      audio.volume = 0;
      audio
        .play()
        .then(() => {
          audio.pause();
          audio.currentTime = 0;
          audio.volume = 1;
        })
        .catch(() => {});
    }
  });
  setAudioUnlocked(true);
};

export const playSound = (
  type: "success" | "error",
  successSoundRef: RefObject<HTMLAudioElement | null>,
  errorSoundRef: RefObject<HTMLAudioElement | null>,
) => {
  if (type === "success") {
    successSoundRef.current?.play();
  } else {
    errorSoundRef.current?.play();
  }
};

interface HandleEventChangeParams {
  scannerRef: RefObject<Html5Qrcode | null>;
  setSelectedEvent: (event: QRScannerEvent | null) => void;
  setLastScan: (data: null) => void;
  setAlreadyCheckedIn: (data: null) => void;
  setError: (error: string | null) => void;
  onUnlockAudio: () => void;
}

export const handleEventChange = (
  event: QRScannerEvent | null,
  {
    scannerRef,
    setSelectedEvent,
    setLastScan,
    setAlreadyCheckedIn,
    setError,
    onUnlockAudio,
  }: HandleEventChangeParams,
) => {
  if (scannerRef.current?.isScanning) {
    scannerRef.current.stop().catch(() => {});
  }
  setSelectedEvent(event);
  setLastScan(null);
  setAlreadyCheckedIn(null);
  setError(null);
  onUnlockAudio();
};
