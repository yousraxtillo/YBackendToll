import React, { useState } from 'react';
import { Modal, Button } from 'react-bootstrap';

const ExplanationModal = ({ explanation }) => {
  const [show, setShow] = useState(false);

  return (
    <>
      <Button variant="primary" onClick={() => setShow(true)}>
        Vis Forklaring
      </Button>

      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Forklaring</Modal.Title>
        </Modal.Header>
        <Modal.Body>{explanation}</Modal.Body>
      </Modal>
    </>
  );
};


// pages/explanation.js
export async function getServerSideProps(context) {
    const inputText = context.query.input; // Anta at du sender input som en query parameter
    const explanation = await generateExplanationForText(inputText); // Kall backend logikken direkte her
  
    return {
      props: { explanation }, // Vil bli passert til siden som props
    };
  }
  
  function ExplanationPage({ explanation }) {
    return <div>Forklaring: {explanation}</div>;
  }
  
  export default ExplanationPage;
  
