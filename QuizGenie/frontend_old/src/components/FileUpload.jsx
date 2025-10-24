// src/components/FileUpload.jsx
import React, { useState } from 'react';

function FileUpload() {
    // State to hold the selected file
    const [selectedFile, setSelectedFile] = useState(null);
    // State to show feedback to the user
    const [uploadStatus, setUploadStatus] = useState('');

    // Handles the file selection from the input
    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
        setUploadStatus(''); // Reset status on new file selection
    };

    // Handles the file upload submission
    const handleFileUpload = async () => {
        if (!selectedFile) {
            setUploadStatus('Please select a file first.');
            return;
        }

        // Create a FormData object to send the file
        const formData = new FormData();
        formData.append('file', selectedFile);

        setUploadStatus('Uploading file...');

        try {
            // Send the request to the backend
            const response = await fetch('http://127.0.0.1:8000/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('File upload failed!');
            }

            const data = await response.json();
            setUploadStatus(`Success: ${data.message}`);

        } catch (error) {
            console.error('Error uploading file:', error);
            setUploadStatus(`Error: ${error.message}`);
        }
    };

    return (
        <div className="file-upload-container">
            <h2>Upload Your Document</h2>
            <p>Upload a PDF file to generate a quiz from its content.</p>
            <input type="file" onChange={handleFileChange} accept=".pdf" />
            <button onClick={handleFileUpload}>Upload File</button>
            {/* Display the status message to the user */}
            {uploadStatus && <p className="status-message">{uploadStatus}</p>}
        </div>
    );
}

export default FileUpload;