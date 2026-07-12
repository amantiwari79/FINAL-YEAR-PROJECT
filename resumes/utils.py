import os
from pypdf import PdfReader
import docx2txt

def extract_text_from_file(file_obj, filename):
    """
    Extracts raw text from a PDF or DOCX file object.
    """
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    
    try:
        if ext == '.pdf':
            reader = PdfReader(file_obj)
            pages_text = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pages_text.append(extracted)
            text = "\n".join(pages_text)
            
        elif ext == '.docx':
            # docx2txt process can read from a file-like object directly or file path
            text = docx2txt.process(file_obj)
            
    except Exception as e:
        print(f"Error extracting text from {filename}: {str(e)}")
        text = ""
        
    return text.strip()
