import type { QRScannerEvent } from "#/interfaces/qr-scanner.ts";
import { Button } from "#/components/ui/button.tsx";

interface EventSelectorProps {
  events: QRScannerEvent[];
  selectedEvent: QRScannerEvent | null;
  onSelectEvent: (event: QRScannerEvent | null) => void;
}

export const EventSelector = ({
  events,
  selectedEvent,
  onSelectEvent,
}: EventSelectorProps) => {
  if (selectedEvent) {
    return (
      <div className="mb-6">
        <h2 className="text-5xl md:text-2xl font-bold mb-4 text-center">
          {selectedEvent.title} - {selectedEvent.date}
        </h2>
        <Button
          variant="outline"
          size="sm"
          className="w-full text-3xl"
          onClick={() => onSelectEvent(null)}
        >
          Select another event
        </Button>
      </div>
    );
  }
  return (
    <div className="p-4 mb-6">
      <label className="block text-3xl font-bold mb-2">Select Event:</label>
      <select
        value=""
        onChange={(e) => {
          const selectedId = Number(e.target.value);
          const event = events.find((ev) => ev.id === selectedId);
          onSelectEvent(event ?? null);
        }}
        className="w-full px-4 py-3 text-xl border rounded-lg"
      >
        <option value="">Choose an event...</option>
        {events.map((event) => (
          <option key={event.id} value={event.id}>
            {event.title} - {event.date}
          </option>
        ))}
      </select>
    </div>
  );
};
