#!/usr/bin/env python
# test.py - Script to test the Book API endpoint

import requests
import os
import sys
import json
from pprint import pprint

# Configuration
API_BASE_URL = "http://localhost:8000/api"
AUTH_URL = "http://localhost:8000/auth/login/"
BOOKS_ENDPOINT = f"{API_BASE_URL}/books/"

# Replace with your credentials
USERNAME = "tanvir1"
PASSWORD = "tanvir"

# Replace with the path to your test PDF file
PDF_FILE_PATH = "/Users/tanvirkhan/fun/summarize_pdf/book-summarizer/book_summarizer_api/media/book_pdfs/prin.pdf" 

def get_auth_token():
    """
    Obtain authentication token using email and password.
    
    Returns:
        str: Authentication token or None if authentication fails
    """
    try:
        response = requests.post(
            AUTH_URL,
            data={
                "email": USERNAME,
                "password": PASSWORD
            }
        )
        response.raise_for_status()
        return response.json().get("key")
    except requests.exceptions.RequestException as e:
        print(f"Authentication error: {e}")
        return None

def create_book(token, title, pdf_path):
    """
    Create a new book by uploading a PDF file.
    
    Args:
        token (str): Authentication token
        title (str): Book title
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Created book data or None if creation fails
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return None
        
    try:
        # Prepare headers with authentication token
        headers = {
            "Authorization": f"Token {token}"
        }
        
        # Prepare multipart form data with file
        files = {
            'pdf_file': (
                os.path.basename(pdf_path),
                open(pdf_path, 'rb'),
                'application/pdf'
            )
        }
        
        # Prepare form data
        data = {
            'title': title
        }
        
        # Make the request
        print(f"Creating book '{title}' with PDF file: {pdf_path}")
        response = requests.post(
            BOOKS_ENDPOINT,
            headers=headers,
            files=files,
            data=data
        )
        
        # Handle response
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error creating book: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print("Error details:")
                pprint(error_data)
            except:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
        return None
    finally:
        # Make sure to close the file
        if 'files' in locals() and 'pdf_file' in files:
            files['pdf_file'][1].close()

def main():
    """Main function to run the test"""
    print("Testing Book API creation endpoint...")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to obtain authentication token. Exiting.")
        sys.exit(1)
    
    print(f"Authentication successful. Token: {token[:10]}...")
    
    # Create a new book
    book_data = create_book(
        token=token,
        title="Test Book via Python API",
        pdf_path=PDF_FILE_PATH
    )
    
    if book_data:
        print("Book created successfully!")
        print("Book details:")
        pprint(book_data)
        return 0
    else:
        print("Failed to create book.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 