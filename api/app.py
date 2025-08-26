import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, jsonify
from utils.pdf import extract_text_from_pdf
from utils.nlp import classify_email, suggest_reply, clean_text

app = Flask(__name__, template_folder="../templates", static_folder="../static")

def read_txt(file_storage) -> str:
    content = file_storage.read()
    try:
        return content.decode("utf-8")
    except Exception:
        return content.decode("latin-1", errors="ignore")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/classify", methods=["POST"])
def classify():
    text = request.form.get("email_text", "").strip()

    if not text and "email_file" in request.files:
        f = request.files["email_file"]
        if f and f.filename:
            if f.filename.lower().endswith(".pdf"):
                text = extract_text_from_pdf(f.stream)
            elif f.filename.lower().endswith(".txt"):
                text = read_txt(f)
            else:
                return jsonify({"error": "Formato não suportado. Envie .txt ou .pdf."}), 400

    text = clean_text(text)
    if not text:
        return jsonify({"error": "Nenhum texto de e-mail enviado."}), 400

    cls = classify_email(text)
    suggestion = suggest_reply(text, cls["label"])
    return jsonify({
        "category": cls["label"],
        "confidence": round(cls["score"], 3),
        "suggested_reply": suggestion
    })

@app.route("/healthz", methods=["GET"])
def health():
    return {"status": "ok"}, 200
