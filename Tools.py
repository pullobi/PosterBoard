import os
import markdown # type: ignore


def convert_to_markdown(document: str):
    """Converts a non-Markdown document to Markdown."""
    doc_path = f"./temp/{document}"
    target_doc_path = f"./temp/{document}.md"

    if document.endswith('.md'):
        print(f"Document {document} is already in Markdown format. Skipping conversion.")
        return

    if not os.path.exists(doc_path):
        print(f"Error: The document {document} does not exist at {doc_path}.")
        return

    try:
        pypandoc.convert_file(doc_path, 'md', outputfile=target_doc_path) # type: ignore
        print(f"Document converted to markdown and saved to {target_doc_path}")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")


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

