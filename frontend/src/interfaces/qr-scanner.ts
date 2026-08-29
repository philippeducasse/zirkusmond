export interface QRScannerEvent {
  id: number;
  title: string;
  date: string;
  begin: string;
}

export interface CheckInSuccess {
  success: true;
  isGroup: boolean;
  guests: string[];
  reservationNumber: string;
}

export interface CheckInAlreadyCheckedIn {
  success: false;
  error: "Ticket already checked in";
  guests: string[];
  reservationNumber: string;
}

export interface CheckInError {
  success: false;
  error: string;
}

export type CheckInResponse =
  CheckInSuccess | CheckInAlreadyCheckedIn | CheckInError;

export interface QRCodeData {
  ticket: string;
  event: number;
}
