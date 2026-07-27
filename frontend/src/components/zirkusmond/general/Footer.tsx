import { Link } from '@tanstack/react-router'

import SectionDivider from './SectionDivider'

const Footer = () => {
  return (
    <>
      <SectionDivider type="moon" margin={'small'} />
      <div className="max-w-2/3 mx-auto flex flex-col text-center p-1 md:p-8 gap-6">
        <div className="flex gap-6 justify-center text-white ">
          <Link
            to="/impressum"
            className="text-base sm:text-lg md:text-xl underline"
          >
            Impressum
          </Link>
          <Link
            to="/datenschutz"
            className="text-base sm:text-lg md:text-xl underline"
          >
            Datenschutz
          </Link>
        </div>
        <div className="flex flex-col md:flex-row align-middle justify-centertext-sm sm:text-base">
          <div className="px-4 lg:w-1/3">
            Lilli-Henoch-Str. Office at: Kultstätte 58 GmbH Körtestraße 38 10967
            Berlin
          </div>
          <div className="px-4 lg:w-1/3">Geschäftsführer Max Mohr</div>
          <div className="px-4 lg:w-1/3">
            Steuer-Nr.: 37 / 406 / 50011 Steuer-ID: DE65 812 397 023 USt-IdNr:
            DE319431419
          </div>
        </div>
      </div>
    </>
  )
}

export default Footer
