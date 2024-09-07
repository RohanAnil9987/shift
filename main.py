from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

GROQ_API_KEY = "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"


@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    
    # Save the audio file temporarily
    temp_audio_path = 'audio.wav'
    audio_file.save(temp_audio_path)

    url = "https://api.groq.com/openai/v1/audio/translations"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    data = {
        "model": "whisper-large-v3",
        "prompt": "Specify context or spelling",
        "temperature": 0,
        "response_format": "json"
    }
    try:
        with open(temp_audio_path, "rb") as file:
            files = {"file": file}
            response = requests.post(url, headers=headers, data=data, files=files)
    finally:
        # Close the file before attempting to remove it
        if 'file' in locals():
            file.close()

        # Try to remove the file
        try:
            os.remove(temp_audio_path)
        except PermissionError:
            print(f"Warning: Unable to delete {temp_audio_path}. It may still be in use.")

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Transcription failed', 'details': response.text}), 500
    
    
@app.route('/combine_words', methods=['POST'])
def combine_words():
    word1 = request.form.get('word1')
    word2 = request.form.get('word2')

    if not word1 or not word2:
        return jsonify({'error': 'Please provide two words'}), 400

    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""
    Combine the words "{word1}" and "{word2}" to create a new, unique word that is related to both input words. 
    The new word should be creative and meaningful. 
    Provide only the new word as the response, without any additional explanation.
    The word should be meaningful, which can be found in a dictionary.
    Example:
    Input: wood, fire
    Output: campfire
    
    Now, combine these words: {word1}, {word2}
    """

    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 50
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        new_word = response.json()['choices'][0]['message']['content'].strip()
        return jsonify({'new_word': new_word})
    else:
        return jsonify({'error': 'Word combination failed', 'details': response.text}), 500

if __name__ == '__main__':
    app.run(debug=True)

