# IRDAI Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for querying IRDAI (Insurance Regulatory and Development Authority of India) regulatory documents. This application uses semantic search and large language models to provide accurate, cited answers from IRDAI circulars and regulations.

## 🎯 Features

- **Semantic Search**: Uses OpenAI embeddings and FAISS for fast, accurate document retrieval
- **Accurate Answers**: GPT-4.1-mini powered responses based on retrieved document chunks
- **Source Citations**: Every answer includes citations to the source document and chunk
- **Conversational**: Maintains conversation history for follow-up questions
- **Web Interface**: User-friendly Streamlit-based web application
- **Comprehensive Coverage**: Indexes 94+ IRDAI regulatory documents

## 🏗️ Architecture

This project implements a RAG (Retrieval-Augmented Generation) pipeline:

1. **Document Processing**: PDFs are extracted, cleaned, and chunked
2. **Vector Indexing**: Text chunks are embedded and indexed using FAISS
3. **Query Processing**: User queries are embedded and matched against the index
4. **Answer Generation**: Relevant chunks are used as context for LLM-generated answers

<img width="1356" height="517" alt="Screenshot 2025-11-24 at 6 15 08 PM" src="https://github.com/user-attachments/assets/d95a9a19-29c5-4c10-9553-8f82f7af9198" />


### Technology Stack

- **Embeddings**: OpenAI `text-embedding-3-small` (1536 dimensions)
- **LLM**: OpenAI GPT-4.1-mini for answer generation
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **Web Framework**: Streamlit
- **PDF Processing**: PyMuPDF (fitz)
- **Text Processing**: ftfy, regex

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- (Optional) Tesseract OCR for PDFs with scanned content

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd irdai-chatbot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Prepare PDF documents**
   Place IRDAI PDF files in the `irdai_pdfs/` directory.

## 📖 Usage

### Step 1: Extract Text from PDFs

Extract and clean text from PDF files:

```bash
python scripts/pdf_text.py
```

This will:
- Extract text from all PDFs in `irdai_pdfs/`
- Use OCR fallback for scanned documents
- Save cleaned text files to `irdai_pdfs/texts/`

### Step 2: Chunk the Documents

Split documents into overlapping chunks for better retrieval:

```bash
python scripts/chunk_texts.py
```

This creates:
- Chunked text files in `irdai_pdfs/chunks/` (JSONL format)
- Each chunk contains ~450 tokens with 50 token overlap

### Step 3: Build the Vector Index

Create embeddings and build the search index:

```bash
python scripts/index.py
```

This will:
- Generate embeddings for all chunks using OpenAI API
- Build a FAISS vector index
- Save index files to `irdai_pdfs/index/`

**Note**: This step requires OpenAI API credits and may take time depending on the number of documents.

### Step 4: Run the Chatbot

Launch the Streamlit web interface:

```bash
streamlit run app/ui.py
```

The application will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
irdai-chatbot/
├── app/
│   ├── __init__.py
│   ├── ui.py                 # Streamlit web interface
│   └── prompt_template.py    # Prompt building logic
├── scripts/
│   ├── pdf_text.py          # PDF to text extraction
│   ├── chunk_texts.py       # Text chunking
│   ├── index.py             # Vector index creation
│   ├── gpt_cleaner.py       # (Optional) GPT-based text cleaning
│   └── fetch-pdfs.py        # (Optional) PDF download script
├── irdai_pdfs/
│   ├── *.pdf                # Original PDF documents
│   ├── texts/               # Extracted text files
│   ├── chunks/              # Chunked JSONL files
│   └── index/               # FAISS index and metadata
│       ├── faiss.index      # Vector index file
│       └── meta.jsonl       # Chunk metadata mapping
├── evaluation_set.txt       # Q&A pairs for evaluation
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
└── README.md               # This file
```

## 🔄 Workflow

### Data Pipeline

```
PDF Files
    ↓
