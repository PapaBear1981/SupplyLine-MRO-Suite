import { Container } from 'react-bootstrap';
import CheckoutForm from '../components/checkouts/CheckoutForm';

const CheckoutPage = () => {
  return (
    <Container>
      <h1 className="mb-4">Checkout Tool</h1>
      <CheckoutForm />
    </Container>
  );
};

export default CheckoutPage;
