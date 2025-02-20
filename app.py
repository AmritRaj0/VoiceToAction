from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS  
import os
from process_audio import transcribe_audio, extract_key_points
from email_service import send_email

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists

@app.route("/")
def home():
    """Render the frontend page"""
    return render_template("index.html")

@app.route("/static/<path:filename>")
def serve_static(filename):
    """Ensure static files load properly"""
    return send_from_directory("static", filename)

@app.route("/", methods=["POST"])
def process_audio():
    """Handles file upload, processes audio, extracts tasks, and sends email"""
    
    email = request.form.get("email")
    audio_file = request.files.get("audio_file")

    if not email or not audio_file:
        return jsonify({"error": "Email and audio file are required!"})

    # Save the file
    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(file_path)

    # Process audio
    transcribed_text = transcribe_audio(file_path)
    if "Error" in transcribed_text:
        return jsonify({"error": transcribed_text})

    # Extract action items & include full transcript
    extraction_result = extract_key_points(transcribed_text)

    # Send email with transcript and extracted tasks
    email_status = send_email(email, f"**Transcript:**\n{extraction_result['transcribed_text']}\n\n**Extracted Tasks:**\n{extraction_result['extracted_tasks']}")

    return jsonify({
        "message": email_status,
        "transcribed_text": extraction_result["transcribed_text"],
        "extracted_report": extraction_result["extracted_tasks"]
    })

if __name__ == "__main__":
    app.run(debug=True)
