
import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            #print(f"extracted text = {text}")
    return text

# Extract text from both PDFs

'''

sample usage

text_subject1 = extract_text_from_pdf("Adolf_Hitler.pdf")
text_subject2 = extract_text_from_pdf("Kunchan_Nambiar.pdf")

'''



