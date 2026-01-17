
import os
import shutil
import re
from extract_code_blocks import extract_code_blocks

SOURCE_ROOT = "/Users/jerrylee/coding/skills"
TARGET_ROOT = "/Users/jerrylee/coding/.agent/skills"

def get_best_source_file(skill_dir):
    """
    Determines the best source file (SKILL.md vs SKILL.antigravity.md).
    """
    p1 = os.path.join(skill_dir, "SKILL.antigravity.md")
    p2 = os.path.join(skill_dir, "SKILL.md")
    
    has_p1 = os.path.exists(p1)
    has_p2 = os.path.exists(p2)
    
    if has_p1 and has_p2:
        # Compare size/completeness. usage logic: prioritize antigravity if it has content
        s1 = os.path.getsize(p1)
        s2 = os.path.getsize(p2)
        if s1 > s2 * 0.8: # If antigravity is at least 80% size of original or larger, prefer it.
            return p1
        if s1 > 500: # If antigravity has substantial content (>500 bytes)
            return p1
        return p2
    elif has_p1:
        return p1
    elif has_p2:
        return p2
    return None

def clean_and_migrate(skill_name, source_file):
    print(f"Migrating {skill_name} from {source_file}...")
    
    target_dir = os.path.join(TARGET_ROOT, skill_name)
    os.makedirs(os.path.join(target_dir, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "examples"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "resources"), exist_ok=True)
    
    # Extract blocks
    blocks = extract_code_blocks(source_file)
    
    with open(source_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    new_content_lines = []
    
    # Simple strategy: iterate lines, skip lines belonging to extracted blocks, invoke replacement text
    # But extract_code_blocks doesn't give end lines easily without re-parsing or logic.
    # Let's use a simpler approach for the content rewrite: 
    # Read the file line by line. If we enter a code block that we decided to extract, write the link instead.
    
    lines = original_content.splitlines()
    skip_until_end_of_block = False
    
    block_map = {b['start_line']: b for b in blocks}
    
    extracted_count = 0
    
    # Heuristic to name extracted files
    # We count by language to give unique names if multiple blocks exist
    lang_counters = {}
    
    for i, line in enumerate(lines):
        lineno = i + 1
        
        if lineno in block_map:
            block = block_map[lineno]
            lang = block['language'] if block['language'] else "text"
            
            # Filter logic: Don't extract small one-liners or headers, only meaningful blocks?
            # For this task, we extract everything that looks like a script or example.
            # Arbitrary threshold: content length > 50 chars or multiple lines
            if len(block['content'].splitlines()) > 3:
                # Decide target category
                category = "examples"
                ext = "txt"
                if lang in ["python", "py"]: ext = "py"; category = "scripts" if "import" in block['content'] else "examples"
                elif lang in ["bash", "sh", "shell"]: ext = "sh"; category = "scripts"
                elif lang in ["json"]: ext = "json"; category = "resources"
                elif lang in ["yaml", "yml"]: ext = "yaml"; category = "resources"
                elif lang in ["javascript", "js", "jsx"]: ext = "js"; category = "examples"
                
                lang_counters[category] = lang_counters.get(category, 0) + 1
                filename = f"{skill_name}_{category}_{lang_counters[category]}.{ext}"
                target_path = os.path.join(target_dir, category, filename)
                
                with open(target_path, 'w', encoding='utf-8') as tf:
                    tf.write(block['content'])
                
                # Write link to SKILL.md
                new_content_lines.append(f"\n> [!TIP]")
                new_content_lines.append(f"> 已提取內容至：[{filename}]({category}/{filename})\n")
                
                skip_until_end_of_block = True
                extracted_count += 1
                continue
            else:
                # Keep small blocks inline
                skip_until_end_of_block = True # We still skip logic below relies on regex, wait. 
                # extract_code_blocks uses regex. 
                # Re-implementing line skipping logic here is tricky without strict state.
                # Let's just blindly keep small blocks? No, the loop structure is `if lineno in block_map`.
                # If we don't extract, we must PRINT the original lines.
                # But we are in a 'skip' mode if we set the flag.
                # Let's adjust:
                pass

        if skip_until_end_of_block:
             if line.strip().startswith("```") and lineno not in block_map: # End of block
                 skip_until_end_of_block = False
                 # If we decided NOT to extract (small block), we missed printing the content.
                 # This logic is flawed. 
             continue
        
        # If not starting a block, just print
        # EXCEPT... what if we are inside a block we actully wanted to keep?
        # Let's refactor: separate parsing and rewriting.
    
    # Better approach:
    # 1. Identify ranges to CUT.
    # 2. Construct new string.
    
    cut_ranges = []
    
    for block in blocks:
        # Determine strict start/end
        # extract_code_blocks returns content and start_line, but not end_line?
        # We need end line.
        # Let's re-read the file to find end lines
        pass 
        # Actually... let's just use the `extract_code_blocks` imported logic if possible? 
        # It doesn't return end line.
    
    # Let's rewrite simple logic here to match standard
    
    final_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r'^```(\w*)', line.strip())
        if match:
             # It's a start of block
             start_idx = i
             lang = match.group(1)
             
             # Find end
             end_idx = -1
             content_buffer = []
             for j in range(i+1, len(lines)):
                 if re.match(r'^```\s*$', lines[j].strip()):
                     end_idx = j
                     break
                 content_buffer.append(lines[j])
             
             if end_idx != -1:
                 content_str = "\n".join(content_buffer)
                 # Decision: Extract?
                 if len(content_buffer) > 5: # Extract if > 5 lines
                      # Determine metadata
                      category = "examples"
                      ext = "txt"
                      if lang in ["python", "py"]: ext = "py"; category = "examples" # Default to examples for safety unless obvious script
                      if lang in ["bash", "sh"]: ext = "sh"; category = "scripts"
                      if lang in ["json", "yaml"]: category = "resources"
                      
                      lang_counters[category] = lang_counters.get(category, 0) + 1
                      # Try to find a name comment?
                      # Simple naming
                      filename = f"example_{lang_counters[category]}.{ext}"
                      if category == "scripts": filename = f"script_{lang_counters[category]}.{ext}"
                      
                      # Write file
                      fpath = os.path.join(target_dir, category, filename)
                      with open(fpath, 'w', encoding='utf-8') as out:
                          out.write(content_str)
                      
                      # Add link
                      final_lines.append(f"\n詳細內容請參閱：[{filename}]({category}/{filename})\n")
                      
                      i = end_idx + 1
                      continue
                 else:
                     # Keep inline
                     final_lines.append(line)
                     i += 1
                     continue
             else:
                 # No end found, legitimate error or text? keep it
                 final_lines.append(line)
                 i += 1
        else:
            final_lines.append(line)
            i += 1
            
    # Write SKILL.md
    with open(os.path.join(target_dir, "SKILL.md"), 'w', encoding='utf-8') as f:
        f.write("\n".join(final_lines))

def main():
    if not os.path.exists(TARGET_ROOT):
        os.makedirs(TARGET_ROOT)
        
    for item in os.listdir(SOURCE_ROOT):
        skill_dir = os.path.join(SOURCE_ROOT, item)
        if os.path.isdir(skill_dir):
            best_source = get_best_source_file(skill_dir)
            if best_source:
                clean_and_migrate(item, best_source)
            else:
                print(f"Skipping {item}: No SKILL.md found.")

if __name__ == "__main__":
    main()
