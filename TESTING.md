# Guía de Pruebas - jorge-transcript

## ✅ Implementación Completada

Todos los componentes principales han sido implementados:

1. ✅ **src/transcriber.py** - Clase Transcriber con lógica completa de transcripción
2. ✅ **src/utils.py** - Funciones de validación, formateo y exportación
3. ✅ **main.py** - Interfaz CLI completa con múltiples opciones
4. ✅ **scripts/check_gpu.py** - Verificación de GPU/CUDA
5. ✅ **README.md** - Documentación completa
6. ✅ **run_examples.sh** - Script de ayuda con ejemplos

## 🧪 Pasos para Probar con tu Archivo de Audio

### Paso 1: Verificar que todo esté listo

```bash
# Activar entorno virtual
source .venv/bin/activate

# Verificar GPU
python scripts/check_gpu.py

# O usar el script de ayuda
./run_examples.sh gpu
```

### Paso 2: Colocar tu archivo de audio

```bash
# Opción A: Copiarlo al directorio input/
cp /ruta/a/tu/audio.mp3 ./input/

# Opción B: Usar directamente desde su ubicación
# (puedes especificar cualquier ruta en --input)
```

### Paso 3: Primera transcripción de prueba (modelo pequeño)

Para una prueba rápida, usa el modelo `small`:

```bash
python main.py --input ./input/tu_audio.mp3 --model small
```

Esto:
- Descargará el modelo small (~500 MB) la primera vez
- Procesará el audio con `batch_size=8` (valor optimizado)
- Guardará el resultado en `./output/tu_audio.txt`
- Mostrará estadísticas de procesamiento

**Nota sobre memoria**: Si tu archivo de audio es muy largo y recibes un error de memoria, reduce el `batch_size`:

```bash
python main.py --input ./input/tu_audio.mp3 --model small --batch-size 4
```

### Paso 4: Transcripción con mejor calidad

Una vez verificado que funciona, usa el modelo `medium` o `turbo`:

```bash
# Modelo medium (recomendado)
python main.py --input ./input/tu_audio.mp3 --model medium

# Modelo turbo (más rápido, excelente calidad)
python main.py --input ./input/tu_audio.mp3 --model turbo
```

### Paso 5: Generar subtítulos

Si necesitas subtítulos para un video:

```bash
python main.py --input ./input/tu_audio.mp3 --format srt --model medium
```

Esto generará `./output/tu_audio.srt` que puedes usar con cualquier reproductor de video.

### Paso 6: Exportar en múltiples formatos

```bash
python main.py --input ./input/tu_audio.mp3 --format txt json srt vtt --model medium
```

Esto creará:
- `tu_audio.txt` - Texto plano
- `tu_audio.json` - JSON con timestamps y metadatos
- `tu_audio.srt` - Subtítulos SRT
- `tu_audio.vtt` - Subtítulos WebVTT

## 📊 Qué Esperar

### Primera Ejecución
- **Descarga del modelo**: 1-5 minutos (solo la primera vez)
- **Carga en GPU**: 10-30 segundos
- **Transcripción**: 10-20x tiempo real
  - Audio de 1 minuto → ~3-6 segundos
  - Audio de 10 minutos → ~30-60 segundos
  - Audio de 1 hora → ~3-6 minutos

### Ejecuciones Siguientes
- Sin descarga de modelo
- Carga en GPU: 10-30 segundos
- Misma velocidad de transcripción

## 🎯 Casos de Prueba Recomendados

### Test 1: Audio Corto (< 5 minutos)
```bash
python main.py --input audio_corto.mp3 --model small
```
**Objetivo**: Verificar funcionamiento básico rápidamente

### Test 2: Audio Medio (5-30 minutos)
```bash
python main.py --input audio_medio.mp3 --model medium --format txt json
```
**Objetivo**: Probar calidad y rendimiento con modelo recomendado

### Test 3: Audio Largo (> 30 minutos)
```bash
python main.py --input audio_largo.mp3 --model turbo --format txt srt
```
**Objetivo**: Probar rendimiento en archivos grandes

### Test 4: Batch Processing
```bash
# Colocar varios archivos en ./input/
python main.py --input-dir ./input --output-dir ./output --model medium
```
**Objetivo**: Procesar múltiples archivos automáticamente

## 🔍 Información del Output

Durante la transcripción verás:

