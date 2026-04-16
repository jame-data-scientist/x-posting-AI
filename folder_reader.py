"""
folder_reader.py
Reads your project folder and builds a context summary for Gemini.
Supports: .txt, .md, .py, .json, .html, .csv, and plain text files.
"""

import os
from pathlib import Path

# File types to read as text content
TEXT_EXTENSIONS = {".txt", ".md", ".py", ".json", ".html", ".htm", ".csv", ".yaml", ".yml", ".toml", ".rst"}

# Max chars to read per file (avoid token overload)
MAX_CHARS_PER_FILE = 50000
# Max total chars to send to Gemini
MAX_TOTAL_CHARS = 100000


def read_project_folder(folder_path: str) -> str:
    """
    Walks the project folder and returns a structured text summary
    of its contents for use as Gemini context.
    """
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Project folder not found: {folder_path}")

    parts = []
    total_chars = 0
    file_count = 0

    for root, dirs, files in os.walk(folder):
        # Skip hidden dirs and common noise folders
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                   {"__pycache__", "node_modules", ".git", "venv", "env", ".venv", "dist", "build"}]

        for filename in files:
            filepath = Path(root) / filename
            ext = filepath.suffix.lower()

            if ext not in TEXT_EXTENSIONS:
                continue

            try:
                text = filepath.read_text(encoding="utf-8", errors="ignore")
                text = text.strip()
                if not text:
                    continue

                # Truncate long files
                truncated = False
                if len(text) > MAX_CHARS_PER_FILE:
                    text = text[:MAX_CHARS_PER_FILE]
                    truncated = True

                rel_path = filepath.relative_to(folder)
                header = f"### File: {rel_path}"
                if truncated:
                    header += " [truncated]"

                part = f"{header}\n{text}\n"
                parts.append(part)

                total_chars += len(part)
                file_count += 1

                if total_chars >= MAX_TOTAL_CHARS:
                    parts.append("### [Additional files omitted to stay within context limit]\n")
                    break

            except Exception as e:
                parts.append(f"### File: {filepath.name} [could not read: {e}]\n")

        if total_chars >= MAX_TOTAL_CHARS:
            break

    if not parts:
        return f"[No readable text files found in {folder_path}]"

    summary = f"PROJECT FOLDER: {folder.name} ({file_count} files read)\n\n"
    summary += "\n".join(parts)
    return summary
