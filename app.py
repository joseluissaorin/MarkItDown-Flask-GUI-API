
from flask import Flask, render_template, request, jsonify, send_file
from docling.document_converter import DocumentConverter
import os
import tempfile
import requests

app = Flask('app')
converter = DocumentConverter()

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".opus", ".aac", ".wma", ".webm"}
INFERBOX_URL = os.environ.get("INFERBOX_URL", "http://192.168.1.102:8811").rstrip("/")
INFERBOX_API_KEY = os.environ.get("INFERBOX_API_KEY", "inferbox-scholaris-2024")
INFERBOX_TIMEOUT = int(os.environ.get("INFERBOX_TIMEOUT", "600"))


def _is_audio(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in AUDIO_EXTS


def _format_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds - h * 3600 - m * 60
    if h:
        return f"{h:02d}:{m:02d}:{s:05.2f}"
    return f"{m:02d}:{s:05.2f}"


def _transcribe_via_inferbox(file_path: str, original_name: str) -> str:
    with open(file_path, "rb") as fh:
        r = requests.post(
            f"{INFERBOX_URL}/v1/transcribe",
            files={"file": (original_name, fh, "application/octet-stream")},
            headers={"X-API-Key": INFERBOX_API_KEY},
            timeout=INFERBOX_TIMEOUT,
        )
    if r.status_code != 200:
        snippet = r.text.strip()[:300] or r.reason
        raise RuntimeError(f"InferBox transcribe failed ({r.status_code}): {snippet}")

    data = r.json()
    text = (data.get("text") or "").strip()
    segments = data.get("segments") or []
    title = os.path.splitext(original_name)[0]

    lines = [f"# {title}", ""]
    if text:
        lines.append(text)
        lines.append("")
    if segments:
        lines.append("## Segments")
        lines.append("")
        for seg in segments:
            ts = _format_ts(float(seg.get("start") or 0.0))
            seg_text = (seg.get("text") or "").strip()
            lines.append(f"- `{ts}` {seg_text}")
        lines.append("")
    return "\n".join(lines)


def _convert_to_markdown(file_path: str, original_name: str) -> str:
    if _is_audio(original_name):
        return _transcribe_via_inferbox(file_path, original_name)
    return converter.convert(file_path).document.export_to_markdown()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No file selected'}), 400

    results = []
    temp_dir = tempfile.mkdtemp()

    try:
        for file in files:
            if not file.filename:
                continue
            temp_path = os.path.join(temp_dir, file.filename)
            file.save(temp_path)

            try:
                content = _convert_to_markdown(temp_path, file.filename)
                results.append({
                    'filename': f"{os.path.splitext(file.filename)[0]}-MarkItDown.md",
                    'content': content,
                })
            except Exception as e:
                print(f"Error converting {file.filename}: {str(e)}")
                continue
    finally:
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except:
                    pass
        try:
            os.rmdir(temp_dir)
        except:
            pass

    if results:
        return jsonify({'files': results})
    return jsonify({'error': 'No files were converted successfully'}), 400

@app.route('/api/convert', methods=['POST'])
def api_convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    file.save(temp_path)

    try:
        markdown = _convert_to_markdown(temp_path, file.filename)
        return jsonify({'markdown': markdown})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
