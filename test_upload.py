import requests
import os
import sys

def test_upload_book(pdf_path, title=None):
    """
    Test the book upload endpoint of the Django REST API
    
    Args:
        pdf_path (str): Path to the PDF file to upload
        title (str, optional): Title for the book. If not provided, will use filename
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return False
    
    if not pdf_path.lower().endswith('.pdf'):
        print("Error: File must be a PDF")
        return False
    
    api_url = 'http://127.0.0.1:8000/api/books/'
    
    # Create form data
    files = {'pdf_file': open(pdf_path, 'rb')}
    data = {}
    
    if title:
        data['title'] = title
    else:
        # Use filename as title if not provided
        data['title'] = os.path.basename(pdf_path).replace('.pdf', '')
    
    print(f"Uploading file: {pdf_path}")
    print(f"Book title: {data['title']}")
    
    try:
        # Make the POST request
        response = requests.post(api_url, files=files, data=data)
        
        # Close the file
        files['pdf_file'].close()
        
        # Check the response
        if response.status_code == 201 or response.status_code == 200:
            print("Upload successful!")
            print("Response:")
            print(response.json())
            return True
        else:
            print(f"Upload failed with status code: {response.status_code}")
            print("Response:")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Error during upload: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_upload.py <path_to_pdf_file> [book_title]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    
    test_upload_book(pdf_path, title)
