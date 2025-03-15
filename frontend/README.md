# Book Summarizer Frontend

This is a React TypeScript frontend for the Book Summarizer API, which allows users to upload PDF books, view extracted chapters, and generate summaries using the Gemini API.

## Features

- Upload PDF books
- View list of uploaded books
- View book details, including chapters extracted from the PDF
- Generate and view summaries for each chapter
- Delete books

## Setup

1. **Prerequisites:**
   - Node.js 14.0+
   - npm or yarn
   - Book Summarizer API running on http://localhost:8000

2. **Installation:**
   - Clone the repository
   - Navigate to the frontend directory: `cd frontend`
   - Install dependencies: `npm install` or `yarn install`

3. **Development:**
   - Start the development server: `npm start` or `yarn start`
   - The application will be available at http://localhost:3000

4. **Production Build:**
   - Build the application: `npm run build` or `yarn build`
   - The built files will be in the `dist` directory

## API Integration

This frontend integrates with the Book Summarizer API which should be running on http://localhost:8000. The API endpoints used are:

- `/api/books/` - For listing, creating, and deleting books
- `/api/chapters/` - For listing chapters
- `/api/chapters/book/{book_pk}/chapter/{chapter_number}/summarize/` - For generating summaries

## Technologies Used

- React 18
- TypeScript
- React Router
- Axios
- Webpack
- Bootstrap 5 (for styling) 