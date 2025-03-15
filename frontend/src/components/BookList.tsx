import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAllBooks, deleteBook, Book } from '../services/api';

const BookList: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBooks = async () => {
    try {
      setLoading(true);
      const data = await getAllBooks();
      setBooks(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch books. Please try again later.');
      console.error('Error fetching books:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  // Format date safely
  const formatDate = (dateString: string): string => {
    if (!dateString) return 'N/A';
    
    try {
      // Handle ISO string format from Django (e.g., "2023-03-13T12:34:56.789Z")
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return 'Invalid Date Format';
      }
      return date.toLocaleDateString();
    } catch (error) {
      console.error('Error formatting date:', error);
      return 'Date Error';
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this book?')) {
      try {
        await deleteBook(id);
        setBooks(books.filter(book => book.id !== id));
      } catch (err) {
        setError('Failed to delete book. Please try again later.');
        console.error('Error deleting book:', err);
      }
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Books</h1>
        <Link to="/upload" className="btn btn-primary">Upload New Book</Link>
      </div>

      {books.length === 0 ? (
        <div className="alert alert-info">
          No books found. Please upload a book to get started.
        </div>
      ) : (
        <div className="row">
          {books.map(book => (
            <div className="col-md-4 mb-4" key={book.id}>
              <div className="card h-100">
                <div className="card-body">
                  <h5 className="card-title">{book.title}</h5>
                  <p className="card-text">
                    <small className="text-muted">Added on: {formatDate(book.created_at)}</small>
                  </p>
                </div>
                <div className="card-footer bg-transparent border-top-0">
                  <div className="d-flex justify-content-between">
                    <Link to={`/books/${book.id}`} className="btn btn-sm btn-primary">
                      View Details
                    </Link>
                    <button 
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(book.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default BookList; 