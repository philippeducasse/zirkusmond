// Locale switcher refs:
// - Paraglide docs: https://inlang.com/m/gerre34r/library-inlang-paraglideJs
// - Router example: https://github.com/TanStack/router/tree/main/examples/react/i18n-paraglide#switching-locale
import { getLocale, locales, setLocale } from '#/paraglide/runtime'
import { cn } from '#/lib/utils.ts'
import { Button } from '#/components/ui/button'

type Locale = (typeof locales)[number]

export default function LocaleSwitcher() {
  const currentLocale = getLocale()

  return (
    <div className="flex items-center gap-1">
      {locales.map((locale) => {
        const isActive = locale === currentLocale

        return (
          <Button
            key={locale}
            variant={'outline'}
            size={'xs'}
            aria-pressed={isActive}
            onClick={() => setLocale(locale as Locale)}
            className={cn(
              isActive
                ? 'border-primary bg-white/5 text-primary shadow-[0_10px_25px_-8px_rgba(0,0,0,0.5),0_0_18px_-6px_rgba(246,174,66,0.55)]'
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
