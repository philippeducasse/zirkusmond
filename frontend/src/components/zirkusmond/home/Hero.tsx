import SectionDivider from "#/components/zirkusmond/general/SectionDivider";

export default function Hero() {
  return (
    <div>
      <div className="h-[80vh] w-full bg-[url(/images/general/zm_banner.webp)] bg-cover bg-center max-md:h-[50vh] max-[500px]:h-[40vh]" />
      <SectionDivider type="flower" />
    </div>
  );
}
