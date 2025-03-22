from datetime import datetime
import json
import re
import pypdf
from typing import Dict, List, Optional, Union, Any

def process_pdf_chapters(reader) -> dict:
    """
    Process PDF chapters and return structured data with nested chapters
    
    Args:
        reader: PDF reader object
        
    Returns:
        dict: Document metadata and chapters in nested format
    """
    try:
        bookmarks = reader.outline
        pages = reader.pages
        
        # Debug the bookmark structure
        print("Analyzing bookmark structure...")
        analyze_bookmark_structure(bookmarks)
        
        document_metadata = {
            "document_info": {
                "total_pages": len(pages),
                "processed_date": datetime.now().isoformat(),
            },
            "chapters": []
        }
        
        # Process bookmarks as a tree structure
        document_metadata["chapters"] = process_bookmark_tree(reader, bookmarks, pages)
        
        return document_metadata
        
    except Exception as e:
        print(f"Critical error processing document: {str(e)}")
        return None

def analyze_bookmark_structure(bookmarks, level=0, path=""):
    """
    Analyze and print the bookmark structure for debugging
    
    Args:
        bookmarks: List of bookmarks or a single bookmark
        level: Current nesting level
        path: Path to current bookmark
    """
    indent = "  " * level
    
    if not isinstance(bookmarks, list):
        title = getattr(bookmarks, "title", "(no title)")
        print(f"{indent}- {title}")
        return
        
    for i, bookmark in enumerate(bookmarks):
        if isinstance(bookmark, list):
            print(f"{indent}+ [Nested bookmark list at level {level}]")
            analyze_bookmark_structure(bookmark, level + 1, f"{path}.{i}")
        else:
            title = getattr(bookmark, "title", "(no title)")
            print(f"{indent}- {title}")

def process_bookmark_tree(reader, bookmarks, pages, level=0):
    """
    Process bookmarks as a tree structure
    
    Args:
        reader: PDF reader object
        bookmarks: List of bookmarks or a single bookmark
        pages: List of pages in the PDF
        level: Current nesting level
        
    Returns:
        list: List of chapters with nested structure
    """
    result = []
    
    if not isinstance(bookmarks, list):
        # Handle single bookmark case
        return [create_chapter_data(reader, bookmarks, pages, level)]
    
    i = 0
    while i < len(bookmarks):
        bookmark = bookmarks[i]
        
        if not isinstance(bookmark, list):
            # Find the next bookmark at the same level to determine the page range
            next_bookmark = find_next_bookmark(bookmarks, i)
            
            # Check if the next item is a nested list (which would be children)
            has_children = i + 1 < len(bookmarks) and isinstance(bookmarks[i + 1], list)
            
            # Create chapter data
            chapter = create_chapter_data(reader, bookmark, pages, level, next_bookmark, has_children)
            
            if has_children:
                # Process children and get the first child's start page for parent's end page adjustment
                children = process_bookmark_tree(reader, bookmarks[i + 1], pages, level + 1)
                
                # Adjust parent chapter's end page to be one page before the first child's start page
                if children and 'start_page' in children[0]:
                    # Adjust the end page of the parent to be one page before the first child starts
                    first_child_start = children[0]['start_page']
                    chapter['end_page'] = first_child_start - 1
                    chapter['page_count'] = max(0, chapter['end_page'] - chapter['start_page'] + 1)
                    
                    # Re-extract the text with the adjusted page range
                    if chapter['start_page'] <= chapter['end_page']:
                        # Convert to 0-based indexing for extraction
                        start_page_idx = chapter['start_page'] - 1
                        end_page_idx = chapter['end_page']
                        chapter['text'] = extract_text_from_page_range(reader, pages, start_page_idx, end_page_idx)
                        chapter['word_count'] = len(chapter['text'].split())
                
                # Add the children to the chapter
                chapter["children"] = children
                i += 2  # Skip the child list
            else:
                i += 1
                
            result.append(chapter)
        else:
            # Skip standalone nested lists (should be handled by parent)
            i += 1
    
    return result

def find_next_bookmark(bookmarks, current_index):
    """
    Find the next bookmark at the same level
    
    Args:
        bookmarks: List of bookmarks
        current_index: Current index in the list
        
    Returns:
        bookmark: Next bookmark or None
    """
    i = current_index + 1
    
    # Skip child bookmark list if present
    if i < len(bookmarks) and isinstance(bookmarks[i], list):
        i += 1
        
    if i < len(bookmarks) and not isinstance(bookmarks[i], list):
        return bookmarks[i]
        
    return None

