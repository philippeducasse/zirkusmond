import { Link } from "@tanstack/react-router";

export default function Logo() {
  return (
    <Link to="/" className="flex justify-center">
      <img
        className="h-[56.25px] w-[56.25px] object-cover"
        src="/images/logos/logo_16x9.webp"
        alt="Zirkusmond logo"
        width={100}
      />
    </Link>
  );
}
