import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import BookList from './components/BookList';
import BookDetail from './components/BookDetail';
import UploadBook from './components/UploadBook';

const App: React.FC = () => {
  return (
    <div>
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
        <div className="container">
          <Link className="navbar-brand" to="/">Book Summarizer</Link>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav">
              <li className="nav-item">
                <Link className="nav-link" to="/">Home</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/upload">Upload Book</Link>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      <div className="container mt-4">
        <Routes>
          <Route path="/" element={<BookList />} />
          <Route path="/books/:bookId" element={<BookDetail />} />
          <Route path="/upload" element={<UploadBook />} />
        </Routes>
      </div>
    </div>
  );
};

export default App; 