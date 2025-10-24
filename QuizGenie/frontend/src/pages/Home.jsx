// src/pages/Home.jsx
import React from 'react';
import FileUpload from '../components/FileUpload'; // 👈 1. Import the component

function Home() {
    return (
        <div className="home-container">
            {/* You can add a navbar or other elements here later */}
            <h1>Welcome to QuizGenie</h1>

            <FileUpload /> {/* 👈 2. Add the component here */}

            {/* The quiz display area can go below this */}
        </div>
    );
}

export default Home;