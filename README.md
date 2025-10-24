#  QuizGenie: AI-Powered Quiz Generator

QuizGenie is an intelligent, full-stack application that automatically generates multiple-choice quizzes from your uploaded documents. It uses a Retrieval-Augmented Generation (RAG) pipeline to create accurate and contextually relevant questions, turning any set of notes into an interactive learning tool.

---
# Web Link (Hosting soonn..)

### 🎥 Video Demonstration

[![QuizGenie Video Demo](https://your-image-host.com/video-thumbnail.png)](https://youtu.be/u3yZ1N0Izss?si=9pIpk7xcPepXUOu5)


---

## ✨ Key Features

* **📝 Document Upload**: Simple interface to upload PDF documents or lecture notes.
* **🧠 AI-Powered Generation**: Leverages a sophisticated RAG pipeline to ensure questions are directly based on the provided text.
* **💡 Interactive Quizzing**: An engaging UI where users can take the generated quiz, select answers, and receive instant feedback with explanations.
* **🎨 Modern Tech Stack**: Built with a high-performance backend and a dynamic, responsive frontend.
* **🚀 Session-Based**: Each document upload creates a unique, isolated session, allowing for concurrent use without data conflicts.

---
## 💻 Tech Stack

This project demonstrates a wide range of modern development skills:

| Category     | Technology                                |
| :----------- | :---------------------------------------- |
| **Frontend** | React.js, Vite                            |
| **Backend** | FastAPI, Python                           |
| **AI & ML** | SentenceTransformers, FAISS, OpenAI     |
| **Hosting** | Netlify (Frontend), Render (Backend)      |
| **DevOps** | Git, GitHub, Virtual Environments       |

---
## 🛠️ How It Works: The RAG Pipeline

QuizGenie is more than a simple app; it's a practical implementation of a Retrieval-Augmented Generation (RAG) system.

1.  **Ingestion & Embedding**: When a PDF is uploaded, the backend extracts the text, splits it into manageable chunks, and uses a `SentenceTransformer` model to convert each chunk into a numerical vector embedding.
2.  **Indexing**: These embeddings are stored in a high-performance `FAISS` vector index, creating a searchable knowledge base from the document.
3.  **Retrieval**: When a quiz is requested, a query is embedded and used to perform a similarity search on the FAISS index, retrieving the most relevant text chunks.
4.  **Augmented Generation**: The retrieved chunks are injected into a carefully crafted prompt that instructs an LLM (like GPT) to generate quiz questions *only* from the provided context, ensuring factual accuracy.

---
## 🚀 Local Development Setup

Follow these instructions to run the project on your local machine.

### **Prerequisites**

* **Node.js** (v18 or later)
* **Python** (v3.9 or later)
* An **OpenAI API Key**

