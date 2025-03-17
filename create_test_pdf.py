from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def create_test_pdf(output_path):
    """
    Create a simple test PDF with some book-like content
    """
    # Create a PDF with ReportLab
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Add a title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, height - 100, "Test Book for PDF Upload")
    
    # Add some "chapters"
    y_position = height - 150
    
    # Chapter 1
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, y_position, "Chapter 1: Introduction")
    y_position -= 30
    
    c.setFont("Helvetica", 12)
    for i in range(5):
        c.drawString(100, y_position, f"This is paragraph {i+1} of the introduction.")
        y_position -= 20
    
    # Chapter 2
    y_position -= 20
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, y_position, "Chapter 2: Main Content")
    y_position -= 30
    
    c.setFont("Helvetica", 12)
    for i in range(5):
        c.drawString(100, y_position, f"This is paragraph {i+1} of the main content.")
        y_position -= 20
    
    # Second page
    c.showPage()
    
    # Chapter 3
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, height - 100, "Chapter 3: Conclusion")
    
    c.setFont("Helvetica", 12)
    y_position = height - 130
    for i in range(5):
        c.drawString(100, y_position, f"This is paragraph {i+1} of the conclusion.")
        y_position -= 20
    
    # Save the PDF
    c.save()
    
    print(f"Test PDF created successfully at {output_path}")

if __name__ == "__main__":
    output_path = "test_book.pdf"
    create_test_pdf(output_path)
