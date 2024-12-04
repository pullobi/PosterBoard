import shutil
import os
import markdown

import os
import pypandoc

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

def MarkdownToHTML(markdownPath: str, grade: str) -> str:
    """Converts markdown to HTML, then returns it."""

    # Read the markdown file
    ##
    with open(f"./content/{grade}/{markdownPath}", 'r') as markdown_file:
        markdown_content = markdown_file.read()
    
    # Convert markdown to HTML using the markdown library
    html_content = markdown.markdown(markdown_content)
    
    return html_content

def TilingWindowHTMLMaker(markdownPathArray, grade: str) -> str:
    """Modifies the existing index.html by adding iframes for each document dynamically and returns the modified HTML as a string."""
    
    # Path to the existing index.html
    index_path = './web/index.html'

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

    with open("./web/style.css", 'r') as file:
        style = file.read()

    # Add the title and grade-specific heading
    new_content = f"""
    <style>
    {style}
    </style>
    """

    # Loop through each markdown file in the array and a
    for markdownPath in markdownPathArray:
        # Convert each markdown file to HTML
        html_document = MarkdownToHTML(markdownPath, grade)

        
        # Wrap the HTbML content inside an iframe
        iframe_code = f"""
            <div class="window"><div class="gap">{html_document}</div></div>
            
        """
        
        # Add iframe to the new content
        new_content += iframe_code
    


    # Replace the old body content with the new content
    updated_html = html_content[:body_start + len('<body>')] + new_content + html_content[body_end:]

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