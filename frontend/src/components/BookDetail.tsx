import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Split from 'react-split';
import { 
  getBook, 
  getChapters, 
  summarizeChapter, 
  deleteBook,
  regenerateSummary,
  getChapterSummaries,
  setActiveSummary,
  availablePrompts,
  Book, 
  Chapter,
  ChapterSummary,
  Prompt 
} from '../services/api';
import './BookDetail.css';

interface RouteParams {
  bookId: string;
  [key: string]: string;
}

const BookDetail: React.FC = () => {
  const { bookId } = useParams<RouteParams>();
  const navigate = useNavigate();
  const [book, setBook] = useState<Book | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [summarizing, setSummarizing] = useState<Record<number, boolean>>({});
  const [viewMode, setViewMode] = useState<'content' | 'summary'>('summary');
  const [selectedChapter, setSelectedChapter] = useState<Chapter | null>(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [availableSummaries, setAvailableSummaries] = useState<ChapterSummary[]>([]);
  const [currentSummaryIndex, setCurrentSummaryIndex] = useState<number>(0);
  const [selectedPrompt, setSelectedPrompt] = useState<string>('default');
  const [customPromptText, setCustomPromptText] = useState<string>('');
  const [showCustomPromptModal, setShowCustomPromptModal] = useState<boolean>(false);

  // Set default prompt on component mount
  useEffect(() => {
    // Find the default prompt in availablePrompts
    const defaultPrompt = availablePrompts.find(prompt => prompt.id === 'default');
    if (defaultPrompt) {
      setSelectedPrompt(defaultPrompt.id);
    }
  }, []);

  useEffect(() => {
    const fetchBookDetails = async () => {
      try {
        setLoading(true);
        if (!bookId) return;
        
        const bookData = await getBook(parseInt(bookId));
        setBook(bookData);
        
        const allChapters = await getChapters();
        const bookChapters = allChapters.filter(chapter => chapter.book === parseInt(bookId));
        setChapters(bookChapters);
        
        // Set the first chapter as selected by default
        if (bookChapters.length > 0) {
          setSelectedChapter(bookChapters[0]);
        }
        
        setError(null);
      } catch (err) {
        setError('Failed to fetch book details. Please try again later.');
        console.error('Error fetching book details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchBookDetails();
  }, [bookId]);

  // Load summaries when a chapter is selected
  useEffect(() => {
    const fetchSummaries = async () => {
      if (selectedChapter) {
        try {
          // Check if the chapter has summaries via the API
          const summaries = await getChapterSummaries(selectedChapter.id);
          setAvailableSummaries(summaries);
          
          // Find index of active summary
          if (selectedChapter.active_summary) {
            const activeIndex = summaries.findIndex(s => s.id === selectedChapter.active_summary?.id);
            setCurrentSummaryIndex(activeIndex >= 0 ? activeIndex : 0);
          } else {
            setCurrentSummaryIndex(0);
          }
        } catch (err) {
          console.error('Error fetching summaries:', err);
          // If API fails, try to use the embedded summaries from the chapter object
          if (selectedChapter.summaries?.length > 0) {
            setAvailableSummaries(selectedChapter.summaries);
            
            // Find index of active summary
            if (selectedChapter.active_summary) {
              const activeIndex = selectedChapter.summaries.findIndex(s => s.id === selectedChapter.active_summary?.id);
              setCurrentSummaryIndex(activeIndex >= 0 ? activeIndex : 0);
            } else {
              setCurrentSummaryIndex(0);
            }
          } else {
            setAvailableSummaries([]);
            setCurrentSummaryIndex(0);
          }
        }
      }
    };
    
    fetchSummaries();
  }, [selectedChapter]);

  // Debug useEffect to log compression ratio when selectedChapter changes
  useEffect(() => {
    if (selectedChapter) {
      console.log('Selected chapter:', selectedChapter);
      console.log('Compression ratio:', selectedChapter.compression_ratio);
      console.log('Available summaries:', availableSummaries);
      console.log('Current summary index:', currentSummaryIndex);
    }
  }, [selectedChapter, availableSummaries, currentSummaryIndex]);

  const handleSummarize = async (chapterNumber: number) => {
    if (!bookId) return;
    
    try {
      setSummarizing({ ...summarizing, [chapterNumber]: true });
      const updatedChapter = await summarizeChapter(parseInt(bookId), chapterNumber, selectedPrompt);
      
      // Log the response from the API to debug
      console.log('API response from summarize:', updatedChapter);
      
      // Update chapters state with new data
      setChapters(chapters.map(chapter => 
        chapter.id === updatedChapter.id ? updatedChapter : chapter
      ));
      
      // Update selectedChapter if this is the one that was summarized
      if (selectedChapter?.id === updatedChapter.id) {
        console.log('Updating selected chapter with new data including compression ratio:', updatedChapter.compression_ratio);
        setSelectedChapter(updatedChapter);
      }
      
      // Refresh summaries for this chapter
      if (updatedChapter.summaries?.length > 0) {
        setAvailableSummaries(updatedChapter.summaries);
        setCurrentSummaryIndex(0); // Set to the first (newest) summary
      }
    } catch (err) {
      setError('Failed to generate summary. Please try again later.');
      console.error('Error generating summary:', err);
    } finally {
      setSummarizing({ ...summarizing, [chapterNumber]: false });
    }
  };

  const handleRegenerateSummary = async (chapterNumber: number) => {
    if (!bookId) return;
    
    try {
      setSummarizing({ ...summarizing, [chapterNumber]: true });
      const updatedChapter = await regenerateSummary(parseInt(bookId), chapterNumber, selectedPrompt);
      
      // Update chapters state with new data
      setChapters(chapters.map(chapter => 
        chapter.id === updatedChapter.id ? updatedChapter : chapter
      ));
      
      // Update selectedChapter if this is the one that was regenerated
      if (selectedChapter?.id === updatedChapter.id) {
        setSelectedChapter(updatedChapter);
      }
      
      // Refresh summaries for this chapter
      if (updatedChapter.summaries?.length > 0) {
        setAvailableSummaries(updatedChapter.summaries);
        setCurrentSummaryIndex(0); // Set to the first (newest) summary
      }
    } catch (err) {
      setError('Failed to regenerate summary. Please try again later.');
      console.error('Error regenerating summary:', err);
    } finally {
      setSummarizing({ ...summarizing, [chapterNumber]: false });
    }
  };
  
  const handleCycleSummary = async (direction: 'next' | 'prev') => {
    if (!selectedChapter || availableSummaries.length <= 1) return;
    
    let newIndex: number;
    if (direction === 'next') {
      newIndex = (currentSummaryIndex + 1) % availableSummaries.length;
    } else {
      newIndex = (currentSummaryIndex - 1 + availableSummaries.length) % availableSummaries.length;
    }
    
    try {
      const summaryId = availableSummaries[newIndex].id;
      const updatedChapter = await setActiveSummary(selectedChapter.id, summaryId);
      
      // Update chapters state with new data
      setChapters(chapters.map(chapter => 
        chapter.id === updatedChapter.id ? updatedChapter : chapter
      ));
      
      // Update selected chapter
      setSelectedChapter(updatedChapter);
      
      // Update current index
      setCurrentSummaryIndex(newIndex);
    } catch (err) {
      setError('Failed to switch summary. Please try again later.');
      console.error('Error switching summary:', err);
    }
  };

  const handleDelete = async () => {
    if (!bookId) return;
    
    if (window.confirm('Are you sure you want to delete this book?')) {
      try {
        await deleteBook(parseInt(bookId));
        navigate('/');
      } catch (err) {
        setError('Failed to delete book. Please try again later.');
        console.error('Error deleting book:', err);
      }
    }
  };

  // Helper to get current summary text and info
  const getCurrentSummary = () => {
    if (!selectedChapter) return null;
    
    if (availableSummaries.length > 0 && currentSummaryIndex < availableSummaries.length) {
      return availableSummaries[currentSummaryIndex];
    }
    
    // Fallback to the chapter's summary field for backward compatibility
    if (selectedChapter.summary) {
      return {
        id: -1,
        summary_text: selectedChapter.summary,
        compression_ratio: selectedChapter.compression_ratio,
        prompt_used: 'Default prompt',
        created_at: new Date().toISOString() // Use current date as fallback
      };
    }
    
    return null;
  };

  // Handle prompt selection change
  const handlePromptChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newPromptId = e.target.value;
    setSelectedPrompt(newPromptId);
    
    // If custom prompt is selected, show the modal
    if (newPromptId === 'custom') {
      // Initialize with existing custom prompt text if available
      const customPrompt = availablePrompts.find(p => p.id === 'custom');
      if (customPrompt && customPrompt.text) {
        setCustomPromptText(customPrompt.text);
      } else {
        // Initialize with default prompt as a starting point
        const defaultPrompt = availablePrompts.find(p => p.id === 'default');
        if (defaultPrompt) {
          setCustomPromptText(defaultPrompt.text);
        }
      }
      setShowCustomPromptModal(true);
    }
  };

  // Save custom prompt
  const handleSaveCustomPrompt = () => {
    // Find the custom prompt in the available prompts array
    const customPromptIndex = availablePrompts.findIndex(p => p.id === 'custom');
    if (customPromptIndex !== -1) {
      // Update the custom prompt text
      availablePrompts[customPromptIndex].text = customPromptText;
    }
    setShowCustomPromptModal(false);
  };

  // Close custom prompt modal without saving
  const handleCloseCustomPromptModal = () => {
    // If no custom prompt text is set, revert to default prompt
    if (!customPromptText.trim() && selectedPrompt === 'custom') {
      setSelectedPrompt('default');
    }
    setShowCustomPromptModal(false);
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

  if (!book) {
    return (
      <div className="alert alert-warning" role="alert">
        Book not found.
      </div>
    );
  }

  const currentSummary = getCurrentSummary();

  return (
    <div className="d-flex flex-column vh-100">
      {/* Header */}
      <div className="border-bottom px-2 py-3">
        <div className="d-flex justify-content-between align-items-center">
          <div>
            <Link to="/" className="btn btn-sm btn-outline-secondary">
              &larr; Back to Books
            </Link>
            <h1 className="h3 mb-0 ms-3 d-inline-block">{book.title}</h1>
          </div>
          <button className="btn btn-danger" onClick={handleDelete}>
            Delete Book
          </button>
        </div>
      </div>

      {/* Custom Prompt Modal */}
      {showCustomPromptModal && (
        <div className="modal d-block" tabIndex={-1} role="dialog" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Custom Summary Prompt</h5>
                <button type="button" className="btn-close" aria-label="Close" onClick={handleCloseCustomPromptModal}></button>
              </div>
              <div className="modal-body">
                <p className="text-muted mb-3">
                  Enter your custom prompt for generating the summary. The text will be sent to the AI model to guide the summary generation process.
                </p>
                <textarea
                  className="form-control"
                  value={customPromptText}
                  onChange={(e) => setCustomPromptText(e.target.value)}
                  rows={10}
                  placeholder="Enter your custom prompt here..."
                ></textarea>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={handleCloseCustomPromptModal}>Cancel</button>
                <button type="button" className="btn btn-primary" onClick={handleSaveCustomPrompt}>Save Prompt</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main content */}
      <div className="flex-grow-1 d-flex" style={{ minHeight: 0 }}>
        {isSidebarCollapsed && (
          <button 
            className="expand-button"
            onClick={() => setIsSidebarCollapsed(false)}
          >
            →
          </button>
        )}
        <Split 
          sizes={isSidebarCollapsed ? [0, 100] : [20, 80]} 
          minSize={0} 
          gutterSize={8}
          snapOffset={100}
          className="split-flex"
        >
          {/* Sidebar */}
          <div className="bg-light border-end p-2 overflow-auto h-100">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="mb-0">Contents</h5>
              <button 
                className="btn btn-sm btn-outline-secondary" 
                onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
              >
                {isSidebarCollapsed ? '→' : '←'}
              </button>
            </div>
            <div className="list-group">
              {chapters.map((chapter) => (
                <button
                  key={chapter.id}
                  className={`list-group-item list-group-item-action ${selectedChapter?.id === chapter.id ? 'active' : ''}`}
                  onClick={() => setSelectedChapter(chapter)}
                >
                  <div className="d-flex justify-content-between align-items-center">
                    <div>Chapter {chapter.chapter_number}: {chapter.title || `Untitled Chapter ${chapter.chapter_number}`}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Main content area */}
          <div className="px-2 py-3 overflow-auto h-100">
            {selectedChapter ? (
              <>
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div className="btn-group" role="group" aria-label="View mode">
                    <button
                      type="button"
                      className={`btn ${viewMode === 'summary' ? 'btn-primary' : 'btn-outline-primary'}`}
                      onClick={() => setViewMode('summary')}
                    >
                      Summary
                    </button>
                    <button
                      type="button"
                      className={`btn ${viewMode === 'content' ? 'btn-primary' : 'btn-outline-primary'}`}
                      onClick={() => setViewMode('content')}
                    >
                      Content
                    </button>
                  </div>
                  <span className="text-muted">
                    {selectedChapter.page_count} {selectedChapter.page_count === 1 ? 'page' : 'pages'}
                    {currentSummary?.compression_ratio !== undefined && currentSummary?.compression_ratio !== null ? (
                      <span className="ms-2 badge bg-info">Compression: {(currentSummary.compression_ratio * 100).toFixed(1)}%</span>
                    ) : (
                      <span className="ms-2 badge bg-secondary">No compression data</span>
                    )}
                  </span>
                </div>

                {viewMode === 'content' ? (
                  <div className="content-preview border rounded p-3">
                    <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{selectedChapter.text}</pre>
                  </div>
                ) : (
                  <div>
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <div className="d-flex align-items-center">
                        <h5 className="mb-0 me-3">Summary</h5>
                        <div className="btn-group summary-controls">
                          <button 
                            className="btn btn-sm btn-outline-primary" 
                            onClick={() => handleCycleSummary('prev')}
                            title="Previous summary"
                            disabled={availableSummaries.length <= 1}
                          >
                            &larr;
                          </button>
                          <button className="btn btn-sm btn-outline-primary" disabled>
                            {availableSummaries.length > 0 ? 
                              `${currentSummaryIndex + 1} / ${availableSummaries.length}` : 
                              "1 / 1"}
                          </button>
                          <button 
                            className="btn btn-sm btn-outline-primary" 
                            onClick={() => handleCycleSummary('next')}
                            title="Next summary"
                            disabled={availableSummaries.length <= 1}
                          >
                            &rarr;
                          </button>
                        </div>
                        {availableSummaries.length > 1 && (
                          <small className="text-muted ms-2">(Use arrows to view different summary versions)</small>
                        )}
                      </div>
                      <div className="d-flex">
                        <select 
                          className="form-select me-2" 
                          value={selectedPrompt}
                          onChange={handlePromptChange}
                          style={{ maxWidth: '200px' }}
                          aria-label="Select prompt template"
                          title="Select a prompt style to control how the summary is generated"
                        >
                          {availablePrompts.map(prompt => (
                            <option key={prompt.id} value={prompt.id}>
                              {prompt.title}
                            </option>
                          ))}
                        </select>

                        {selectedChapter.summary ? (
                          <button 
                            className="btn btn-primary" 
                            onClick={() => handleRegenerateSummary(selectedChapter.chapter_number)}
                            disabled={summarizing[selectedChapter.chapter_number]}
                          >
                            {summarizing[selectedChapter.chapter_number] ? (
                              <>
                                <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                                Processing...
                              </>
                            ) : 'Regenerate Summary'}
                          </button>
                        ) : (
                          <button 
                            className="btn btn-primary" 
                            onClick={() => handleSummarize(selectedChapter.chapter_number)}
                            disabled={summarizing[selectedChapter.chapter_number]}
                          >
                            {summarizing[selectedChapter.chapter_number] ? (
                              <>
                                <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                                Summarizing...
                              </>
                            ) : 'Generate Summary'}
                          </button>
                        )}
                      </div>
                    </div>
                    <div className="summary-preview border rounded p-3">
                      {currentSummary ? (
                        <>
                          <div className="markdown-content">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {currentSummary.summary_text}
                            </ReactMarkdown>
                          </div>
                          {availableSummaries.length > 0 && (
                            <div className="text-muted mt-3 border-top pt-2">
                              <small>
                                {currentSummary.created_at && (
                                  <>Created: {new Date(currentSummary.created_at).toLocaleString()}</>
                                )}
                                {currentSummary.prompt_used && (
                                  <> • Generated using {
                                    availablePrompts.find(p => currentSummary.prompt_used.includes(p.id))?.title || 
                                    (currentSummary.prompt_used.includes('concise') ? 'concise' : 'detailed') + ' prompt'
                                  }</>
                                )}
                              </small>
                            </div>
                          )}
                        </>
                      ) : (
                        <p className="text-muted">No summary available. Click "Generate Summary" to create one.</p>
                      )}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="alert alert-info">
                Select a chapter from the sidebar to view its content.
              </div>
            )}
          </div>
        </Split>
      </div>
    </div>
  );
};

export default BookDetail; 