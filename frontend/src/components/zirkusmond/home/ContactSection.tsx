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

export default function ContactSection() {
  return (
    <div className="flex flex-col justify-between gap-12 p-12 border-2 border-primary bg-black/20 text-center text-primary lg:flex-row ">
      <div className="flex flex-col justify-center align-middle lg:w-1/3">
        <h3 className="my-4 sm:my-6">Contact</h3>
        <div className="flex items-center justify-evenly py-4">
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
        <div className="">
          <p className="p-4 sm:p-6">
            Direct matters concerning reservations
            <a
              className="my-4 sm:my-6 block underline"
              href="mailto:zirkusmond@gmail.com"
            >
              zirkusmond@gmail.com
            </a>
          </p>
        </div>
        <Button
          asChild
          variant={'primary'}
          className="self-center max-w-sm w-full"
        >
          <a href="https://www.paypal.com/donate?hosted_button_id=AA2ZBHH6JHX9E">
            Donate via PayPal
          </a>
        </Button>
      </div>

      <div className="flex justify-center">
        <div>
          <h3 className="my-4 sm:my-6">Find us</h3>
          <img
            className="m-auto w-9/12 max-w-80"
            src="/images/general/map.webp"
            alt="Der Zirkus liegt in der Nähe der Lili-Henoch-Str."
          />
        </div>
      </div>

      <div className="lg:w-1/3 flex flex-col justify-center align-middle">
        <h3 className="my-4 sm:my-6">Mailing List</h3>
        <p className="lg:pr-6">
          Want to be notified about new Shows? Hear what's going on on the moon?
          Not be forgotten or left out? Become part of our magical Mailing List!
        </p>
        <p className="pt-3 sm:pt-4 lg:pr-6">
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
            e.preventDefault()
          }}
        >
          <Field className="items-center">
            <FieldLabel htmlFor="newsletter-email" className="text-lg">
              Email:
            </FieldLabel>
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
      </div>
    </div>
  )
}
