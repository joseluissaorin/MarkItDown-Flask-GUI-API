
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

    def generate():
        results = []
        temp_dir = tempfile.mkdtemp()
    
    try:
        for file in files:
            temp_path = os.path.join(temp_dir, file.filename)
            file.save(temp_path)
            
            try:
                result = md.convert(temp_path)
                output_path = os.path.join(temp_dir, f"{os.path.splitext(file.filename)[0]}-MarkItDown.md")
                
                with open(output_path, 'w') as f:
                    f.write(result.text_content)
                
                results.append({
                    'path': output_path,
                    'filename': f"{os.path.splitext(file.filename)[0]}-MarkItDown.md"
                })
            except Exception as e:
                print(f"Error converting {file.filename}: {str(e)}")
                continue

        if results:
            yield jsonify({
                'files': [{
                    'content': open(r['path'], 'r').read(),
                    'filename': r['filename']
                } for r in results]
            }).get_data(as_text=True)
        else:
            yield jsonify({'error': 'No files were converted successfully'}).get_data(as_text=True)

    return app.response_class(generate(), mimetype='application/json')

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