```
======================================================================
TRANSCRIPTOR DE AUDIO - WHISPER + GPU
======================================================================
Transcriptor inicializado:
  Dispositivo: cuda
  Modelo: medium
  Idioma: spanish
  Batch size: 24
  Flash Attention: False

Cargando modelo 'medium'...
(La primera vez descargará el modelo, puede tardar varios minutos)

✓ Modelo cargado en GPU: NVIDIA GeForce RTX 4080 Laptop GPU
  Memoria GPU usada: 4.23 GB

Transcribiendo: tu_audio.mp3
✓ Transcripción completada en 25.45s

======================================================================
Archivo: tu_audio.mp3
Tiempo de procesamiento: 25.45s
Caracteres transcritos: 15432
Palabras aproximadas: 2456
Segmentos: 147
Duración del audio: 10m 15s
Velocidad: 24.2x tiempo real
======================================================================

Exportando transcripción...
✓ Transcripción guardada: ./output/tu_audio.txt

✓ Transcripción finalizada
```

## 🐛 Troubleshooting Durante Pruebas

### Si el modelo no se descarga
```bash
# Verificar conexión a internet y acceso a Hugging Face
# Los modelos se descargan de: https://huggingface.co/openai/

# Ver caché de modelos descargados
ls ~/.cache/huggingface/hub/
```

### Si hay error de memoria GPU (IMPORTANTE)

**Error**: `torch.OutOfMemoryError: CUDA out of memory`

Este es el error más común al transcribir archivos largos. **Soluciones**:

```bash
# 1. Reducir batch_size (PRIMERA OPCIÓN)
python main.py --input audio.mp3 --model medium --batch-size 4
python main.py --input audio.mp3 --model medium --batch-size 2
python main.py --input audio.mp3 --model medium --batch-size 1  # Más lento pero seguro

# 2. Usar modelo más pequeño
python main.py --input audio.mp3 --model small

# 3. Limpiar memoria GPU y reintentar
python -c "import torch; torch.cuda.empty_cache()"
python main.py --input audio.mp3 --model medium --batch-size 4

# 4. Usar variable de entorno
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True python main.py --input audio.mp3
```

**Guía rápida de batch_size**:
- Audio corto (< 5 min): `--batch-size 8` (default)
- Audio medio (5-30 min): `--batch-size 4-8`
- Audio largo (> 30 min): `--batch-size 2-4`
- Audio muy largo (> 1 hora) con modelo large: `--batch-size 1`

### Si la transcripción está en idioma incorrecto
```bash
# Especificar idioma explícitamente
python main.py --input audio.mp3 --language spanish
python main.py --input audio.mp3 --language english
```

### Si necesitas ver más detalles
```bash
# Modo verbose (cuando se implemente)
python main.py --input audio.mp3 --verbose
```

## 📈 Métricas de Rendimiento

Anota estas métricas durante tus pruebas:

- ✓ Tiempo de descarga del modelo: _____ minutos (solo primera vez)
- ✓ Tiempo de carga en GPU: _____ segundos
- ✓ Duración del audio: _____ minutos
- ✓ Tiempo de transcripción: _____ segundos
- ✓ Factor de velocidad (audio/tiempo): _____x tiempo real
- ✓ Memoria GPU usada: _____ GB
- ✓ Calidad de transcripción: _____ (subjetivo 1-10)

## ✨ Características Implementadas

| Característica | Estado | Comando |
|---------------|--------|---------|
| Transcripción individual | ✅ | `--input file.mp3` |
| Transcripción batch | ✅ | `--input-dir ./input` |
| Múltiples modelos | ✅ | `--model tiny/base/small/medium/large/turbo` |
| Múltiples idiomas | ✅ | `--language spanish/english/etc` |
| Exportación TXT | ✅ | `--format txt` |
| Exportación JSON | ✅ | `--format json` |
| Exportación SRT | ✅ | `--format srt` |
| Exportación VTT | ✅ | `--format vtt` |
| Timestamps | ✅ | Por defecto (usar `--no-timestamps` para desactivar) |
| Traducción a inglés | ✅ | `--task translate` |
| Info GPU | ✅ | `--gpu-info` |
| Lista de modelos | ✅ | `--list-models` |
| Aceleración GPU | ✅ | Automático si CUDA disponible |
| Soporte CPU | ✅ | `--device cpu` |

## 🎓 Tips para Mejores Resultados

1. **Calidad del audio**: Audio claro y sin mucho ruido de fondo da mejores resultados
2. **Elección del modelo**: 
   - `small`: Pruebas rápidas
   - `medium`: Mejor balance (recomendado)
   - `turbo`: Más rápido que medium, calidad similar
   - `large`: Máxima calidad, más lento
3. **Idioma**: Especifica el idioma correcto con `--language` para mejor precisión
4. **Formato**: Usa `json` si necesitas timestamps precisos y metadatos

## 📞 Siguiente Paso

**Sube tu archivo de audio** y ejecuta:

```bash
python main.py --input tu_archivo.mp3 --model small
```

¡Y verás la transcripción en acción! 🚀

