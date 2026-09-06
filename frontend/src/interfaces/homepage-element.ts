export interface HomepageElementBase {
  id: number;
  title: string;
  message: string;
  active: boolean;
  link: string;
}

export type PopUpPosition = "top" | "bottom" | "top_right" | "bottom_right";

export interface PopUpElement extends HomepageElementBase {
  type: "popupelement";
  position: PopUpPosition;
}

/**
 * Discriminated on `type` (the Django model name). Add further element
 * types to this union as they are created in `homepage_elements`.
 */
export type HomepageElement = PopUpElement;
