import os
import markdown  # type: ignore
from datetime import datetime
from docx import Document  # For DOCX conversion
import PyPDF2  # For PDF conversion


def log(message, app_route, ip): 
    # Create logs directory if it doesn't exist
    os.makedirs('./logs', exist_ok=True)
    
    # Get current date in format e.g., December-9-2024
    current_date = datetime.now().strftime("%B-%d-%Y")
    
    # Define log file path
    log_file_path = f'./logs/{current_date}.log'
    
    # Construct log message
    log_entry = f"[📝] Log: {ip} called {app_route} on {datetime.now()}    {message}\n"
    
    # Print log to console
    print(log_entry)
    
    # Append log entry to the file
    with open(log_file_path, 'a') as log_file:
        log_file.write(log_entry)


def convert_to_markdown(input_path):
    """
    Converts the given document to Markdown format.
    
    Parameters:
        input_path (str): The path to the input file to convert.
    
    Returns:
        str: The path to the converted Markdown file.
    """
    try:
        # Extract filename without extension
        filename = os.path.splitext(os.path.basename(input_path))[0]
        
        # Define output path for the Markdown file
        output_dir = os.path.dirname(input_path)  # Use the same directory as input
        output_path = os.path.join(output_dir, f"{filename}.md")

        # Skip conversion if it's already a Markdown file
        if input_path.endswith(".md"):
            return input_path
        
        # Conversion logic based on file type
        file_extension = os.path.splitext(input_path)[1].lower()

        if file_extension == ".txt":
            # Convert TXT to Markdown
            with open(input_path, "r", encoding="utf-8") as input_file:
                content = input_file.read()
            markdown_content = f"# {filename}\n\n{content}"

        elif file_extension == ".docx":
            # Convert DOCX to Markdown
            markdown_content = convert_docx_to_markdown(input_path)

        elif file_extension == ".pdf":
            # Convert PDF to Markdown
            markdown_content = convert_pdf_to_markdown(input_path)

        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

        # Write the converted content to a markdown file
        with open(output_path, "w", encoding="utf-8") as md_file:
            md_file.write(markdown_content)
        
        return output_path  # Return the full path of the converted file

    except Exception as e:
        raise RuntimeError(f"Failed to convert to Markdown: {e}")


def convert_docx_to_markdown(docx_path):
    """
    Converts a DOCX file to Markdown format.
    
    Parameters:
        docx_path (str): The path to the DOCX file to convert.
    
    Returns:
        str: The content in Markdown format.
    """
    document = Document(docx_path)
    markdown_content = ""

    # Iterate over paragraphs in the DOCX file
    for para in document.paragraphs:
        # Check for headings
        if para.style.name.startswith('Heading'):
            level = int(para.style.name.split()[-1])
            markdown_content += f"{'#' * level} {para.text}\n\n"
        else:
            markdown_content += f"{para.text}\n\n"

    return markdown_content


def convert_pdf_to_markdown(pdf_path):
    """
    Converts a PDF file to Markdown format.
    
    Parameters:
        pdf_path (str): The path to the PDF file to convert.
    
    Returns:
        str: The content in Markdown format.
    """
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            markdown_content = ""

            # Extract text from each page of the PDF
            for page in reader.pages:
                markdown_content += page.extract_text() + "\n\n"

            return markdown_content
    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF to Markdown: {e}")


def markdown_to_html(markdown_path: str, grade: str) -> str:
    """Converts markdown file to HTML."""
    markdown_file_path = f"./content/{grade}/{markdown_path}"
    
    # Check if markdown file exists
    if not os.path.exists(markdown_file_path):
        print(f"Error: {markdown_file_path} does not exist.")
        return ""

    # Read the markdown file
    with open(markdown_file_path, 'r') as markdown_file:
        markdown_content = markdown_file.read()

    try:
        # Convert markdown to HTML using the markdown library
        html_content = markdown.markdown(markdown_content)
        return html_content
    except Exception as e:
        print(f"Error converting markdown to HTML: {e}")
        return ""


