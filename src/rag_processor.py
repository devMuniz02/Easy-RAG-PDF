import os
import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import requests
import json
from typing import List, Tuple
import re

class RAGProcessor:
    def __init__(self, embedding_model='all-MiniLM-L6-v2', data_dir='data'):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.index = None
        self.documents = []
        self.document_paths = []  # Store full paths
        self.chunks = []
        self.chunk_size = 1000
        self.overlap = 200
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Try to load existing data
        self.load_data()

    def save_data(self):
        """Save the FAISS index and document data to disk."""
        try:
            if self.index is not None:
                # Save FAISS index
                faiss.write_index(self.index, os.path.join(self.data_dir, 'faiss_index.idx'))
                
                # Save document data
                data = {
                    'documents': self.documents,
                    'document_paths': self.document_paths,
                    'chunks': self.chunks
                }
                with open(os.path.join(self.data_dir, 'documents.json'), 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def save_uploaded_files_list(self, uploaded_files_data):
        """Save the list of uploaded files and their metadata, avoiding duplicates."""
        try:
            # Load existing files
            existing_files = self.load_uploaded_files_list()
            
            # Create a set of existing file identifiers (name + size + lastModified)
            existing_ids = set()
            for file_data in existing_files:
                file_id = f"{file_data['name']}_{file_data['size']}_{file_data['lastModified']}"
                existing_ids.add(file_id)
            
            # Filter out duplicates
            new_files = []
            duplicates = 0
            
            for file_data in uploaded_files_data:
                file_id = f"{file_data['name']}_{file_data['size']}_{file_data['lastModified']}"
                if file_id not in existing_ids:
                    new_files.append(file_data)
                else:
                    duplicates += 1
            
            # Combine existing and new files
            all_files = existing_files + new_files
            
            # Save the combined list
            with open(os.path.join(self.data_dir, 'uploaded_files.json'), 'w') as f:
                json.dump(all_files, f, indent=2)
            
            return {
                'saved': len(new_files),
                'duplicates': duplicates,
                'total': len(all_files)
            }
            
        except Exception as e:
            print(f"Error saving uploaded files list: {e}")
            return {
                'saved': 0,
                'duplicates': 0,
                'total': len(existing_files) if 'existing_files' in locals() else 0,
                'error': str(e)
            }

    def load_uploaded_files_list(self):
        """Load the list of uploaded files and their metadata."""
        try:
            file_path = os.path.join(self.data_dir, 'uploaded_files.json')
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading uploaded files list: {e}")
        return []

    def load_data(self):
        """Load the FAISS index and document data from disk."""
        try:
            index_path = os.path.join(self.data_dir, 'faiss_index.idx')
            data_path = os.path.join(self.data_dir, 'documents.json')
            
            if os.path.exists(index_path) and os.path.exists(data_path):
                # Load FAISS index
                self.index = faiss.read_index(index_path)
                
                # Load document data
                with open(data_path, 'r') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                    self.document_paths = data.get('document_paths', [])
                    self.chunks = data.get('chunks', [])
                    
                print(f"Loaded {len(self.documents)} documents from disk")
        except Exception as e:
            print(f"Error loading data: {e}")
            # Initialize empty if loading fails
            self.index = None
            self.documents = []
            self.document_paths = []
            self.chunks = []

    def get_pdf_page_count(self, pdf_path: str) -> int:
        """Get the number of pages in a PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception as e:
            print(f"Error getting page count for {pdf_path}: {e}")
            return 0

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
        return text

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.overlap
        return chunks

    def process_pdfs(self, pdf_paths: List[str]) -> bool:
        """Process multiple PDFs: extract text, create chunks, and build vector index."""
        try:
            all_chunks = []
            all_documents = []
            all_paths = []

            for pdf_path in pdf_paths:
                text = self.extract_text_from_pdf(pdf_path)
                if text.strip():
                    chunks = self.chunk_text(text)
                    all_chunks.extend(chunks)
                    all_documents.extend([os.path.basename(pdf_path)] * len(chunks))
                    all_paths.extend([pdf_path] * len(chunks))

            if not all_chunks:
                return False

            # Create embeddings
            embeddings = self.embedding_model.encode(all_chunks, show_progress_bar=True)

            # Build FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(np.array(embeddings).astype('float32'))

            self.chunks = all_chunks
            self.documents = all_documents
            self.document_paths = all_paths

            # Save data to disk
            self.save_data()

            return True
        except Exception as e:
            print(f"Error processing PDFs: {e}")
            return False

    def remove_file(self, file_path: str) -> bool:
        """Remove a file and its embeddings from the index."""
        try:
            file_path = file_path.replace('/', os.sep).replace('\\', os.sep)
            if file_path not in self.document_paths:
                return False
            
            # Find all indices for this file
            indices_to_remove = []
            for i, path in enumerate(self.document_paths):
                if path == file_path:
                    indices_to_remove.append(i)
            
            if not indices_to_remove:
                return False
            
            # Remove from all lists (in reverse order to maintain indices)
            for i in sorted(indices_to_remove, reverse=True):
                del self.chunks[i]
                del self.documents[i]
                del self.document_paths[i]
            
            # Rebuild FAISS index if we have remaining documents
            if self.chunks:
                embeddings = self.embedding_model.encode(self.chunks, show_progress_bar=True)
                dimension = embeddings.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
                self.index.add(np.array(embeddings).astype('float32'))
            else:
                self.index = None
            
            # Save updated data
            self.save_data()
            
            return True
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")
            return False

    def retrieve_relevant_chunks(self, query: str, top_k: int = 5, selected_files: List[str] = None) -> List[Tuple[str, str, str, float]]:
        """Retrieve the most relevant chunks for a query, optionally filtered by selected files."""
        if self.index is None or not self.chunks:
            return []

        # Normalize selected_files to use OS path separator
        if selected_files:
            selected_files = [f.replace('/', os.sep).replace('\\', os.sep) for f in selected_files]

        query_embedding = self.embedding_model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                doc = self.documents[idx]
                path = self.document_paths[idx]
                
                # If selected_files is provided, only include chunks from selected files
                if selected_files and path not in selected_files:
                    continue
                    
                # Convert distance to similarity score (FAISS returns L2 distance, convert to cosine similarity)
                similarity_percent = float(f"{100.0 / (1.0 + distances[0][i]):.2f}")  # Simple conversion for display
                results.append((chunk, doc, path, similarity_percent))

        return results

    def chat(self, message: str, api_url: str, model: str, selected_files: List[str] = None) -> dict:
        """Chat with the RAG system using the provided LLM API, optionally filtered by selected files."""
        # Retrieve relevant context
        relevant_chunks = self.retrieve_relevant_chunks(message, selected_files=selected_files)

        if not relevant_chunks:
            return {
                "answer": "No relevant information found in the selected PDFs.",
                "sources": []
            }

        # Build context from relevant chunks
        context = "\n\n".join([f"From {doc}: {chunk}" for chunk, doc, path, score in relevant_chunks])

        # Create unique sources list with additional metadata
        unique_sources = []
        seen_files = set()
        for chunk, doc, path, score in relevant_chunks:
            if doc not in seen_files:
                # Get file size and page count
                file_size = os.path.getsize(path) if os.path.exists(path) else 0
                page_count = self.get_pdf_page_count(path)
                
                unique_sources.append({
                    "name": doc, 
                    "path": path, 
                    "file_size": file_size,
                    "page_count": page_count,
                    "similarity_percent": float(score)
                })
                seen_files.add(doc)

        # Sort sources by similarity percent (highest first)
        unique_sources.sort(key=lambda x: x["similarity_percent"], reverse=True)

        # Prepare the prompt
        prompt = f"""You are a helpful assistant that answers questions based on the provided context from PDF documents.

Context:
{context}

Question: {message}

Answer the question based only on the provided context. If the context doesn't contain enough information to answer the question, say so.

When referencing information from specific documents, use numbered citations like [1], [2], etc. corresponding to the sources provided."""

        # Call the LLM API
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }

            response = requests.post(api_url, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            answer = result['choices'][0]['message']['content'].strip()

            # Add href to sources
            for source in unique_sources:
                source["href"] = f"/uploads/{os.path.basename(source['path'])}"

            # Replace filename mentions with links
            for i, source in enumerate(unique_sources):
                number = str(i + 1)
                href = source["href"]
                filename = source["name"]
                answer = re.sub(r'\b' + re.escape(filename) + r'\b', f'<a href="{href}" target="_blank">[{number}]</a>', answer)

            # Replace citations with links
            for i, source in enumerate(unique_sources):
                number = str(i + 1)
                href = source["href"]
                answer = re.sub(r'\[' + re.escape(number) + r'\]', f'<a href="{href}" target="_blank">[{number}]</a>', answer)

            return {
                "answer": answer,
                "sources": unique_sources
            }

        except requests.exceptions.RequestException as e:
            return {
                "answer": f"Error calling LLM API: {str(e)}",
                "sources": []
            }
        except (KeyError, IndexError) as e:
            return {
                "answer": f"Error parsing LLM response: {str(e)}",
                "sources": []
            }