import React from 'react';
import GoogleLogin from './GoogleLogin';

const LandingPage: React.FC = () => {
  return (
    <div className="container my-5">
      <div className="row">
        <div className="col-md-8 offset-md-2 text-center">
          <h1 className="display-4 mb-4">Project Orion</h1>
          <p className="lead mb-5">
            Knowledge is compression. 
            Project Orion will will help you compress all the information you encounter everyday 
            in compressed and more manageable form. But currently you can only use it to compress (summarize) your books.
            In the future, you will be able to compress every single information you encounter everyday from web and your 
            personal notes in compressed and more manageable form. Your ultimate knowledge base refined for you with all the neuances of you
            , your personal assistant 
            that will be second brain predicting your knowledge and information needs allowing you to be most productive and efficient.
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
                  <h3 className="h5 mb-3">Compression Rate</h3>
                  <p className="card-text">Change your compression rate in two mode currently detailed and concise</p>
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