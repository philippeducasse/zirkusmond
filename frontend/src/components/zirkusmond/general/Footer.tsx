import PageContainer from './PageContainer'
import SectionDivider from './SectionDivider'

const Footer = () => {
  return (
    <PageContainer>
      <SectionDivider type="moon" margin={'small'} />
      <div className="flex items-center justify-center max-w-7xl mx-auto text-white p-1 md:p-8">
        <div className="flex gap-6">
          <a
            href="/impressum"
            className="text-base sm:text-lg md:text-xl underline"
          >
            Impressum
          </a>
          <a
            href="/datenschutz"
            className="text-base sm:text-lg md:text-xl underline"
          >
            Datenschutz
          </a>
        </div>
      </div>
      <div className="flex flex-col md:flex-row text-sm sm:text-base text-center">
        <div className="px-4 lg:w-1/3">
          Kultstätte 58 GmbH Körtestraße 38 10967 Berlin
        </div>
        <div className="px-4 lg:w-1/3">Geschäftsführer: Max Mohr</div>
        <div className="px-4 lg:w-1/3">
          Steuer-Nr.: 37 / 406 / 50011 Steuer-ID: DE65 812 397 023 USt-IdNr:
          DE319431419
        </div>
      </div>
    </PageContainer>
  )
}

export default Footer
