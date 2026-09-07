export interface HomepageElementBase {
  id: number;
  titleDe: string;
  titleEn: string;
  messageDe: string;
  messageEn: string;
  active: boolean;
  link: string;
}

export interface PopUpElement extends HomepageElementBase {
  type: "popupelement";
}
export interface InlineSectionElement extends HomepageElementBase {
  type: "preshowselement" | "postshowselement";
}

/**
 * Discriminated on `type` (the Django model name). Add further element
 * types to this union as they are created in `homepage_elements`.
 */
export type HomepageElement = PopUpElement | InlineSectionElement;
