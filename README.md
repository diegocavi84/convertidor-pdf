# 📄 PDF Converter

A modern, efficient web application to convert various file formats (Office documents, images, text) into PDF. Built with a robust backend using FastAPI and LibreOffice, and a lightweight, minimal frontend.

## ✨ Features

-   **Office to PDF**: Converts `.docx`, `.xlsx`, `.pptx`, `.odt`, `.ods`, `.odp`, and `.rtf` files.
-   **Local Conversion**: Instantly converts images (`.png`, `.jpg`) and text files (`.txt`, `.md`) locally without backend load.
-   **Drag & Drop Interface**: Simple, user-friendly frontend.
-   **Containerized Backend**: Dockerized environment ensuring consistent behavior across local and production.
-   **Cloud Deployed**: Live on Render (Free Tier) for public access.

## 🛠️ Tech Stack

-   **Backend**: Python 3.11, FastAPI, Uvicorn
-   **Conversion Engine**: LibreOffice (Headless) + Java
-   **Frontend**: Vanilla HTML/CSS/JS
-   **Infrastructure**: Docker, GitHub, Render

## 🚀 Getting Started

### Prerequisites

-   Python 3.11+
-   Docker & Docker Desktop
-   Git

### Local Development

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/diegocavi84/convertidor-pdf.git
    cd convertidor-pdf
    ```

2.  **Run the Backend (Docker)**:
    The backend includes LibreOffice and dependencies.
    ```bash
    cd backend
    docker build -t convertidor-pdf .
    docker run -p 8000:8000 convertidor-pdf
    ```

3.  **Run the Frontend**:
    ```bash
    cd frontend
    python3 -m http.server 8080
    ```

4.  **Access**:
    Open your browser at `http://localhost:8080`.

## ☁️ API Documentation

Once the backend is running, access the interactive API docs at:
👉 `http://localhost:8000/docs`

### Endpoints

-   `GET /`: Health check & status message.
-   `GET /health`: Verifies LibreOffice installation.
-   `POST /convert`: Upload a file to convert it to PDF.

## 🌐 Live Demo

Try it out here: [https://convertidor-pdf-52xh.onrender.com](https://convertidor-pdf-52xh.onrender.com)

*(Note: The backend might take ~30-50s to wake up on the first request due to Render's free tier sleep policy.)*

##  License

This project is open source.
