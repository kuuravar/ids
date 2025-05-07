import nbformat as nbf
from glob import glob

# Process all notebooks
for notebook_path in glob("*.ipynb", recursive=False):
    ntbk = nbf.read(notebook_path, nbf.NO_CONVERT)
    
    for cell in ntbk.cells:
        if cell.cell_type == "code":
            # Get existing tags or create new list
            tags = cell.metadata.get("tags", [])
            
            # Add tag if not present
            if "hide-input" not in tags:
                tags.append("hide-input")
                cell.metadata["tags"] = tags
    
    # Save changes
    nbf.write(ntbk, notebook_path)