[pdf_text.py] → Extract & Clean Text
    ↓
Text Files
    ↓
[chunk_texts.py] → Split into Overlapping Chunks
    ↓
Chunk Files (JSONL)
    ↓
[index.py] → Generate Embeddings → Build FAISS Index
    ↓
Vector Index (Ready for Querying)
```

### Query Pipeline

```
User Question
    ↓
Embed Query (OpenAI)
    ↓
Search FAISS Index → Retrieve Top-K Chunks
    ↓
Build Prompt (chunks + history + question)
    ↓
Generate Answer (GPT-4o-mini)
    ↓
Extract Citations → Display to User
```

## ⚙️ Configuration

### Chunking Parameters

Edit `scripts/chunk_texts.py`:
- `max_tokens`: Maximum tokens per chunk (default: 450)
- `overlap`: Token overlap between chunks (default: 50)

### Retrieval Parameters

Edit `app/ui.py`:
- `k`: Number of chunks to retrieve (default: 4)
- `max_tokens`: Maximum tokens in response (default: 400)
- `temperature`: LLM temperature (default: 0.0)

### Model Configuration

Edit `app/ui.py` and `scripts/index.py`:
- Embedding model: `text-embedding-3-small`
- Chat model: `gpt-4o-mini` (or `gpt-4.1-mini`)

## 📊 Evaluation

The project includes an evaluation set (`evaluation_set.txt`) with 109 question-answer pairs extracted from the IRDAI documents. Each entry contains:

- `DOC_ID`: Source document identifier
- `QUESTION`: Content-based question about regulatory provisions
- `ANSWER`: Ground truth answer from the document

Use this set to evaluate the chatbot's accuracy and performance.

### Evaluation Set Format

```
DOC_ID: 1
QUESTION: What are the requirements for The board policy on commission structures for intermediaries?
ANSWER: The board policy on commission structures for intermediaries shall, at the minimum, include the following key elements...
--------------------------------------------------------------------------------
```

## 🔍 How It Works

### 1. Document Processing

- **PDF Extraction**: Uses PyMuPDF to extract text directly from PDFs
- **OCR Fallback**: Automatically uses Tesseract OCR if direct extraction fails
- **Text Cleaning**: Removes Hindi characters, fixes encoding issues, normalizes whitespace

### 2. Chunking Strategy

- Documents are split into overlapping chunks (~450 tokens each)
- Overlap ensures context is preserved across chunk boundaries
- Each chunk is stored with metadata: `doc_id`, `chunk_id`, `position`

### 3. Vector Search

- Text chunks are converted to 1536-dimensional vectors using OpenAI embeddings
- FAISS IndexFlatL2 provides fast L2 distance-based similarity search
- Query embedding is matched against all chunk embeddings

### 4. Answer Generation

- Top-K most similar chunks are retrieved
- Chunks are formatted with source information
- GPT-4o-mini generates concise answers based on retrieved context
- Citations are automatically extracted by matching sentences

## 🛠️ Troubleshooting

### Issue: OCR not working
- Install Tesseract: `brew install tesseract` (macOS) or `apt-get install tesseract-ocr` (Linux)
- Install Python packages: `pip install pytesseract pillow`

### Issue: OpenAI API errors
- Check your API key in `.env` file
- Verify you have sufficient API credits
- Check rate limits (script includes 0.1s delay between batches)

### Issue: FAISS index not found
- Run `python scripts/index.py` to build the index
- Ensure `irdai_pdfs/index/` directory exists

### Issue: Empty or poor quality answers
- Check if chunks contain meaningful text
- Verify retrieved chunks are relevant to the query
- Adjust `k` parameter to retrieve more chunks

## 📝 Notes

- The first run of `index.py` will take time and cost API credits
- FAISS index is cached after first load for faster startup
- Conversation history is maintained in Streamlit session state
- Citations are extracted by sentence matching (may not be perfect)
