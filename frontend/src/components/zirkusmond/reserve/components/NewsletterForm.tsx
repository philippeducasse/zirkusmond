import { buildNewsletterField } from "../formFieldBuilders";
import DynamicForm from "../../form/DynamicForm";

interface NewsletterFormProps {
  newsletter: boolean;
  setNewsletter: (checked: boolean) => void;
}

const NewsletterForm = ({ newsletter, setNewsletter }: NewsletterFormProps) => {
  return (
    <DynamicForm fields={buildNewsletterField({ newsletter, setNewsletter })} />
  );
};

export default NewsletterForm;
