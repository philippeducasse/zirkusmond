import { useTranslation } from "react-i18next";

interface SpinnerProps {
  text?: string;
}

export default function Spinner({ text }: SpinnerProps) {
  const { t } = useTranslation();
  const displayText = text ?? t("button_processing");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-6">
        <div className="relative w-32">
          <img
            src="/images/logos/logo_16x9.webp"
            alt="Zirkusmond logo"
            className="w-full h-auto object-contain"
            style={{
              animation: "spin-slow 2s linear infinite",
            }}
          />
        </div>

        {displayText && (
          <p className="text-2xl font-medium text-white animate-pulse">
            {displayText}
          </p>
        )}
      </div>
    </div>
  );
}
