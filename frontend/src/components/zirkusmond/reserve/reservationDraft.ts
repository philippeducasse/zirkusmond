import { useEffect } from "react";

export interface GuestFormData {
  firstName: string;
  lastName: string;
  email: string;
  guests: { firstName: string; lastName: string }[];
}

export interface ReservationDraft extends GuestFormData {
  attendeeCount: number;
  customPrice: number;
  newsletter: boolean;
}

export const extractGuestFormData = (
  formData: FormData,
  guestCount: number,
): GuestFormData => {
  const guests: GuestFormData["guests"] = [];

  for (let i = 0; i < guestCount; i++) {
    guests.push({
      firstName: formData.get(`guest-${i}-first-name`) as string,
      lastName: formData.get(`guest-${i}-last-name`) as string,
    });
  }

  return {
    firstName: formData.get("firstName") as string,
    lastName: formData.get("lastName") as string,
    email: formData.get("email") as string,
    guests,
  };
};

const DRAFT_KEY = "reservation-draft";

export const loadDraft = (): ReservationDraft | null => {
  if (typeof window === "undefined") return null;

  const draftJson = sessionStorage.getItem(DRAFT_KEY);
  if (!draftJson) return null;

  try {
    return JSON.parse(draftJson);
  } catch (error) {
    console.error(
      `Failed to parse field inputs: ${draftJson}, error: ${error}`,
    );
    return null;
  }
};

export const saveDraft = (draft: ReservationDraft) => {
  sessionStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
};

export const clearDraft = () => {
  sessionStorage.removeItem(DRAFT_KEY);
};

export const setFormValue = (name: string, value: string | undefined) => {
  if (value === undefined) return;

  const form = document.getElementById(
    "reservation-form",
  ) as HTMLFormElement | null;
  if (!form) return;

  const el = form.elements.namedItem(name);
  if (el instanceof HTMLInputElement) el.value = value;
};

export const useFormStorage = (savedInputs: ReservationDraft | null) => {
  useEffect(() => {
    if (!savedInputs) return;

    setFormValue("firstName", savedInputs.firstName);
    setFormValue("lastName", savedInputs.lastName);
    setFormValue("email", savedInputs.email);

    savedInputs.guests.forEach((guest, i) => {
      setFormValue(`guest-${i}-first-name`, guest.firstName);
      setFormValue(`guest-${i}-last-name`, guest.lastName);
    });
  });
};
