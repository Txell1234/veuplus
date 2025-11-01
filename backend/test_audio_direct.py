#!/usr/bin/env python3
"""
Test directe d'àudio Edge-TTS
"""
import asyncio
import edge_tts
import base64
import tempfile
import os

async def test_audio():
    try:
        print("🔍 Testant àudio directe...")
        
        text = "Hola, aquesta és una prova de síntesi de veu."
        voice_id = "es-ES-ElviraNeural"
        
        print(f"🎵 Generant: '{text}' amb '{voice_id}'")
        
        communicate = edge_tts.Communicate(text, voice_id)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        await communicate.save(temp_path)
        
        with open(temp_path, "rb") as f:
            audio_data = f.read()
        
        audio_base64 = base64.b64encode(audio_data).decode()
        os.unlink(temp_path)
        
        print(f"✅ Àudio generat: {len(audio_data)} bytes")
        print(f"✅ Base64: {audio_base64[:100]}...")
        
        # Crear fitxer HTML per provar
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Audio Directe</title>
</head>
<body>
    <h1>Test Audio Edge-TTS</h1>
    <p>Text: {text}</p>
    <p>Veu: {voice_id}</p>
    <p>Mida: {len(audio_data)} bytes</p>
    <audio controls>
        <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
        El teu navegador no suporta àudio.
    </audio>
    <br><br>
    <button onclick="playAudio()">Reproduir Àudio</button>
    
    <script>
        function playAudio() {{
            const audio = new Audio('data:audio/wav;base64,{audio_base64}');
            audio.play();
        }}
    </script>
</body>
</html>
"""
        
        with open("test_audio_direct.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("✅ Fitxer HTML creat: test_audio_direct.html")
        print("🌐 Obre: file:///" + os.path.abspath("test_audio_direct.html"))
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_audio())
