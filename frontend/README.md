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

## Authentication

This application uses Google OAuth for authentication. Here's how it works:

1. Users are presented with a landing page when not authenticated
2. After clicking "Sign in with Google", they are redirected to Google's authentication page
3. Upon successful authentication, they are redirected back to the application with a token
4. This token is used for all subsequent API requests
5. Users can only access their own books and summaries

### Development Setup

For local development, ensure the backend server is running at http://localhost:8000 and has been properly configured with Google OAuth credentials:

- Client ID: 866184954339-ajnk71sobbsomlodkaiq8vthuk42c187.apps.googleusercontent.com
- Callback URL: http://localhost:8000/accounts/google/login/callback/

### Authentication Flow Pages

- **Landing Page** (`/`): Shows application information and login button for non-authenticated users
- **Books Page** (`/books`): Shows the user's books (requires authentication)
- **Upload Page** (`/upload`): Allows users to upload new books (requires authentication)
- **Book Detail Page** (`/books/:id`): Shows book details and chapters (requires authentication)

## Technologies Used

- React 18
- TypeScript
- React Router
- Axios
- Webpack
- Bootstrap 5 (for styling) 