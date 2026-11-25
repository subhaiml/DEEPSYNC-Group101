"""Analyze a selected video and open the evidence page without a web server."""
import json
import sys
import tempfile
import webbrowser
from pathlib import Path
from tkinter import Tk, filedialog, messagebox

from fastapi import UploadFile, HTTPException
from app import analyze, ROOT

def main():
    dialog = None
    if len(sys.argv) == 1:
        dialog = Tk()
        dialog.withdraw()
    filename = sys.argv[1] if len(sys.argv) > 1 else filedialog.askopenfilename(
        parent=dialog, title="Select a single-speaker video",
        initialdir=ROOT / "demo", filetypes=[("Video", "*.mp4 *.mov *.webm *.avi"), ("All files", "*.*")]
    )
    if not filename:
        return
    print("Analyzing the selected video locally...", flush=True)
    try:
        with open(filename, "rb") as clip:
            result = analyze(UploadFile(file=clip, filename=Path(filename).name))
    except HTTPException as error:
        messagebox.showerror("DEEPSYNC", str(error.detail), parent=dialog)
        return
    page = (ROOT / "index.html").read_text(encoding="utf-8-sig")
    payload = json.dumps(result, allow_nan=False).replace("<", "\\u003c")
    page = page.replace("</body>", "<script>el('form').closest('section').hidden=true;display(" +
                        payload + ");</script></body>")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", prefix="DEEPSYNC-",
                                     encoding="utf-8", delete=False) as output:
        output.write(page)
    report = Path(output.name)
    print("Evidence page saved at", report)
    webbrowser.open(report.as_uri())

if __name__ == "__main__":
    main()

