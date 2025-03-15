import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadBook } from '../services/api';

const UploadBook: React.FC = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files ? e.target.files[0] : null;
    
    if (!selectedFile) {
      setFile(null);
      setFileError('Please select a file.');
      return;
    }
    
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setFile(null);
      setFileError('Only PDF files are supported.');
      return;
    }
    
    setFile(selectedFile);
    setFileError(null);
    
    // If title is empty, use the file name without extension as default
    if (!title) {
      const fileName = selectedFile.name.replace(/\.[^/.]+$/, '');
      setTitle(fileName);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!file) {
      setFileError('Please select a PDF file.');
      return;
    }
    
    try {
      setUploading(true);
      setUploadProgress(0);
      
      // Create form data
      const formData = new FormData();
      if (title) {
        formData.append('title', title);
      }
      formData.append('pdf_file', file);
      
      // Simulate upload progress (in a real app, you'd use axios progress events)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 5;
        });
      }, 200);
      
      const uploadedBook = await uploadBook(formData);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Navigate to the book detail page
      setTimeout(() => {
        navigate(`/books/${uploadedBook.id}`);
      }, 1000);
      
    } catch (err) {
      setError('Failed to upload book. Please try again later.');
      console.error('Error uploading book:', err);
      setUploading(false);
    }
  };

  return (
    <div>
      <h1 className="mb-4">Upload Book</h1>
      
      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}
      
      {uploading ? (
        <div className="card">
          <div className="card-body">
            <h5 className="card-title">Uploading Book</h5>
            <div className="mb-3">
              <div className="progress">
                <div 
                  className="progress-bar progress-bar-striped progress-bar-animated" 
                  role="progressbar" 
                  style={{ width: `${uploadProgress}%` }}
                  aria-valuenow={uploadProgress} 
                  aria-valuemin={0} 
                  aria-valuemax={100}
                >
                  {uploadProgress}%
                </div>
              </div>
            </div>
            <p className="card-text">
              {uploadProgress < 100 ? 
                'Please wait while we upload and process your book...' :
                'Upload complete! Redirecting to book details...'
              }
            </p>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="title" className="form-label">Book Title (Optional)</label>
                <input
                  type="text"
                  className="form-control"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="If left blank, the filename will be used"
                />
                <div className="form-text">If left blank, the filename will be used.</div>
              </div>
              
              <div className="mb-3">
                <label htmlFor="pdf_file" className="form-label">PDF File</label>
                <input
                  type="file"
                  className={`form-control ${fileError ? 'is-invalid' : ''}`}
                  id="pdf_file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  required
                />
                {fileError && (
                  <div className="invalid-feedback">
                    {fileError}
                  </div>
                )}
                <div className="form-text">Only PDF files are supported.</div>
              </div>
              
              <div className="d-grid gap-2">
                <button type="submit" className="btn btn-primary" disabled={!file || uploading}>
                  Upload Book
                </button>
                <button type="button" className="btn btn-outline-secondary" onClick={() => navigate('/')}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadBook; 