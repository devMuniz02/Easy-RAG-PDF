# Easy Rag Pdf

> Your PDF library, now with a brain. 🧠 Stop wasting hours digging through folders; this dead-simple RAG interface turns your local files into an interactive knowledge base. You control the intelligence: simply point the API connection to a local endpoint for 100% air-gapped privacy where no data ever leaves your machine, or link to a cloud provider for maximum reasoning power. No forced uploads, no subscriptions, and zero data leaks—just drop your PDFs, connect your model, and start talking to your data.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/devMuniz02/Easy-RAG-PDF)](https://github.com/devMuniz02/Easy-RAG-PDF/issues)
[![GitHub stars](https://img.shields.io/github/stars/devMuniz02/Easy-RAG-PDF)](https://github.com/devMuniz02/Easy-RAG-PDF/stargazers)

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Configuration](#configuration)
- [Cleanup](#cleanup)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## ✨ Features

- **PDF Upload & Processing**: Upload multiple PDF documents and automatically extract text for analysis
- **Intelligent Chat**: Ask questions about your documents and get context-aware answers using RAG (Retrieval-Augmented Generation)
- **Privacy-First Design**: Choose between Local Mode (100% private, runs on your machine) and API Mode (maximum AI intelligence)
- **File Management**: Easily manage uploaded files, view page counts, and remove documents as needed
- **Web-Based Interface**: User-friendly web UI for seamless interaction
- **Persistent Storage**: Uploaded files and processed data are saved for future sessions
- **Source Citations**: Answers include clickable links to relevant document sections

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- For Local Mode: A local LLM server (e.g., LM Studio, Ollama, or similar) running on `http://localhost:1234/v1/chat/completions`
- For API Mode: Internet connection and API access to LLM providers

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/devMuniz02/Easy-RAG-PDF.git

# Navigate to the project directory
cd Easy-RAG-PDF

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Getting Started

After cloning this repository, follow these steps to set up and run the application:

## 📁 Project Structure

```
Easy-RAG-PDF/
├── assets/                 # Static assets (images, icons, etc.)
├── data/                   # Data files and datasets
├── docs/                   # Documentation files
├── notebooks/              # Jupyter notebooks for analysis and prototyping
├── scripts/                # Utility scripts and automation tools
├── src/                    # Source code
├── tests/                  # Unit tests and test files
├── LICENSE                 # License file
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

### Directory Descriptions

- **`assets/`**: Static assets (images, icons, etc.)
- **`data/`**: Processed document data, FAISS index, and metadata
- **`docs/`**: Documentation files
- **`notebooks/`**: Jupyter notebooks for analysis and prototyping
- **`scripts/`**: Utility scripts and automation tools
- **`src/`**: Main source code (Flask app and RAG processor)
- **`tests/`**: Unit tests and test files
- **`uploads/`**: Uploaded PDF files (created automatically)
- **`LICENSE`**: MIT License file
- **`README.md`**: Project documentation
- **`requirements.txt`**: Python dependencies
- **`cleanup.py`**: Script to clear all processed data and uploaded files

## 📖 Usage

### Starting the Application

```bash
# Navigate to the src directory
cd src

# Run the Flask application
python app.py
```

The application will start on `http://localhost:5000`

### Basic Usage

1. **Upload PDFs**: Click the "Upload PDFs" button and select one or more PDF files
2. **Select Files**: Choose which uploaded files to include in your chat session
3. **Configure Mode**: 
   - **Local Mode**: Uses your local LLM server for maximum privacy
   - **API Mode**: Connects to external LLM APIs for enhanced capabilities
4. **Start Chatting**: Ask questions about your documents in natural language

### Advanced Usage

- **File Management**: View uploaded files, see page counts, and remove files you no longer need
- **Persistent Sessions**: Your uploaded files and processed data are saved between sessions
- **Source Citations**: Click on citation links in responses to view relevant document sections
- **Cleanup**: Use `python cleanup.py` to clear all processed data and uploaded files

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory for custom configuration:

```env
# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=True

# LLM API Configuration (for API Mode)
API_URL=https://api.openai.com/v1/chat/completions
MODEL=gpt-3.5-turbo
API_KEY=your_api_key_here

# Local LLM Configuration (for Local Mode)
LOCAL_API_URL=http://localhost:1234/v1/chat/completions
LOCAL_MODEL=local-model
```

### Application Settings

- **Upload Limit**: Maximum 100MB per file
- **Supported Formats**: PDF files only
- **Chunk Size**: 1000 characters with 200 character overlap for text processing
- **Embedding Model**: Uses `all-MiniLM-L6-v2` for document embeddings

## � Cleanup

To clear all processed data and uploaded files:

```bash
python cleanup.py
```

This will remove:
- FAISS index and document embeddings
- Processed document metadata
- All uploaded PDF files

**Warning**: This action cannot be undone. Use with caution.

## �🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies (if available)
pip install -r requirements.txt

# Run the application in development mode
cd src
python app.py

# For testing PDF processing
# Place test PDFs in the uploads/ directory
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Links:**
- **GitHub:** [https://github.com/devMuniz02/](https://github.com/devMuniz02/)
- **LinkedIn:** [https://www.linkedin.com/in/devmuniz](https://www.linkedin.com/in/devmuniz)
- **Hugging Face:** [https://huggingface.co/manu02](https://huggingface.co/manu02)
- **Portfolio:** [https://devmuniz02.github.io/](https://devmuniz02.github.io/)

Project Link: [https://github.com/devMuniz02/Easy-RAG-PDF](https://github.com/devMuniz02/Easy-RAG-PDF)

---

⭐ If you find this project helpful, please give it a star!
