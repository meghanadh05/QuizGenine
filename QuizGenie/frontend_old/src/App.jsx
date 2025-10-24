// src/App.jsx
import React from 'react';
import Home from './pages/Home'; // 👈 1. Import your Home page
import './App.css'; // You may need to create this file or use an existing CSS file

function App() {
    return (
        <div className="App">
            <Home /> {/* 👈 2. Render your Home page here */}
        </div>
    );
}

export default App;