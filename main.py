
from flask import Flask, render_template, request, jsonify, send_file
from markitdown import MarkItDown
import os
import tempfile

app = Flask('app')
md = MarkItDown()

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
                result = md.convert(temp_path)
                output_path = os.path.join(temp_dir, f"{os.path.splitext(file.filename)[0]}-MarkItDown.md")
                
                with open(output_path, 'w') as f:
                    f.write(result.text_content)
                
                with open(output_path, 'r') as f:
                    content = f.read()
                    
                results.append({
                    'filename': f"{os.path.splitext(file.filename)[0]}-MarkItDown.md",
                    'content': content
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
        result = md.convert(temp_path)
        return jsonify({'markdown': result.text_content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
