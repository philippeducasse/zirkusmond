import { Link } from '@tanstack/react-router'

import SectionDivider from './SectionDivider'
import { useTranslation } from 'react-i18next'

const Footer = () => {
  const { t } = useTranslation()
  return (
    <>
      <SectionDivider type="moon" margin={'small'} />
      <div className="w-full md:max-w-2/3 mx-auto flex flex-col text-center p-1 md:p-8 gap-6">
        <div className="flex gap-6 justify-center text-white ">
          <Link
            to="/impressum"
            className="text-base sm:text-lg md:text-xl underline"
          >
            {t('footer_impressum')}
          </Link>
          <Link
            to="/datenschutz"
            className="text-base sm:text-lg md:text-xl underline"
          >
            {t('footer_datenschutz')}
          </Link>
        </div>
        <div className="flex flex-col md:flex-row align-middle justify-centertext-sm sm:text-base">
          <p className="px-4 lg:w-1/3 text-sm">
            {t('footer_address')}
          </p>
          <p className="px-4 lg:w-1/3 text-sm">{t('footer_director')}</p>
          <p className="px-4 lg:w-1/3 text-sm">
            {t('footer_tax_info')}
          </p>
        </div>
      </div>
    </>
  )
}

export default Footer
