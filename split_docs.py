import os
import re

source_file = r"e:\governed-rag\docs\governed-ai-frameworks-cheatsheet.md"
output_dir = r"e:\governed-rag\data\docs"

os.makedirs(output_dir, exist_ok=True)

with open(source_file, "r", encoding="utf-8") as f:
    content = f.read()

# Split by "## " (but keep the "## ")
parts = re.split(r"(?=^## )", content, flags=re.MULTILINE)

# The first part is the header, which we can either ignore or prepend to the first real doc.
# Let's just grab the actual sections.
file_count = 0
for part in parts:
    part = part.strip()
    if not part.startswith("## "):
        continue
        
    # Extract a filename from the heading
    heading_line = part.split("\n")[0]
    heading_text = heading_line.replace("## ", "").strip()
    
    # clean up for filename
    safe_name = re.sub(r'[^a-zA-Z0-9]+', '-', heading_text).strip('-').lower()
    
    # Let's remove the leading number e.g., "1-eu-ai-act" -> "eu-ai-act" if we want, or keep it.
    
    out_path = os.path.join(output_dir, f"{safe_name}.md")
    with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(part)
    
    file_count += 1
    print(f"Created: {out_path} ({len(part.split())} words)")

print(f"Total files created: {file_count}")
