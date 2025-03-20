# Book Summarizer API: Google OAuth Authentication

This document explains how to use the Google OAuth authentication in the Book Summarizer API.

## Authentication Flow

The Book Summarizer API implements a secure authentication flow using Google OAuth 2.0. Here's how it works:

1. Users authenticate through Google's OAuth system
2. Upon successful authentication, users receive an API token
3. This token is used for all subsequent API requests
4. Books created by users are associated with their accounts
5. Users can only access their own books and summaries

## Using Authentication in API Requests

### 1. Login with Google

To authenticate, users should be directed to:

```
/accounts/google/login/
```

The callback URL will be:

```
/accounts/google/login/callback/
```

### 2. Retrieving the Token

After successful authentication, users can get their token by:

```
POST /auth/token/
```

### 3. Using the Token

For all API requests, include the token in the Authorization header:

```
Authorization: Token <your_token_here>
```

Example:
```bash
curl -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  https://your-api.com/api/books/
```

## API Endpoints

All API endpoints require authentication:

- `GET /api/books/` - List all books owned by the current user
- `POST /api/books/` - Upload a new book (authenticated user becomes the owner)
- `GET /api/books/{id}/` - Get details of a specific book (if owned by the current user)
- `GET /api/chapters/` - List all chapters from books owned by the current user
- `POST /api/chapters/book/{book_id}/chapter/{chapter_number}/summarize/` - Generate a summary for a chapter

## Security Notes

- All books are associated with the user who created them
- Users can only view and modify their own books and chapters
- API access is secured with token authentication
- HTTPS should be used for all communications with the API

## Existing Data

All existing books have been migrated to the superuser account:
- Username: tanvir1
- Password: tanvir 