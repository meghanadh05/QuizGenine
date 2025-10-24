import React, { useState } from 'react';
import Loader from './Loader'; // Import the new animated loader

// --- INTERACTIVE QUIZ CARD COMPONENT (No changes here) ---
const QuizCard = ({ questionData, index }) => {
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const hasAnswered = selectedAnswer !== null;

    const handleChoiceClick = (choiceKey) => {
        if (hasAnswered) return;
        setSelectedAnswer(choiceKey);
    };

    return (
        <div className="question-card">
            <p><strong>{index + 1}. {questionData.question}</strong></p>
            <div className="choices-container">
                {Object.entries(questionData.choices).map(([key, value]) => {
                    let buttonClass = 'choice-btn';
                    if (hasAnswered) {
                        if (key === questionData.answer) {
                            buttonClass += ' correct';
                        } else if (key === selectedAnswer) {
                            buttonClass += ' incorrect';
                        }
                    }
                    return (
                        <button 
                            key={key} 
                            className={buttonClass} 
                            onClick={() => handleChoiceClick(key)}
                            disabled={hasAnswered}
                        >
                            {key}: {value}
                        </button>
                    );
                })}
            </div>
            {hasAnswered && (
                <div className="explanation">
                    <em>Explanation: {questionData.explanation}</em>
                </div>
            )}
        </div>
    );
};

// --- MAIN FILE UPLOAD COMPONENT ---
function FileUpload() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');
    const [isFileUploaded, setIsFileUploaded] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [quizData, setQuizData] = useState(null);
    const [sessionId, setSessionId] = useState(null);

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
        setUploadStatus('');
        setIsFileUploaded(false);
        setQuizData(null);
    };

    const handleFileUpload = async () => {
        if (!selectedFile) {
            setUploadStatus('Please select a file first.');
            return;
        }
        const formData = new FormData();
        formData.append('file', selectedFile);
        setUploadStatus('Uploading and processing file...');
        try {
            const response = await fetch('http://127.0.0.1:8000/upload', { method: 'POST', body: formData });
            if (!response.ok) throw new Error('File upload failed!');
            const data = await response.json();
            setUploadStatus(`Success: ${data.message}`);
            setSessionId(data.session_id);
            setIsFileUploaded(true);
        } catch (error) {
            setUploadStatus(`Error: ${error.message}`);
        }
    };

    const handleGenerateQuiz = async () => {
        setIsGenerating(true);
        setQuizData(null);
        try {
            const response = await fetch('http://127.0.0.1:8000/generate_quiz', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
            if (!response.ok) throw new Error('Failed to generate quiz.');
            const data = await response.json();
            setQuizData(data.data);
        } catch (error) {
            console.error('Quiz generation error:', error);
            setUploadStatus(`Error: ${error.message}`);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="file-upload-container">
            <h2>1. Upload Your Document</h2>
            <p>Upload a PDF file to generate a quiz from its content.</p>
            <input type="file" onChange={handleFileChange} accept=".pdf" />
            <button onClick={handleFileUpload}>Upload & Process</button>
            {uploadStatus && <p>{uploadStatus}</p>}
            
            <hr />

            {isFileUploaded && (
                <div>
                    <h2>2. Generate Your Quiz</h2>
                    {/* The button text is simplified now that we have a loader */}
                    <button onClick={handleGenerateQuiz} disabled={isGenerating}>
                        Generate Quiz
                    </button>
                </div>
            )}

            {/* Conditionally render the Loader component */}
            {isGenerating && <Loader />}

            {/* Render quiz data only when it's available and not generating */}
            {quizData && !isGenerating && (
                <div className="quiz-results">
                    <h2>Quiz Results</h2>
                    {quizData.map((q, index) => (
                        <QuizCard key={index} questionData={q} index={index} />
                    ))}
                </div>
            )}
        </div>
    );
}

export default FileUpload;