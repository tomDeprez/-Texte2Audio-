import os
import uuid
import json
import base64
from flask import Flask, request, jsonify, send_file
from TTS.api import TTS
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'voices'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs("static", exist_ok=True)

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

VOICES_JSON = os.path.join(app.config['UPLOAD_FOLDER'], "saved_voices.json")
if not os.path.exists(VOICES_JSON):
    with open(VOICES_JSON, "w", encoding="utf-8") as f:
        json.dump({}, f)

AUDIO_HISTORY_JSON = os.path.join("static", "generated_audios.json")
if not os.path.exists(AUDIO_HISTORY_JSON):
    with open(AUDIO_HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump([], f)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>AI TTS Premium</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
      display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
      background: linear-gradient(135deg, #fafafa 0%, #e0e0e0 100%);
      min-height: 100vh; padding: 2rem;
    }
    h1 { margin-bottom: 1rem; color: #333; }
    form {
      background: #fff; padding: 1.5rem; border-radius: 10px;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); width: 600px; max-width: 90%;
      display: flex; flex-direction: column; gap: 1rem;
      margin-bottom: 2rem;
    }
    form label { font-weight: bold; margin-bottom: 0.5rem; }
    textarea {
      width: 100%; min-height: 60px; resize: vertical; font-size: 1rem; padding: 0.5rem;
    }
    select, input[type="file"], input[type="text"] {
      padding: 0.5rem; font-size: 1rem;
    }
    button {
      padding: 0.75rem 1rem; font-size: 1rem; background-color: #5c6bc0;
      color: #fff; border: none; border-radius: 5px; cursor: pointer;
      transition: background 0.2s ease-in; margin-top: 1rem; align-self: flex-start;
    }
    button:hover { background-color: #3f51b5; }
    .loader {
      margin: 1rem auto; width: 48px; height: 48px; border-radius: 50%; position: relative;
      border: 4px solid transparent; border-top: 4px solid #3f51b5; animation: spin 1s linear infinite;
      display: none;
    }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    .result { margin-top: 1rem; text-align: center; }
    audio { margin-top: 1rem; width: 100%; outline: none; }
    .section-title { margin-top: 1rem; margin-bottom: 0.5rem; font-weight: bold; }
    .history-item {
      background: #fff; margin: 0.5rem 0; padding: 1rem; border-radius: 10px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .copy-btn {
      margin-top: 0.5rem; padding: 0.5rem 1rem; font-size: 0.9rem;
      background-color: #8e24aa; border: none; border-radius: 5px; color: #fff;
      cursor: pointer; transition: background 0.2s ease-in;
    }
    .copy-btn:hover { background-color: #6a1b9a; }
  </style>
</head>
<body>
  <h1>AI TTS Premium</h1>

  <form id="ttsForm">
    <label for="text">Texte à convertir en audio :</label>
    <textarea id="text" name="text"></textarea>

    <label for="language">Langue :</label>
    <select id="language" name="language">
      <option value="en">Anglais (en)</option>
      <option value="fr">Français (fr)</option>
      <option value="es">Espagnol (es)</option>
      <option value="it">Italien (it)</option>
    </select>

    <label for="savedVoice">Voix enregistrée (optionnel) :</label>
    <select id="savedVoice" name="savedVoice">
      <option value="">(Aucune)</option>
    </select>

    <button type="submit">Générer l'audio</button>
  </form>

  <div class="loader" id="loader"></div>
  <div class="result" id="result"></div>

  <form id="uploadForm" enctype="multipart/form-data" style="margin-top:2rem;">
    <label class="section-title">Enregistrer une nouvelle voix de référence (clonage vocal) :</label>
    <label for="voiceName">Nom de la voix :</label>
    <input type="text" id="voiceName" name="voiceName" required/>

    <label for="voiceFile">Fichier audio :</label>
    <input type="file" id="voiceFile" name="voiceFile" accept="audio/*" required/>

    <button type="submit">Enregistrer la voix</button>
  </form>

  <div class="section-title">Historique des audios générés :</div>
  <div id="history"></div>

  <script>
    const ttsForm = document.getElementById('ttsForm');
    const uploadForm = document.getElementById('uploadForm');
    const loader = document.getElementById('loader');
    const resultDiv = document.getElementById('result');
    const savedVoiceSelect = document.getElementById('savedVoice');
    const historyDiv = document.getElementById('history');

    async function fetchSavedVoices() {
      const res = await fetch('/list_voices');
      const data = await res.json();
      if (data.status === 'ok') {
        savedVoiceSelect.innerHTML = '<option value="">(Aucune)</option>';
        Object.keys(data.voices).forEach(voiceName => {
          const opt = document.createElement('option');
          opt.value = data.voices[voiceName];
          opt.textContent = voiceName;
          savedVoiceSelect.appendChild(opt);
        });
      }
    }
    fetchSavedVoices();

    async function fetchHistory() {
      const res = await fetch('/audio_history');
      const data = await res.json();
      if (data.status === 'ok') {
        historyDiv.innerHTML = '';
        data.history.forEach(item => {
          const container = document.createElement('div');
          container.className = 'history-item';
          container.innerHTML = `
            <p><strong>Texte:</strong> ${item.text}</p>
            <audio controls src="${item.url}"></audio>
            <button class="copy-btn" onclick="copyBase64('${item.filename}')">Copier en Base64</button>
          `;
          historyDiv.appendChild(container);
        });
      }
    }
    fetchHistory();

    async function copyBase64(filename) {
      try {
        const res = await fetch('/get_base64?filename=' + filename);
        const data = await res.json();
        if (data.status === 'ok') {
          await navigator.clipboard.writeText(data.base64);
          alert('Audio copié en base64 !');
        }
      } catch (err) {
        alert('Erreur de copie en base64');
      }
    }

    ttsForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = document.getElementById('text').value.trim();
      const language = document.getElementById('language').value;
      const savedVoice = savedVoiceSelect.value;
      if(!text) return;

      loader.style.display = 'block';
      resultDiv.innerHTML = '';

      try {
        const response = await fetch('/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, language, voicePath: savedVoice })
        });
        const data = await response.json();
        loader.style.display = 'none';
        if (data.status === 'ok') {
          resultDiv.innerHTML = `
            <p>Audio généré :</p>
            <audio controls src="${data.url}"></audio>
          `;
          fetchHistory();
        } else {
          resultDiv.innerHTML = '<p>Une erreur est survenue.</p>';
        }
      } catch (err) {
        loader.style.display = 'none';
        resultDiv.innerHTML = '<p>Erreur lors de la requête.</p>';
      }
    });

    uploadForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const voiceName = document.getElementById('voiceName').value.trim();
      const voiceFile = document.getElementById('voiceFile').files[0];
      if(!voiceName || !voiceFile) return;

      loader.style.display = 'block';
      resultDiv.innerHTML = '';

      const formData = new FormData();
      formData.append('voiceName', voiceName);
      formData.append('voiceFile', voiceFile);

      try {
        const response = await fetch('/upload_voice', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        loader.style.display = 'none';
        if (data.status === 'ok') {
          resultDiv.innerHTML = '<p>Voix enregistrée avec succès !</p>';
          fetchSavedVoices();
        } else {
          resultDiv.innerHTML = `<p>Une erreur est survenue: ${data.message}</p>`;
        }
      } catch (err) {
        loader.style.display = 'none';
        resultDiv.innerHTML = '<p>Erreur lors de la requête.</p>';
      }
    });
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_PAGE

