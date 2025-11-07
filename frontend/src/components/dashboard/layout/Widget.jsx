import React from 'react';
import { Card, Button } from 'react-bootstrap';
import { FaTimes } from 'react-icons/fa';

const Widget = ({ title, children, onRemove }) => {
  return (
    <Card className="h-100">
      <Card.Header>
        {title}
        <Button
          variant="link"
          className="float-end text-danger"
          onClick={onRemove}
        >
          <FaTimes />
        </Button>
      </Card.Header>
      <Card.Body>{children}</Card.Body>
    </Card>
  );
};

export default Widget;
