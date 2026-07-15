import { Button } from '#/components/ui/button.tsx'
import { Field, FieldLabel } from '#/components/ui/field.tsx'
import { Input } from '#/components/ui/input.tsx'

// TODO: REFACTOR THIS ENTIRE PAGE AND MAKE IT BETTER

const SOCIAL_LINKS = [
  {
    label: 'YouTube',
    href: 'https://www.youtube.com/channel/UCa4CK1Fl7ZpTA6mz04wH6CA',
    icon: '/images/icons/youtube.svg',
  },
  {
    label: 'Facebook',
    href: 'https://de-de.facebook.com/zirkusmond',
    icon: '/images/icons/facebook.svg',
  },
  {
    label: 'Instagram',
    href: 'https://www.instagram.com/zirkus_mond/',
    icon: '/images/icons/instagram.svg',
  },
]

export default function FooterSection() {
  return (
    <div className="mx-auto max-w-[1800px] px-6 lg:px-16">
      <div className="flex flex-col justify-between gap-12 border-2 border-[#e7b548] bg-[#00000040] p-6 text-center text-primary lg:flex-row">
        <div className="flex flex-col items-center lg:w-1/3">
          <h2 className="my-4 sm:my-6 text-xl sm:text-2xl md:text-3xl">Contact</h2>
          <div className="flex items-center justify-evenly gap-6 py-4">
            {SOCIAL_LINKS.map((social) => (
              <a
                key={social.label}
                href={social.href}
                target="_blank"
                rel="noreferrer"
              >
                <img className="w-12" src={social.icon} alt={social.label} />
              </a>
            ))}
          </div>
          <p className="p-4 sm:p-6 text-base sm:text-lg">
            Direct matters concerning reservations
            <a
              className="my-4 sm:my-6 block underline"
              href="mailto:zirkusmond@gmail.com"
            >
              zirkusmond@gmail.com
            </a>
          </p>
        </div>

        <div className="flex justify-center lg:w-1/3">
          <div className="w-4/5 lg:w-3/5">
            <h2 className="my-4 sm:my-6 text-xl sm:text-2xl md:text-3xl">Find us</h2>
            <img
              className="m-auto w-9/12 max-w-80"
              src="/images/general/map.webp"
              alt="Der Zirkus liegt in der Nähe der Lili-Henoch-Str."
            />
          </div>
        </div>

        <div className="lg:w-1/3">
          <h2 className="my-4 sm:my-6 text-xl sm:text-2xl md:text-3xl">Mailing List</h2>
          <p className="text-base sm:text-lg lg:pr-6">
            Want to be notified about new Shows? Hear what's going on on the
            moon? Not be forgotten or left out? Become part of our magical
            Mailing List!
          </p>
          <p className="pt-3 sm:pt-4 text-base sm:text-lg lg:pr-6">
            You can also join our Telegram{' '}
            <a
              className="underline"
              href="https://t.me/+bTzQFVB2cHc5b4Zm"
              target="_blank"
              rel="noreferrer"
            >
              channel
            </a>
            !
          </p>
          <form
            className="my-6"
            onSubmit={(e) => {
              // TODO: wire up to POST /newsletter/register once an API client exists
              e.preventDefault()
            }}
          >
            <Field className="items-center">
              <FieldLabel htmlFor="newsletter-email">Email:</FieldLabel>
              <Input
                className="my-2"
                id="newsletter-email"
                type="email"
                name="email"
                maxLength={254}
                required
              />
            </Field>
            <Button type="submit" className="mt-4">
              Submit
            </Button>
          </form>

          <h2 className="text-xl sm:text-2xl md:text-3xl">Support Us</h2>
          <div className="my-4 sm:my-6 text-center">
            <h3 className="my-3 sm:my-4 text-sm sm:text-base">Bank Transfer/Überweisung:</h3>
            <p className="py-2 text-sm sm:text-base">IBAN: DE34 4306 0967 1226 9437 00</p>
            <p className="text-sm sm:text-base">BIC: GENODEM1GLS</p>
          </div>
          <Button asChild>
            <a href="https://www.paypal.com/donate?hosted_button_id=AA2ZBHH6JHX9E">
              Donate via PayPal
            </a>
          </Button>
        </div>
      </div>

      <div className="mb-6 sm:mb-8 pt-6 sm:pt-8 text-center">
        <div className="flex justify-evenly gap-4">
          <a href="/impressum" className="text-base sm:text-lg md:text-xl underline">
            Impressum
          </a>
          <a href="/datenschutz" className="text-base sm:text-lg md:text-xl underline">
            Datenschutz
          </a>
        </div>
        <div className="flex flex-col md:flex-row text-sm sm:text-base">
          <div className="px-4 lg:w-1/3">
            Tent at: Lilli-Henoch-Str. Office at: Kultstätte 58 GmbH Körtestraße
            38 10967 Berlin
          </div>
          <div className="px-4 lg:w-1/3">Geschäftsführer Max Mohr</div>
          <div className="px-4 lg:w-1/3">
            Steuer-Nr.: 37 / 406 / 50011 Steuer-ID: DE65 812 397 023 USt-IdNr:
            DE319431419
          </div>
        </div>
      </div>
    </div>
  )
}
