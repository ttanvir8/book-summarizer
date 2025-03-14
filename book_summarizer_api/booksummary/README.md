# Book Summarizer API

This is a REST API built with Django REST Framework for managing books and their chapters, with the capability to automatically extract chapter information from PDF files and generate summaries using the Gemini API.

## Setup

1.  **Prerequisites:**
    *   Python 3.8+
    *   Pip
    *   Virtual environment (recommended)
    *   Google Generative AI API key

2.  **Installation:**
    *   Clone the repository: `git clone <repository_url>`
    *   Create a virtual environment: `python3 -m venv venv`
    *   Activate the virtual environment:
        *   Linux/macOS: `source venv/bin/activate`
        *   Windows: `venv\Scripts\activate`
    *   Navigate into the project folder: `cd summarize_pdf`
    *   Install dependencies: `pip install -r requirements.txt`
    * Update your google gemini API KEY in file: `book_summarizer_api/booksummary/views.py`
    *   Run migrations: `python manage.py migrate`

3. **Run the server**
    * `python manage.py runserver`

## API Endpoints

### Books

*   **Base URL:** `/api/books/`

*   **`GET /api/books/`**
    *   **Description:** Lists all books.
    *   **Response:**
        *   `200 OK`: Array of book objects.

*   **`GET /api/books/{book_id}/`**
    *   **Description:** Retrieves a specific book.
    *   **Path Parameters:**
        *   `book_id`: The ID of the book.
    *   **Response:**
        *   `200 OK`: Book object.
        *   `404 Not Found`: If the book is not found.

*   **`POST /api/books/`**
    *   **Description:** Creates a new book and extracts chapter data from a PDF file.
    *   **Request Body:** `multipart/form-data`
        *   `title` (optional): The title of the book. If not provided, defaults to the filename.
        *   `pdf_file` (required): The PDF file.
    *   **Response:**
        *   `201 Created`: Book object with chapter information.
        *   `400 Bad Request`: If no `pdf_file` is provided or if there are issues with the request data.

*   **`PUT /api/books/{book_id}/`**
    *   **Description:** Updates a specific book.
*   **`PATCH /api/books/{book_id}/`**
    *   **Description:** Partially updates a specific book.

*   **`DELETE /api/books/{book_id}/`**
    *   **Description:** Deletes a specific book.

### Chapters

*   **Base URL:** `/api/chapters/`

*   **`GET /api/chapters/`**
    *   **Description:** Lists all chapters.
    *   **Response:**
        *   `200 OK`: Array of chapter objects.

*   **`GET /api/chapters/{chapter_id}/`**
    *   **Description:** Retrieves a specific chapter.
    *   **Path Parameters:**
        *   `chapter_id`: The ID of the chapter.
    *   **Response:**
        *   `200 OK`: Chapter object.
        *   `404 Not Found`: If the chapter is not found.
*   **`PUT /api/chapters/{chapter_id}/`**
    *   **Description:** Updates a specific chapter.
*   **`PATCH /api/chapters/{chapter_id}/`**
    *   **Description:** Partially updates a specific chapter.
*   **`DELETE /api/chapters/{chapter_id}/`**
    *   **Description:** Deletes a specific chapter.

*   **`POST /api/chapters/book/{book_pk}/chapter/{chapter_number}/summarize/`**
    *   **Description:** Generates a summary for a specific chapter within a book.
    *   **Path Parameters:**
        *   `book_pk`: The ID of the book.
        *   `chapter_number`: The chapter number within the book.
    *   **Request Body:** None
    *   **Response:**
        *   `200 OK`: The chapter object with the generated summary.
        *   `404 Not Found`: If the specified chapter is not found.
        *   `500 Internal Server Error`: If there's an error during summary generation.

## Example Usage (using curl)

### Create a Book (with PDF upload)

```bash
curl -X POST \
     -F "title=My New Book" \
     -F "pdf_file=@/path/to/your/book.pdf" \
     http://localhost:8000/api/books/
