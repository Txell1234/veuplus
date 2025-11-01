#!/usr/bin/env python3
"""
Test simple per Edge-TTS
"""
import asyncio
import edge_tts
import base64
import tempfile
import os

async def test_edge_tts():
    try:
        print("🔍 Testant Edge-TTS...")
        
        # Test 1: Llistar veus
        print("📋 Obtenint veus...")
        voices = await edge_tts.list_voices()
        print(f"✅ Trobades {len(voices)} veus")
        
        # Test 2: Síntesi simple
        print("🎵 Generant àudio...")
        text = "Hola, aquesta és una prova de síntesi de veu."
        voice_id = "es-ES-ElviraNeural"
        
        communicate = edge_tts.Communicate(text, voice_id)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        await communicate.save(temp_path)
        
        # Llegir àudio
        with open(temp_path, "rb") as f:
            audio_data = f.read()
        
        audio_base64 = base64.b64encode(audio_data).decode()
        
        # Netejar
        os.unlink(temp_path)
        
        print(f"✅ Àudio generat: {len(audio_data)} bytes")
        print(f"✅ Base64: {audio_base64[:50]}...")
        
        return {
            "success": True,
            "voices_count": len(voices),
            "audio_size": len(audio_data),
            "audio_base64": audio_base64[:100] + "..."
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(test_edge_tts())
    print(f"Resultat: {result}")







