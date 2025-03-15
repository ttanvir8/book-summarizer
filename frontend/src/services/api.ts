import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api';

export interface Book {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
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
    text: `Create a detailed summary of the following chapter that adheres to these principles:

Relevant: Give me all the main arguments, analogies, processes, tools, examples, and supporting evidence from the source. Prioritize ideas central to the author's thesis. And make it detailed engough so that each arguments are discussed in enough comprehensive details.

Concise: Avoid repetition, redundancy, and filler. Present ideas in a densely informative way (e.g., explain an analogy once with clarity, not multiple times). But, Give each argument's main paragraph enough details to get the point across.

Coherent: Structure the summary logically (e.g., mirror the chapter's flow or group related arguments). Use transitions to show connections between ideas. Make it readable and have logical flow of sentence.

Faithful: Do not add, interpret, or omit content. Preserve the author's tone, emphasis, and proportional focus (e.g., if the author spends 30% of the chapter on a process, reflect that weighting).

Avoid:
Paraphrasing that loses nuance (e.g., oversimplifying a multi-step process).
Listing disconnected facts without contextualizing their role in the argument.

Structure:
Make logical sections for each reasonable sections of the summary and use bold and italic formatting of text to emphasis important parts for better understandability and readability.`
  },
  {
    id: 'concise',
    title: 'Concise',
    text: `Create a concise summary of the following chapter that covers only the most essential points:

Focus on:
- The core argument or thesis
- Key supporting evidence
- Main conclusions

Use simple language and short paragraphs.
Limit to about 1/5 the length of the original text.`
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
  chapter_number: number;
  title: string;
  text: string;
  content: string;
  summary: string;
  page_count: number;
  compression_ratio: number | null;
  created_at: string;
  updated_at: string;
  summaries: ChapterSummary[];
  active_summary: ChapterSummary | null;
}

// Book API calls
export const getAllBooks = async (): Promise<Book[]> => {
  const response = await axios.get(`${API_URL}/books/`);
  return response.data;
};

export const getBook = async (id: number): Promise<Book> => {
  const response = await axios.get(`${API_URL}/books/${id}/`);
  return response.data;
};

export const uploadBook = async (formData: FormData): Promise<Book> => {
  const response = await axios.post(`${API_URL}/books/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const deleteBook = async (id: number): Promise<void> => {
  await axios.delete(`${API_URL}/books/${id}/`);
};

// Chapter API calls
export const getChapters = async (): Promise<Chapter[]> => {
  const response = await axios.get(`${API_URL}/chapters/`);
  console.log('API response for getChapters:', response.data);
  return response.data;
};

export const getChapter = async (id: number): Promise<Chapter> => {
  const response = await axios.get(`${API_URL}/chapters/${id}/`);
  console.log('API response for getChapter:', response.data);
  return response.data;
};

export const summarizeChapter = async (bookId: number, chapterNumber: number, promptId?: string): Promise<Chapter> => {
  let requestData = {};
  
  if (promptId) {
    const selectedPrompt = availablePrompts.find(p => p.id === promptId);
    if (selectedPrompt) {
      requestData = { prompt_template: selectedPrompt.text };
    }
  }
  
  const response = await axios.post(`${API_URL}/chapters/book/${bookId}/chapter/${chapterNumber}/summarize/`, requestData);
  console.log('API response for summarizeChapter:', response.data);
  return response.data;
};

// New API functions for working with multiple summaries
export const regenerateSummary = async (bookId: number, chapterNumber: number, promptId?: string): Promise<Chapter> => {
  let requestData = {};
  
  if (promptId) {
    const selectedPrompt = availablePrompts.find(p => p.id === promptId);
    if (selectedPrompt) {
      requestData = { prompt_template: selectedPrompt.text };
    }
  }
  
  const response = await axios.post(
    `${API_URL}/chapters/book/${bookId}/chapter/${chapterNumber}/regenerate-summary/`, 
    requestData
  );
  console.log('API response for regenerateSummary:', response.data);
  return response.data;
};

export const getChapterSummaries = async (chapterId: number): Promise<ChapterSummary[]> => {
  const response = await axios.get(`${API_URL}/summaries/chapter/${chapterId}/`);
  console.log('API response for getChapterSummaries:', response.data);
  return response.data;
};

export const setActiveSummary = async (chapterId: number, summaryId: number): Promise<Chapter> => {
  const response = await axios.post(`${API_URL}/chapters/${chapterId}/set-active-summary/${summaryId}/`);
  console.log('API response for setActiveSummary:', response.data);
  return response.data;
}; 