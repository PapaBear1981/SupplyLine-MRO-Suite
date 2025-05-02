import { Modal, Button } from 'react-bootstrap';

const ModalContainer = ({
  show,
  onHide,
  title,
  children,
  footer,
  size = 'lg',
  closeButton = true,
}) => {
  return (
    <Modal show={show} onHide={onHide} size={size} centered>
      <Modal.Header closeButton={closeButton}>
        <Modal.Title>{title}</Modal.Title>
      </Modal.Header>
      <Modal.Body>{children}</Modal.Body>
      {footer && <Modal.Footer>{footer}</Modal.Footer>}
    </Modal>
  );
};

export default ModalContainer;
