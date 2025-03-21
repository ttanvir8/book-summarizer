import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://book-summarizer-ur5b.onrender.com/api';
const AUTH_URL = process.env.REACT_APP_AUTH_URL || 'https://book-summarizer-ur5b.onrender.com';

// Set up axios defaults for authentication
const token = localStorage.getItem('token');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Token ${token}`;
}

// Initialize axios interceptors
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // If the token is invalid or expired, log out the user
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export interface Book {
  id: number;
  title: string;
  pdf_file: string;
  processed_date: string;
  total_pages: number | null;
  total_chapters: number | null;
  chapters?: Chapter[];
}

export interface ChapterSummary {
  id: number;
  summary_text: string;
  prompt_used: string;
  compression_ratio: number | null;
  created_at: string;
}

export interface Prompt {
  id: string;
  title: string;
  text: string;
}

export const availablePrompts: Prompt[] = [
  {
    id: 'default',
    title: 'Default (Detailed)',
    text: `Create a detailed but concise summary of the following chapter that adheres to these principles:

Relevant: Give me all the main arguments, analogies, processes, tools, examples, and supporting evidence from the source. Prioritize ideas central to the author's thesis..
Concise: Avoid repetition, redundancy, and filler. Present ideas in a densely informative way (e.g., explain an analogy once with clarity, not multiple times). But, Give each argument's main paragraph enough details to get the point across.
Coherent: Structure the summary logically (e.g., mirror the chapter's flow or group related arguments). Use transitions to show connections between ideas. Make it readable and have a logical flow of sentences.
Faithful: Do not add, interpret, or omit content. Preserve the author's tone, emphasis, and proportional focus (e.g., if the author spends 30% of the chapter on a process, reflect that weighting).
Avoid:
Paraphrasing that loses nuance (e.g., oversimplifying a multi-step process).
Listing disconnected facts without contextualizing their role in the argument.
Structure:
Make logical sections for each reasonable section of the summary and use bold and italic formatting of text to emphasis important parts for better understandability and readability.
`
  },
  {
    id: 'concise',
    title: 'Concise',
    text: `Create a summary of the following chapter with these guidelines:

Main Ideas: Include only the main arguments. Add one key supporting point for each argument if it’s critical to the thesis.
Short and Simple: Keep it concise. Skip extra details, examples, or evidence unless absolutely necessary.
Clear: Arrange the arguments in a logical order with basic transitions.
True to the Text: Stick to the author’s main points and tone. Don’t interpret or add ideas.
Avoid: Extra examples, minor points, or repetition.

Make logical sections for each reasonable section of the summary and use bold and italic formatting of text to emphasis important parts for better understandability and readability.`
  },
  {
    id: 'custom',
    title: 'Custom Prompt',
    text: '' // Empty by default, will be filled by the user
  }
];

export interface Chapter {
  id: number;
  book: number;
  chapter_number: string;
  title: string;
  text: string;
  summary: string | null;
  start_page: number;
  end_page: number;
  page_count: number;
  word_count: number;
  compression_ratio: number | null;
  summaries: ChapterSummary[];
  active_summary: ChapterSummary | null;
  level?: number;
  parent?: number | null;
}

// Authentication API calls
export const loginWithGoogle = () => {
  window.location.href = `${AUTH_URL}/accounts/google/login/`;
};

export const getAuthToken = async () => {
  try {
    const response = await axios.post(`${AUTH_URL}/auth/token/`, {}, {
      withCredentials: true
    });
    return response.data;
  } catch (error) {
    console.error('Error getting auth token:', error);
    throw error;
  }
};

// Book API calls
export const getAllBooks = async (): Promise<Book[]> => {
  const response = await axios.get(`${API_URL}/books/`);
  return response.data;
};

export const getBook = async (id: number): Promise<Book> => {
  try {
    console.log(`Fetching book with ID: ${id}`);
    const response = await axios.get(`${API_URL}/books/${id}/`);
    console.log('Book API response data:', JSON.stringify(response.data));
    return response.data;
  } catch (error) {
    console.error('Error fetching book:', error);
    throw error;
  }
};

export const uploadBook = async (formData: FormData): Promise<Book> => {
  try {
    const response = await axios.post(`${API_URL}/books/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log('Upload response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error in uploadBook:', error);
    throw error;
  }
};

export const deleteBook = async (id: number): Promise<void> => {
  await axios.delete(`${API_URL}/books/${id}/`);
};

// Chapter API calls
export const getChapters = async (bookId?: number): Promise<Chapter[]> => {
  try {
    console.log(`Fetching chapters${bookId ? ` for book ${bookId}` : ''}`);
    const response = await axios.get(`${API_URL}/chapters/${bookId ? `?book=${bookId}` : ''}`);
    console.log(`Received ${response.data.length} chapters`);
    if (response.data.length > 0) {
      console.log('First chapter sample:', JSON.stringify(response.data[0]));
    } else {
      console.log('No chapters returned from API');
    }
    return response.data;
  } catch (error) {
    console.error('Error fetching chapters:', error);
    throw error;
  }
};

export const getChapter = async (id: number): Promise<Chapter> => {
  const response = await axios.get(`${API_URL}/chapters/${id}/`);
  console.log('API response for getChapter:', response.data);
  return response.data;
};

export const summarizeChapter = async (bookId: number, chapterNumber: string | number, promptId?: string): Promise<ChapterSummary> => {
  let requestData = {};
  
  if (promptId) {
    const selectedPrompt = availablePrompts.find(p => p.id === promptId);
    if (selectedPrompt && selectedPrompt.text) {
      requestData = { custom_prompt: selectedPrompt.text };
    }
  }
  
  // Add timestamp to prevent caching
  const timestamp = new Date().getTime();
  const response = await axios.post(
    `${API_URL}/chapters/book/${bookId}/chapter/${chapterNumber}/summarize/?_=${timestamp}`, 
    requestData
  );
  console.log('API response for summarizeChapter:', response.data);
  
  return response.data;
};

// New API functions for working with multiple summaries
export const regenerateSummary = async (bookId: number, chapterNumber: string | number, promptId?: string): Promise<Chapter> => {
  let requestData = {};
  
  if (promptId) {
    const selectedPrompt = availablePrompts.find(p => p.id === promptId);
    if (selectedPrompt && selectedPrompt.text) {
      requestData = { custom_prompt: selectedPrompt.text };
    }
  }
  
  // Add timestamp to prevent caching
  const timestamp = new Date().getTime();
  const response = await axios.post(
    `${API_URL}/chapters/book/${bookId}/chapter/${chapterNumber}/regenerate-summary/?_=${timestamp}`, 
    requestData
  );
  console.log('API response for regenerateSummary:', response.data);
  
  // Response contains a ChapterSummary, we need to fetch the updated chapter
  const chapterId = response.data.chapter;
  return await getChapter(chapterId);
};

export const getChapterSummaries = async (chapterId: number): Promise<ChapterSummary[]> => {
  // Add timestamp to prevent caching
  const timestamp = new Date().getTime();
  const response = await axios.get(`${API_URL}/summaries/chapter/${chapterId}/?_=${timestamp}`);
  console.log('API response for getChapterSummaries:', response.data);
  return response.data;
};

export const setActiveSummary = async (chapterId: number, summaryId: number): Promise<Chapter> => {
  const response = await axios.post(`${API_URL}/chapters/${chapterId}/set-active-summary/${summaryId}/`);
  console.log('API response for setActiveSummary:', response.data);
  return response.data;
}; 