// src/components/Loader.jsx
import React from 'react';
import './Loader.css'; // We'll create this file next

const Loader = () => {
  return (
    <div className="loader-container">
      <div className="pulsing-dot"></div>
      <p>Generating Quiz...</p>
    </div>
  );
};

export default Loader;