def create_chapter_data(reader, bookmark, pages, level, next_bookmark=None, has_children=False):
    """
    Create chapter data from a bookmark
    
    Args:
        reader: PDF reader object
        bookmark: Bookmark object
        pages: List of pages
        level: Nesting level
        next_bookmark: Next bookmark at the same level (optional)
        has_children: Whether this bookmark has children
        
    Returns:
        dict: Chapter data
    """
    try:
        # Get start page
        start_page = reader.get_destination_page_number(bookmark)
        
        # Get end page from next bookmark if available
        end_page = None
        if next_bookmark:
            try:
                end_page = reader.get_destination_page_number(next_bookmark)
            except:
                pass
                
        # If no end page, use the last page
        if end_page is None:
            end_page = len(pages)
            
        chapter = {
            "title": bookmark.title,
            "start_page": start_page + 1,  # Convert to 1-based page numbers
            "end_page": end_page,
            "page_count": max(0, end_page - start_page),
            "level": level,
        }
        
        # If this is a parent bookmark with children, we'll adjust its end page later
        # when we process the children. For now, just set a flag to indicate this.
        if not has_children:
            # Extract text if we have valid page numbers
            if start_page >= 0 and start_page < len(pages):
                chapter["text"] = extract_text_from_page_range(reader, pages, start_page, min(end_page, len(pages)))
                chapter["word_count"] = len(chapter["text"].split())
            
        return chapter
        
    except Exception as e:
        print(f"Error creating chapter data: {e}")
        # Return a minimal chapter with just the title
        return {
            "title": getattr(bookmark, "title", "Unknown"),
            "error": str(e),
            "level": level
        }

def extract_text_from_page_range(reader, pages, start_page, end_page):
    """
    Extract text from a range of pages
    
    Args:
        reader: PDF reader object
        pages: List of pages
        start_page: Start page index (0-based)
        end_page: End page index (0-based)
        
    Returns:
        str: Extracted text
    """
    text = ""
    
    # Ensure valid page range
    start = max(0, start_page)
    end = min(len(pages), end_page)
    
    # Extract text from each page
    for i in range(start, end):
        # Add page number with clear formatting
        text += f"\n( Page {i + 1} )\n\n"
        try:
            # Extract text from the current page
            page_text = pages[i].extract_text()
            if page_text:
                text += normalize_text(page_text)
            # Add spacing after page
            text += "\n\n"
        except Exception as e:
            print(f"Error extracting text from page {i+1}: {str(e)}")
    
    return text

def normalize_text(raw_text):
    """
    Normalize text by cleaning and formatting
    
    Args:
        raw_text: Raw text from PDF
        
    Returns:
        str: Normalized text
    """
    if not raw_text:
        return ""
        
    # Replace tabs and multiple newlines with a single space
    text = re.sub(r'[\t\n]+', ' ', raw_text)
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    # Add line breaks after periods, exclamation marks, and question marks
    text = re.sub(r'(?<=[.!?]) +', '\n', text)
    
    # Capitalize the first letter of each sentence
    sentences = text.split('\n')
    sentences = [sentence.strip().capitalize() for sentence in sentences]
    
    # Join sentences back into a single string
    normalized_text = '\n'.join(sentences)
    
    # Handle common abbreviations and contractions
    normalized_text = re.sub(r"\bi'm\b", "I'm", normalized_text)
    normalized_text = re.sub(r"\bcan't\b", "cannot", normalized_text)
    normalized_text = re.sub(r"\bwon't\b", "will not", normalized_text)
    normalized_text = re.sub(r"\b(\w+)'ll\b", r"\1 will", normalized_text)
    normalized_text = re.sub(r"\b(\w+)'ve\b", r"\1 have", normalized_text)
    normalized_text = re.sub(r"\b(\w+)'re\b", r"\1 are", normalized_text)
    normalized_text = re.sub(r"\b(\w+)'d\b", r"\1 would", normalized_text)
    normalized_text = re.sub(r"\b(\w+)'s\b", r"\1 is", normalized_text)
    
    return normalized_text

if __name__ == "__main__":
    book_path = "books/prin.pdf"
    reader = pypdf.PdfReader(book_path)
    pages = reader.pages
    document_metadata = process_pdf_chapters(reader)

    with open("output.json", "w", encoding='utf-8') as f:
        json.dump(document_metadata, f, indent=4, ensure_ascii=False)