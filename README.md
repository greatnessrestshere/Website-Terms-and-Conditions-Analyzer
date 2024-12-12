# Website-Terms-and-Conditions-Analyzer
A Flask-based web app that analyzes website Terms and Conditions to extract key terms, rights, and risks in simple language, with NLP support and PDF export.

# Overview of the Website Analyzer
The Website Analyzer is a Flask-based web application designed to extract and analyze terms and conditions or similar text from a website. Users input a URL, and the app retrieves the webpage content (even from dynamically rendered sites using Selenium), processes the text to extract meaningful insights, and generates a downloadable PDF report.

# High-Level Workflow

User Input: The user provides the URL of the webpage containing the terms and conditions or other content to analyze.

Content Retrieval: Selenium dynamically loads the webpage and retrieves the rendered HTML to handle both static and JavaScript-heavy sites.

Text Extraction: BeautifulSoup parses the HTML to extract readable text.

Natural Language Processing (NLP): SpaCy is used to process the extracted text and identify specific terms (e.g., rights, agreements, or legal terms).

PDF Generation: The analyzed terms and sections are structured and saved as a downloadable PDF using the FPDF library.
