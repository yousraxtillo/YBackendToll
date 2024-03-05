import React, { useState } from 'react';

const ExplanationComponent = () => {
  const [inputText, setInputText] = useState('');
  const [explanation, setExplanation] = useState('');

  const fetchExplanation = async () => {
    const response = await fetch('http://localhost:5000/get-explanation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ inputText }),
    });

    const data = await response.json();
    setExplanation(data.explanation);
  };

  return (
    <div>
      <input 
        type="text" 
        value={inputText} 
        onChange={(e) => setInputText(e.target.value)} 
      />
      <button onClick={fetchExplanation}>Få Forklaring</button>
      <p>Forklaring: {explanation}</p>
    </div>
  );
};

