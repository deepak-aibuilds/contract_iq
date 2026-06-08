import re

def chunk_by_sections(text: str) -> list[dict]:
    
    pattern = r'(?m)^(?:Section\s+\d+[\.\:]?\s+)?(\d+[\.\:]?\s+)?([A-Z][A-Z\s\-]{3,}[A-Z])$'

    
    matches = list(re.finditer(pattern, text))
    

    if not matches:
        return [{"section": "FULL_DOCUMENT", "content": text.strip()}]
    
    chunks = []
    for i, match in enumerate(matches):
        header = match.group().strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        
        if content: 
            chunks.append({
                "section": header,
                "content": content
            })
    
    return chunks