def inject_style(html_content: str, stylesheet: str) -> str:
    """Injects the styles into the HTML content by reading the CSS file."""
    if not os.path.exists(stylesheet):
        print(f"Error: Stylesheet {stylesheet} not found.")
        return html_content

    # Read the CSS file
    with open(stylesheet, 'r') as file:
        style = file.read()

    # Create a <style> tag with the CSS content
    style_tag = f"<style>{style}</style>"

    # Inject style tag into <head> section
    head_index = html_content.find("<head>")
    if head_index != -1:
        head_index += len("<head>")
        html_content = html_content[:head_index] + style_tag + html_content[head_index:]
    else:
        print("Warning: <head> tag not found in the HTML content. Style not injected.")

    return html_content


def tiling_window_html_maker(markdown_path_array, grade: str) -> str:
    """Creates HTML with markdown content rendered inside 'window' divs."""
    index_path = './web/template/index.html'

    # Check if index.html exists
    if not os.path.exists(index_path):
        return {"error": "index.html not found in the /web directory."}

    # Read the existing HTML content from index.html
    with open(index_path, 'r') as file:
        html_content = file.read()

    html_content = inject_style(html_content=html_content, stylesheet="./web/style.css")

    # Begin modifying the body of the HTML content
    body_start = html_content.find('<body>')
    body_end = html_content.find('</body>', body_start)

    if body_start == -1 or body_end == -1:
        return {"error": "HTML structure in index.html is not correct."}

    body_content = html_content[body_start + len('<body>'):body_end]

    # Wrap the entire content inside a window-container div
    new_content = '<div class="window-container">'

    # Loop through each markdown file in the array and add it
    for markdown_path in markdown_path_array:
        # Convert each markdown file to HTML
        html_document = markdown_to_html(markdown_path, grade)

        if html_document:
            # Wrap the HTML content inside a div with class 'window' and 'gap'
            iframe_code = f"""
                <div><div class="window"><div class="gap">{html_document}</div></div></div>
            """
            # Add iframe to the new content
            new_content += iframe_code

    # Close the window-container div
    new_content += '</div>'

    # Replace the old body content with the new content
    updated_html = html_content[:body_start + len('<body>')] + new_content + html_content[body_end:]

    return updated_html


def get_docs_from_grade(grade: str):
    """Returns an array of files in the specified grade's path."""
    path = f"./content/{grade}/"

    if not os.path.exists(path):
        return {"error": "Grade folder not found."}

    try:
        files = os.listdir(path)
        files = [file for file in files if os.path.isfile(os.path.join(path, file))]
        return files
    except Exception as e:
        return {"error": str(e)}


def assemble(grade: str):
    """Assembles the final HTML page for the specified grade."""
    documents = get_docs_from_grade(grade)

    if isinstance(documents, list):
        return tiling_window_html_maker(documents, grade=grade)
    else:
        return documents


def html(path: str, stylesheet: str):
    """Return HTML with injected styles."""
    if not os.path.exists(path):
        return {"error": f"File {path} does not exist."}

    with open(path, 'r') as file:
        html_content = file.read()

    return inject_style(html_content=html_content, stylesheet=stylesheet)


def directory_tree_json_format(in_folder: str) -> dict:
    """Returns the directory tree in a folder as JSON."""

    def build_tree(path):
        """Recursively builds a dictionary representation of the directory tree."""
        tree = {"name": os.path.basename(path), "type": "directory", "children": []}

        try:
            for entry in os.listdir(path):
                entry_path = os.path.join(path, entry)
                if os.path.isdir(entry_path):
                    tree["children"].append(build_tree(entry_path))
                else:
                    tree["children"].append({"name": entry, "type": "file"})
        except PermissionError:
            tree["children"].append({"name": "Permission denied", "type": "error"})

        return tree

    if not os.path.exists(in_folder):
        return {"error": f"Folder {in_folder} does not exist."}

    if not os.path.isdir(in_folder):
        return {"error": f"Path {in_folder} is not a directory."}

    return build_tree(in_folder)