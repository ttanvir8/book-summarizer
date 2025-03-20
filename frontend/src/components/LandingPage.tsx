import React from 'react';
import GoogleLogin from './GoogleLogin';

const LandingPage: React.FC = () => {
  return (
    <div className="container my-5">
      <div className="row">
        <div className="col-md-8 offset-md-2 text-center">
          <h1 className="display-4 mb-4">Book Summarizer</h1>
          <p className="lead mb-5">
            Transform your reading experience with our AI-powered book summary tool.
            Upload your PDFs and get instant, comprehensive chapter summaries.
          </p>
          
          <div className="row mb-5">
            <div className="col-md-4">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body text-center p-4">
                  <h3 className="h5 mb-3">Upload Books</h3>
                  <p className="card-text">Upload your PDF books to our platform for processing.</p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body text-center p-4">
                  <h3 className="h5 mb-3">Extract Chapters</h3>
                  <p className="card-text">Our system automatically extracts chapters from your books.</p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body text-center p-4">
                  <h3 className="h5 mb-3">Generate Summaries</h3>
                  <p className="card-text">Get AI-powered summaries for each chapter with a single click.</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="d-flex justify-content-center mt-4">
            <GoogleLogin />
          </div>
          
          <div className="mt-5 text-muted">
            <p>
              <small>
                Sign in to access your books and summaries. All your data is securely stored and accessible only to you.
              </small>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage; 