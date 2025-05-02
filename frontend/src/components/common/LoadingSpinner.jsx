import { Spinner } from 'react-bootstrap';

const LoadingSpinner = ({ size = 'md', text = 'Loading...' }) => {
  return (
    <div className="d-flex flex-column justify-content-center align-items-center my-5">
      <Spinner
        animation="border"
        role="status"
        variant="primary"
        className={`spinner-${size}`}
      />
      {text && <span className="mt-2">{text}</span>}
    </div>
  );
};

export default LoadingSpinner;
