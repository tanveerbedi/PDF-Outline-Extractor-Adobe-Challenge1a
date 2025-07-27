import os
import fitz  # PyMuPDF
import json
import unicodedata
from collections import Counter


def normalize_font_size(size, precision=0.5):
    return round(size / precision) * precision


def detect_script(text):
    """Detect Unicode script (like DEVANAGARI, CJK, etc.)."""
    scripts = set()
    for char in text:
        if char.isalpha():
            try:
                script = unicodedata.name(char).split()[0]
                scripts.add(script)
            except ValueError:
                continue
    return list(scripts)


def is_potential_heading(text, is_bold, y_pos, page_height, scripts):
    """Strict multilingual heading detection."""
    text = text.strip()
    word_count = len(text.split())

    # Reject empty or long lines
    if not text or word_count > 10:
        return False

    # Accept only from top 60% of page
    if y_pos > page_height * 0.60:
        return False

    # Multilingual keywords
    keywords = [
        # English
        "goals", "overview", "objectives", "summary", "mission", "requirements", "pathway",
        # Hindi
        "परिचय", "लक्ष्य", "उद्देश्य", "सारांश", "मिशन"
    ]
    if any(kw in text.lower() for kw in keywords):
        return True

    # Reject paragraphs with punctuation unless short
    if (text.endswith(".") or text.endswith("।")) and word_count > 4:
        return False

    # Non-English script fallback: only accept if bold or keyword
    if any(s in scripts for s in ["DEVANAGARI", "CJK", "ARABIC", "HANGUL"]):
        if is_bold or any(kw in text for kw in keywords):
            return True
        return False

    # English-based heading rules
    if text.isupper() or (is_bold and word_count <= 10):
        return True
    if text.istitle() and word_count <= 6:
        return True

    return False


def extract_blocks(doc):
    """Extracts text blocks from PDF with font/style/position metadata."""
    blocks = []
    for page_num, page in enumerate(doc, start=1):
        page_height = page.rect.height
        for block in page.get_text("dict").get("blocks", []):
            if "lines" not in block:
                continue
            for line in block["lines"]:
                line_text = ""
                max_font_size = 0
                font_names = set()
                for span in line["spans"]:
                    line_text += span["text"]
                    max_font_size = max(max_font_size, span["size"])
                    font_names.add(span.get("font", ""))
                if line_text.strip():
                    is_bold = any("Bold" in f or "bold" in f for f in font_names)
                    blocks.append({
                        "text": line_text.strip(),
                        "font_size": normalize_font_size(max_font_size),
                        "page": page_num,
                        "y": block.get("bbox", [0, 0, 0, 0])[1],
                        "is_bold": is_bold,
                        "page_height": page_height,
                        "scripts": detect_script(line_text)
                    })
    return blocks


def extract_headings_from_pdf(pdf_path):
    """Main logic to extract headings from PDF."""
    doc = fitz.open(pdf_path)
    blocks = extract_blocks(doc)

    if not blocks:
        return {"title": "", "outline": []}

    # Title: largest text on page 1
    first_page_blocks = [b for b in blocks if b["page"] == 1]
    sorted_fp = sorted(first_page_blocks, key=lambda b: (-b["font_size"], b["y"]))
    title = sorted_fp[0]["text"] if sorted_fp else blocks[0]["text"]

    # Top 5 font sizes (more flexible)
    font_counter = Counter(b["font_size"] for b in blocks)
    font_sizes = sorted([f for f, _ in font_counter.most_common(5)], reverse=True)
    h1, h2, h3 = (font_sizes + [0, 0, 0])[:3]

    outline = []
    seen = set()

    for b in blocks:
        if not is_potential_heading(b["text"], b["is_bold"], b["y"], b["page_height"], b["scripts"]):
            continue

        level = None
        if b["font_size"] == h1:
            level = "H1"
        elif b["font_size"] == h2:
            level = "H2"
        elif b["font_size"] == h3:
            level = "H3"

        key = (b["text"].lower(), level)
        if level and key not in seen:
            outline.append({
                "level": level,
                "text": b["text"],
                "page": b["page"]
            })
            seen.add(key)

    return {
        "title": title,
        "outline": outline
    }


def main():
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    print(f"🔍 Scanning for PDFs in: {input_dir}")
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            print(f"📄 Processing: {filename}")
            pdf_path = os.path.join(input_dir, filename)
            result = extract_headings_from_pdf(pdf_path)
            output_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved to: {output_path}")


if __name__ == "__main__":
    main()