@app.route('/list_voices', methods=['GET'])
def list_voices():
    with open(VOICES_JSON, "r", encoding="utf-8") as f:
        voices = json.load(f)
    return jsonify({"status": "ok", "voices": voices})

@app.route('/audio_history', methods=['GET'])
def audio_history():
    with open(AUDIO_HISTORY_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify({"status": "ok", "history": data})

@app.route('/get_base64', methods=['GET'])
def get_base64_route():
    filename = request.args.get('filename', '')
    if not filename:
        return jsonify({"status": "error", "message": "Filename manquant"}), 400
    file_path = os.path.join("static", filename)
    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "Fichier introuvable"}), 404
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    return jsonify({"status": "ok", "base64": encoded})

@app.route('/upload_voice', methods=['POST'])
def upload_voice():
    if 'voiceFile' not in request.files or 'voiceName' not in request.form:
        return jsonify({"status": "error", "message": "Fichier ou nom manquant."}), 400
    voice_file = request.files['voiceFile']
    voice_name = request.form['voiceName'].strip()
    if not voice_file or not voice_name:
        return jsonify({"status": "error", "message": "Données invalides."}), 400

    filename = secure_filename(voice_file.filename)
    ext = os.path.splitext(filename)[1]
    new_filename = f"{voice_name}{ext}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    voice_file.save(save_path)

    with open(VOICES_JSON, "r", encoding="utf-8") as f:
        voices = json.load(f)
    voices[voice_name] = save_path
    with open(VOICES_JSON, "w", encoding="utf-8") as f:
        json.dump(voices, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "ok", "message": "Voix enregistrée."})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    text = data.get('text', '').strip()
    language = data.get('language', 'en')
    voice_path = data.get('voicePath', '')
    if not text:
        return jsonify({"status": "error", "message": "Aucun texte fourni"}), 400

    try:
        filename = f"output_{uuid.uuid4()}.wav"
        filepath = os.path.join("static", filename)
        if voice_path:
            tts.tts_to_file(text=text, speaker_wav=voice_path, language=language, file_path=filepath)
        else:
            tts.tts_to_file(text=text, language=language, file_path=filepath)

        audio_url = f"/static/{filename}"
        with open(AUDIO_HISTORY_JSON, "r", encoding="utf-8") as f:
            history = json.load(f)
        history.append({
            "filename": filename,
            "url": audio_url,
            "text": text
        })
        with open(AUDIO_HISTORY_JSON, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        return jsonify({"status": "ok", "url": audio_url})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
