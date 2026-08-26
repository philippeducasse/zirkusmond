import { useTranslation } from 'react-i18next'
import { cn } from '#/lib/utils.ts'
import { Button } from '#/components/ui/button'

const locales = ['en', 'de'] as const
type Locale = (typeof locales)[number]

export default function LocaleSwitcher({ isMobile }: { isMobile?: boolean }) {
  const { i18n } = useTranslation()
  const currentLocale = i18n.language

  const changeLanguage = (locale: Locale) => {
    i18n.changeLanguage(locale)
  }

  return (
    <div className="flex items-center gap-1">
      {locales.map((locale) => {
        const isActive = locale === currentLocale

        return (
          <Button
            key={locale}
            variant={'outline'}
            size={isMobile ? 'default' : 'xs'}
            aria-pressed={isActive}
            onClick={() => changeLanguage(locale)}
            className={cn(
              isActive
                ? 'border-primary bg-black/5 text-primary shadow-[0_10px_25px_-8px_rgba(0,0,0,0.5),0_0_18px_-6px_rgba(246,174,66,0.55)]'
                : 'border-transparent text-primary/50 hover:text-primary/80',
            )}
          >
            {locale.toUpperCase()}
          </Button>
        )
      })}
    </div>
  )
}
