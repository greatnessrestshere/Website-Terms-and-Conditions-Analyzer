import os
from flask import Flask, render_template, request, send_file, session
from flask_session import Session
import spacy
from bs4 import BeautifulSoup
from fpdf import FPDF

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

# Configure Flask-Session for server-side sessions
app.config['SESSION_TYPE'] = 'filesystem'  # Use the file system to store session data
app.config['SESSION_PERMANENT'] = False    # Make sessions non-permanent
app.secret_key = "your_secret_key"         # Secret key for session signing
Session(app)

# Selenium function for fetching dynamic content
def fetch_content_with_selenium(url):
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        # Wait for the main content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        text = driver.page_source  # Fully rendered HTML
    except Exception as e:
        print(f"Error loading page: {e}")
        text = ""
    finally:
        driver.quit()

    return text

# Function to extract terms and rights
def extract_terms(doc):
    terms = {"Terms of Use": [], "Rights": []}
    for sentence in doc.sents:
        sentence_text = sentence.text.lower()
        if "right" in sentence_text:
            terms["Rights"].append(sentence.text)
        elif "term" in sentence_text or "agreement" in sentence_text:
            terms["Terms of Use"].append(sentence.text)
    print(f"Extracted Terms: {terms}")  # Debug
    return terms

# Function to structure extracted terms into sections
def create_sections(terms):
    sections = []
    for category, items in terms.items():
        # Use the first item as the subtitle (if available) and the rest as content
        subtitle = items[0] if items else "No subtitle available"
        content = items[1:] if len(items) > 1 else ["No additional content available"]
        sections.append({"title": category, "subtitle": subtitle, "content": content})
    print(f"Sections Created: {sections}")  # Debug
    return sections

# Function to preprocess text for Unicode compatibility
def preprocess_text(text):
    """
    Replace unsupported characters with Unicode-compatible equivalents.
    """
    replacements = {
        '\u2019': "'",  # Replace smart quote
        '\u201C': '"',  # Replace opening smart double quote
        '\u201D': '"',  # Replace closing smart double quote
        '\u2014': '--', # Replace em dash
        '\u2026': '...', # Replace ellipsis
        '\n': ' ',       # Replace newlines with spaces
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text

# Updated Function to generate a PDF
def create_pdf(sections):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Use a font that supports Unicode
    pdf.add_font("Arial", "", "/Library/Fonts/Arial Unicode.ttf", uni=True)  # Adjust path for your system
    pdf.set_font("Arial", size=12)

    # Add the title at the top
    pdf.set_y(10)  # Reduce top margin
    pdf.cell(200, 10, txt="Website Analysis", ln=True, align='C')

    # Add the content directly under the title
    for section in sections:
        # Add section title
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(0, 10, txt=preprocess_text(section.get('title', 'Unknown Section')), ln=True)

        # Add subtitle directly under the title
        pdf.set_font("Arial", style="I", size=12)
        pdf.cell(0, 10, txt=preprocess_text(section.get('subtitle', 'No subtitle available')), ln=True)

        # Add section content
        pdf.set_font("Arial", size=12)
        content = section.get('content', [])
        if content:
            for sentence in content:
                pdf.multi_cell(0, 10, preprocess_text(sentence))
        else:
            pdf.multi_cell(0, 10, "No content available for this section.")

        pdf.ln(10)  # Add spacing between sections

    # Save the PDF file
    pdf.output("terms_analysis.pdf")

# Flask route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Flask route for analyzing terms
@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['url']
    print(f"URL received: {url}")

    # Fetch content with Selenium
    page_content = fetch_content_with_selenium(url)
    soup = BeautifulSoup(page_content, 'html.parser')
    text = soup.get_text()
    print(f"Extracted Text: {text[:500]}")  # Debug

    # Process text with SpaCy
    doc = nlp(text)
    terms = extract_terms(doc)
    print(f"Extracted Terms: {terms}")  # Debug

    sections = create_sections(terms)
    print(f"Sections Created: {sections}")  # Debug

    # Store sections in server-side session
    session['sections'] = sections
    print(f"Stored in session: {session['sections']}")  # Debug

    return render_template('analysis.html', sections=sections)

# Flask route for generating PDF
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    sections = session.get('sections', [])  # Retrieve sections from session
    print(f"Sections passed to PDF: {sections}")  # Debug
    create_pdf(sections)
    return send_file("terms_analysis.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)


