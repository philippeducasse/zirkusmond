import { buildNewsletterField } from '../helper'
import DynamicForm from '../../form/DynamicForm'

interface NewsletterFormProps {
  newsletter: boolean
  setNewsletter: (checked: boolean) => void
}

const NewsletterForm = ({ newsletter, setNewsletter }: NewsletterFormProps) => {
  return (
    // <div className="-mt-12">
    <DynamicForm fields={buildNewsletterField({ newsletter, setNewsletter })} />
    // </div>
  )
}

export default NewsletterForm
