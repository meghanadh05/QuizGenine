// src/App.jsx
import React from 'react';
import Home from './pages/Home';

function App() {
  return (
    // We'll use the .App container for max-width and centering
    <div className="App">
      <header className="app-header">
        <div className="header-inner">
          <h1 className="brand-title">QuizGenie</h1>
          <p className="brand-tagline">AI-Powered Quiz Generation</p>
        </div>
      </header>
      <main>
        <Home />
      </main>
    </div>
  );
}

export default App;