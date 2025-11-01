# Hyperrealistic Catalan Voices – Roadmap

Aquests són els passos a seguir quan disposem de GPU i volem passar de l’engine mock actual a síntesi real:

## 1. Preparar models entrenats
- Entrenar XTTS/Coqui amb els datasets localitzats a `backend/training_data/<voice_id>/`.
- Exportar cada veu en un format d’inferència (`.pth`, `.onnx` o `.pt`) i guardar-la a `backend/voice_models/<voice_id>/` junt amb la configuració necessària (sample rate, vocoder, etc.).
- Afegir o actualitzar `metadata.json` amb camps: `model_path`, `config_path`, `sample_rate`, `speaker_reference`, `language`, `dialect`…

## 2. Substituir el motor mock
- Editar `backend/hyperrealistic_engine.py` i substituir la funció `synthesize` perquè carregui el model i generi l’àudio en temps real en lloc de retornar `processed.wav`.
- Mantenir el format de retorn (`audio_base64`, `mime_type`, `metadata`, `source`…) i conservar el fallback a Edge-TTS si l’inferència falla.

## 3. Optimitzacions per a GPU
- Afegir cache i warm-up dels models que s’usaran habitualment (exemple: `senyor_catala_1`, `dona_catalana`).  
- Afegir un endpoint de health que comprovi que les veus estan carregades (`/api/catalan/health` ja hi és, cal només ajustar-lo).  
- Documentar els requisits de GPU (memòria, drivers, versions de CUDA) i, si cal, limitar el nombre d’inferències concurrent per evitar saturació.

## 4. Validació i UI
- Generar mostres noves amb el motor neuronal i comparar-les amb les gravacions originals per garantir la qualitat.  
- Actualitzar la fitxa de cada veu a la UI (`CatalanHyperrealistic.jsx`) per indicar quan el motor és “neural” (el badge `mock` deixarà d’aparèixer).  
- Rehabilitar la pestanya “Veus Hiperrealistes” al `Layout.jsx` quan tot estigui llest i es vulgui fer públic.

## 5. Documentació i manteniment
- Afegir aquests passos al README i al dossier d’onboarding de VeuPlus.  
- Mantenir `backend/voice_inventory.json` actualitzat (executant `python backend/tools/generate_voice_inventory.py`).  
- Crear scripts de regressió que provin la síntesi per text abans de desplegar a producció.

