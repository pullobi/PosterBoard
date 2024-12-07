import shutil, os, markdown, pypandoc
from flask import jsonify

def convertToMarkdown(document: str):
    docPath = f"./temp/{document}"
    targetDocPath = f"./temp/{document}.md"
    if document.endswith('.md'):
        print(f"Document {document} is already in Markdown format. Skipping conversion.")
        return
    if not os.path.exists(docPath):
        print(f"Error: The document {document} does not exist at {docPath}.")
        return
    try:
        pypandoc.convert_file(docPath, 'md', outputfile=targetDocPath)
        print(f"Document converted to markdown and saved to {targetDocPath}")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

## Adding documents
def AddDocumentToPosterBoard(forGrade: str, DocumentName: str):
    docPath = f"./temp/{DocumentName}"
    targetGradeBoard = f"./content/{forGrade}/"
    
    # Ensure target directory exists
    if not os.path.exists(targetGradeBoard):
        os.makedirs(targetGradeBoard)

    # Convert document to markdown
    convertToMarkdown(DocumentName)
    
    # Move converted file to the grade board
    targetDocPath = f"./temp/{DocumentName}.md"
    shutil.move(targetDocPath, f"{targetGradeBoard}{DocumentName}.md")
    
    # Remove original document
    os.remove(docPath)
    
    print(f"Document {DocumentName} moved to {targetGradeBoard} and original removed.")

## For Rendering the converted markdown
def MarkdownToHTML(markdownPath: str, grade: str) -> str:
    """Converts markdown to HTML, then returns it."""

    # Read the markdown file
    with open(f"./content/{grade}/{markdownPath}", 'r') as markdown_file:
        markdown_content = markdown_file.read()
    
    # Convert markdown to HTML using the markdown library
    html_content = markdown.markdown(markdown_content)
    
    return html_content

def injectStyle(html_content: str, stylesheet) -> str:
    """Injects the styles into the HTML content by reading the CSS file."""
    
    # Read the CSS file
    with open(stylesheet, 'r') as file:
        style = file.read()

    # Create a <style> tag with the CSS content
    style_tag = f"<style>{style}</style>"

    # Find the position of the <head> tag and inject the <style> tag after it
    head_index = html_content.find("<head>")
    if head_index != -1:
        head_index += len("<head>")
        html_content = html_content[:head_index] + style_tag + html_content[head_index:]
    else:
        print("Warning: <head> tag not found in the HTML content. Style not injected.")

    return html_content

def TilingWindowHTMLMaker(markdownPathArray, grade: str) -> str:
    """Modifies the existing index.html by adding iframes for each document dynamically and returns the modified HTML as a string."""
    
    # Path to the existing index.html
    index_path = './web/template/index.html'

    # Check if index.html exists
    if not os.path.exists(index_path):
        return {"error": "index.html not found in the /web directory."}
    
    # Read the existing HTML content from index.html
    with open(index_path, 'r') as file:
        html_content = file.read()

    # Begin modifying the body of the HTML content
    body_start = html_content.find('<body>')
    body_end = html_content.find('</body>', body_start)

    if body_start == -1 or body_end == -1:
        return {"error": "HTML structure in index.html is not correct."}
    
    body_content = html_content[body_start + len('<body>'):body_end]

    # Loop through each markdown file in the array and add it
    new_content = ""
    for markdownPath in markdownPathArray:
        # Convert each markdown file to HTML
        html_document = MarkdownToHTML(markdownPath, grade)

        # Wrap the HTML content inside an iframe
        iframe_code = f"""
            <div class="window"><div class="gap">{html_document}</div></div>
        """
        
        # Add iframe to the new content
        new_content += iframe_code

    # Replace the old body content with the new content
    updated_html = html_content[:body_start + len('<body>')] + new_content + html_content[body_end:]

    # Inject styles into the updated HTML
    updated_html = injectStyle(updated_html, stylesheet="./web/style.css")

    # Return the dynamically modified HTML content
    return updated_html

def getDocsFromGrade(grade: str):
    """Returns an array of files in the specified grade's path."""
    path = f"./content/{grade}/"

    if not os.path.exists(path):
        return {"error": "Grade folder not found."}
    
    try:
        files = os.listdir(path)
        # Filter out directories if needed and return only files
        files = [file for file in files if os.path.isfile(os.path.join(path, file))]
        print(f">>>> files: {files}")
        return files
    except Exception as e:
        return {"error": str(e)}

def assemble(grade: str):
    """Return TilingWindowHTMLMaker(getDocsFromGrade(grade))"""
    # Get list of document filenames for the specified grade
    documents = getDocsFromGrade(grade)
    
    # Ensure the result is a list (not an error message or dictionary)
    if isinstance(documents, list):
        # Assuming getDocsFromGrade returns a list of document names
        return TilingWindowHTMLMaker(documents, grade=grade)
    else:
        # If there's an error in getDocsFromGrade, return the error message
        return documents

def html(path: str, stylesheet: str):
    """Return html"""
    with open(path, 'r') as file:
        html = file.read()
    html = injectStyle(html_content=html, stylesheet=stylesheet)
    return html

def DirectoryTreeJSONFormat(inFolder: str) -> dict:
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

    if not os.path.exists(inFolder):
        return {"error": f"Folder {inFolder} does not exist."}

    if not os.path.isdir(inFolder):
        return {"error": f"Path {inFolder} is not a directory."}

    return build_tree(inFolder)