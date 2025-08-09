from flask import Flask, request, render_template
import boto3
import os
import uuid
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25 MB max

# AWS config
S3_BUCKET = 'your-bucket-name'
S3_REGION = 'your-region'
s3 = boto3.client('s3', region_name=S3_REGION)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'zip', 'mp3', 'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file')
        email = request.form['email']

        uploaded_files = []

        for file in files:
            if file and allowed_file(file.filename):
                ext = os.path.splitext(file.filename)[1]
                unique_filename = f"{uuid.uuid4()}{ext}"
                file.save(unique_filename)

                s3.upload_file(
                    Filename=unique_filename,
                    Bucket=S3_BUCKET,
                    Key=unique_filename
                )

                os.remove(unique_filename)
                uploaded_files.append(unique_filename)

        # Here you can add logic to:
        # - Generate pre-signed URLs
        # - Send email to `email` with those links

        return f"Uploaded successfully. Files sent to {email}:<br>{'<br>'.join(uploaded_files)}"

    return render_template('upload.html')

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return "File too large! Max upload size is 25 MB.", 413

if __name__ == '__main__':
    app.run(debug=True)
