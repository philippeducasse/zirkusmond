import { buildNewsletterField } from '../helper'
import DynamicField from '../../form/DynamicField'

interface NewsletterFormProps {
  newsletter: boolean
  setNewsletter: (checked: boolean) => void
}

const NewsletterForm = ({ newsletter, setNewsletter }: NewsletterFormProps) => {
  const newsletterFields = buildNewsletterField({ newsletter, setNewsletter })

  return (
    <div className="bg-white/10">
      {newsletterFields.map((field) => (
        <DynamicField key={field.id} field={field} />
      ))}
    </div>
  )
}

export default NewsletterForm
