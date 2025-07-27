# 📄 PDF Structure Tool – Adobe "Connecting the Dots" Challenge (Round 1A)

This project is built for **Round 1A** of the Adobe India Hackathon 2025 – *"Connecting the Dots Challenge"*. The goal is to reimagine the humble PDF as an intelligent, structured experience by extracting title and heading-level outlines from raw PDFs.

---

## ✨ What It Does

This solution:

* Accepts a `.pdf` file (up to 50 pages)
* Extracts:

  * Title (largest font on first page)
  * Headings with hierarchy: **H1**, **H2**, **H3**
  * Page numbers for each heading
* Outputs a clean `.json` file in the required format

### ✅ Sample Output Format

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
```

---

## 🔄 Project Approach

* **Multilingual Support**: Detects script type (English, Hindi, CJK, Arabic, Japanese etc.) using Unicode block names.
* **Heading Detection Logic**: Combines heuristics like font size, boldness, Y-position on page, and semantic keyword presence.
* **Font Size-Based Hierarchy**: Top 3 most frequent font sizes are mapped to H1, H2, H3 levels.
* **Title Extraction**: Selects the largest font text from page 1.
* **Duplicate Filtering**: Ensures each heading is included once even if repeated.

---

## 🚀 How to Build & Run the Project

### 1. Install Python Dependencies

```bash
pip install pymupdf
```

### 2. Folder Structure

```
project/
├── input/               # Place your PDF files here
├── output/              # Output JSONs will be saved here
├── extractor.py         # Main script file
```

### 3. Run the Extractor

```bash
python extractor.py
```

---

## 📊 Models & Libraries Used

* **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)** — for parsing and analyzing PDF text blocks.
* **Python built-ins**: `unicodedata`, `collections.Counter`, `os`, `json` — for text analysis and script detection.

---

## 🚧 Docker Support

This project includes a **Dockerfile** to simplify execution and dependency setup across environments.

### Dockerfile Purpose:

* Creates a minimal Python environment using `python:3.10-slim`
* Installs project dependencies from `requirements.txt`
* Copies your script and required files into the container
* Runs the `extractor.py` automatically

### Sample Dockerfile

```Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "extractor.py"]
```

### requirements.txt

```
PyMuPDF==1.23.7
```

### Build and Run Docker Image

```bash
docker build -t pdf-structure-tool .
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-structure-tool
```

> Make sure to mount `input/` and `output/` folders when running the container.

---

## 👨‍💼 Authors

Made with ❤️ by:

* **Tanveer Singh**
* **Sehajdeep Singh**
* **Tarun Bhatti**

All authors are final-year undergraduate students from **Thapar Institute of Engineering & Technology**, Patiala.

---
