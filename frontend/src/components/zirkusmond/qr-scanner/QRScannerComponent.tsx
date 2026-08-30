import { useEffect, useRef, useState } from "react";
import { Html5Qrcode } from "html5-qrcode";

import type {
  CheckInAlreadyCheckedIn,
  CheckInSuccess,
  QRCodeData,
  QRScannerEvent,
} from "#/interfaces/qr-scanner.ts";
import { checkInTicket } from "#/lib/qr-scanner-api.ts";
import { AlreadyCheckedIn } from "./AlreadyCheckedIn.tsx";
import { CheckInSuccess as CheckInSuccessComponent } from "./CheckInSuccess.tsx";
import { EventSelector } from "./EventSelector.tsx";
import { ScanError } from "./ScanError.tsx";

interface QRScannerComponentProps {
  events: QRScannerEvent[];
}

export const QRScannerComponent = ({ events }: QRScannerComponentProps) => {
  const [selectedEvent, setSelectedEvent] = useState<QRScannerEvent | null>(
    null,
  );
  const [lastScan, setLastScan] = useState<CheckInSuccess | null>(null);
  const [alreadyCheckedIn, setAlreadyCheckedIn] =
    useState<CheckInAlreadyCheckedIn | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [audioUnlocked, setAudioUnlocked] = useState(false);

  const scannerRef = useRef<Html5Qrcode | null>(null);
  const successSoundRef = useRef<HTMLAudioElement | null>(null);
  const errorSoundRef = useRef<HTMLAudioElement | null>(null);

  // Auto-select today's event
  useEffect(() => {
    if (events.length > 0 && !selectedEvent) {
      const today = new Date().toISOString().split("T")[0];
      const todayEvent = events.find((event) => event.begin.includes(today));
      if (todayEvent) {
        setSelectedEvent(todayEvent);
      }
    }
  }, [events, selectedEvent]);

  // Unlock audio on user interaction
  const unlockAudio = () => {
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

  const playSound = (type: "success" | "error") => {
    if (type === "success") {
      successSoundRef.current?.play();
    } else {
      errorSoundRef.current?.play();
    }
  };

  const handleCheckIn = async (ticketUuid: string, eventId: number) => {
    if (!selectedEvent) return;

    if (eventId !== selectedEvent.id) {
      setError("Ticket for wrong event!");
      playSound("error");
      return;
    }

    try {
      const data = await checkInTicket(ticketUuid, eventId);

      if (data.success) {
        setLastScan(data);
        setAlreadyCheckedIn(null);
        setError(null);
        playSound("success");
        scannerRef.current?.pause();
        setTimeout(() => scannerRef.current?.resume(), 2000);
      } else if (
        data.error === "Ticket already checked in" &&
        "guests" in data &&
        "reservationNumber" in data
      ) {
        setAlreadyCheckedIn(data);
        setLastScan(null);
        setError(null);
        playSound("error");
        scannerRef.current?.pause();
        setTimeout(() => scannerRef.current?.resume(), 2000);
      } else {
        setError(data.error || "Check-in failed");
        setLastScan(null);
        setAlreadyCheckedIn(null);
        playSound("error");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error checking in ticket");
      setLastScan(null);
      setAlreadyCheckedIn(null);
      playSound("error");
    }
  };

  const onScanSuccess = (decodedText: string) => {
    setError(null);
    setAlreadyCheckedIn(null);
    setLastScan(null);

    try {
      const data: QRCodeData = JSON.parse(decodedText);
      handleCheckIn(data.ticket, data.event);
    } catch {
      setError("Invalid QR code format");
      playSound("error");
    }
  };

  const onScanError = (err: string) => {
    // Suppress "No QR code found" errors
    if (!err.includes("No QR code found")) {
      // console.debug(err)
    }
  };

  // Initialize scanner when event is selected
  useEffect(() => {
    if (!selectedEvent) return;

    const scanner = new Html5Qrcode("reader");
    scannerRef.current = scanner;

    const config = {
      fps: 10,
      qrbox: (viewfinderWidth: number, viewfinderHeight: number) => ({
        width: viewfinderWidth,
        height: viewfinderHeight,
      }),
    };

    scanner
      .start({ facingMode: "environment" }, config, onScanSuccess, onScanError)
      .catch((err) => {
        setError(`Failed to start scanner: ${err}`);
      });

    return () => {
      if (scanner.isScanning) {
        scanner.stop().catch(() => {});
      }
    };
  }, [selectedEvent]);

  const handleEventChange = (event: QRScannerEvent | null) => {
    // Stop scanner if it's running
    if (scannerRef.current?.isScanning) {
      scannerRef.current.stop().catch(() => {});
    }
    setSelectedEvent(event);
    setLastScan(null);
    setAlreadyCheckedIn(null);
    setError(null);
    unlockAudio();
  };

  return (
    <div className="min-h-screen p-4" onClick={unlockAudio}>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-6xl md:text-3xl font-bold mb-6 text-center">
          QR Code Scanner
        </h1>

        <EventSelector
          events={events}
          selectedEvent={selectedEvent}
          onSelectEvent={handleEventChange}
        />

        <div
          id="reader"
          className="bg-white rounded-lg shadow-lg mb-6"
          style={{
            width: "100%",
            maxWidth: "500px",
            margin: "0 auto 1.5rem",
          }}
        />

        {lastScan && <CheckInSuccessComponent data={lastScan} />}
        {alreadyCheckedIn && <AlreadyCheckedIn data={alreadyCheckedIn} />}
        {error && <ScanError error={error} />}

        <audio ref={successSoundRef} src="/audio/success_sound.mp3" />
        <audio ref={errorSoundRef} src="/audio/error_sound.mp3" />
      </div>
    </div>
  );
};
