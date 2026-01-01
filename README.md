# jorge-transcript

Aplicación de transcripción de audio usando Whisper con aceleración GPU (NVIDIA).

## 🎯 Características

- ✅ Transcripción de audio con modelos Whisper de OpenAI
- ✅ Aceleración por GPU (NVIDIA CUDA)
- ✅ **Interfaz Web (Streamlit) y CLI**
- ✅ Soporte para múltiples formatos de audio (mp3, m4a, wav, flac, ogg, opus, webm)
- ✅ Exportación en varios formatos (txt, json, srt, vtt)
- ✅ Procesamiento batch de múltiples archivos
- ✅ Auto-detección de idioma
- ✅ Timestamps automáticos para generación de subtítulos

## 📋 Requisitos del Sistema

### Hardware
- **GPU**: NVIDIA GeForce RTX 4080 (o compatible con CUDA)
- **VRAM**: Mínimo 8GB recomendado (modelos grandes requieren más)
- **RAM**: 16GB recomendado

### Software
- **SO**: Linux (Ubuntu 22.04 o superior)
- **Python**: >= 3.12
- **CUDA**: >= 11.8 (detectado: 12.2)
- **Drivers NVIDIA**: >= 535.xx
- **FFmpeg**: >= 4.x (para procesamiento de audio)

## ✅ Estado de la Instalación

```
✓ PyTorch 2.5.1 con CUDA 12.1 instalado
✓ GPU detectada: NVIDIA GeForce RTX 4080 Laptop GPU
✓ Memoria GPU disponible: 11.73 GB
✓ CUDA funcionando correctamente
✓ cuDNN habilitado (versión 90100)
✓ FFmpeg instalado (versión 4.4.2)
✓ Aplicación implementada y funcional
```

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/jorge-transcript.git
cd jorge-transcript
```

### 2. Crear entorno virtual con uv
```bash
uv venv
source .venv/bin/activate
```

### 3. Instalar PyTorch con CUDA
```bash
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 4. Instalar dependencias del proyecto
```bash
uv pip install -e .
```

### 5. Verificar GPU
```bash
python scripts/check_gpu.py
```

Deberías ver un mensaje confirmando que la GPU está disponible y funcionando.

## 📖 Uso

### 🌐 Interfaz Web (Recomendado)

La forma más fácil de usar la aplicación es a través de la interfaz web:

```bash
# Activar entorno virtual
source .venv/bin/activate

# Iniciar la aplicación web
streamlit run streamlit_app.py
```

Se abrirá automáticamente en tu navegador (`http://localhost:8501`).

**Características de la interfaz web:**
- 🎤 Upload de archivos drag & drop
- 📊 Monitoreo de GPU en tiempo real
- 📁 Procesamiento batch con descarga en ZIP
- ⚙️ Configuración visual de parámetros
- 📥 Descarga en múltiples formatos simultáneos

Ver [STREAMLIT.md](STREAMLIT.md) para más detalles.

---

### 💻 Interfaz CLI (Línea de Comandos)

### 🌍 Auto-Detección de Idioma (Nuevo)

**Por defecto, la aplicación detecta automáticamente el idioma del audio**. No necesitas especificar `--language` a menos que:
- La auto-detección falle o detecte incorrectamente
- Quieras forzar un idioma específico
- El audio contiene múltiples idiomas mezclados

```bash
# Auto-detección (RECOMENDADO) - detecta inglés, español, francés, etc.
python main.py --input audio.mp3

# Forzar idioma solo si necesario
python main.py --input audio.mp3 --language english
```

### Comandos Informativos

```bash
# Ver ayuda completa
python main.py --help

# Listar modelos disponibles
python main.py --list-models

# Ver información de GPU
python main.py --gpu-info
```

### Transcripción Básica

```bash
# Transcribir un archivo (auto-detección de idioma)
python main.py --input audio.mp3

# Especificar archivo de salida
python main.py --input audio.mp3 --output transcripcion.txt

# Forzar idioma específico si la auto-detección no funciona bien
python main.py --input audio_ingles.mp3 --language english
python main.py --input audio_espanol.mp3 --language spanish

# Transcribir con modelo específico
python main.py --input audio.m4a --model large
```

### Traducción

```bash
# Transcribir Y traducir a inglés (cualquier idioma → inglés)
python main.py --input audio_espanol.mp3 --task translate

# Esto funciona con audio en cualquier idioma y lo traduce a inglés
python main.py --input audio_frances.mp3 --task translate --model medium
```

**Nota**: La opción `--task translate` de Whisper **solo traduce a inglés**. Si necesitas traducción a otros idiomas, primero transcribe y luego usa una herramienta de traducción externa.

### Procesamiento Batch

```bash
# Transcribir todos los archivos en un directorio
python main.py --input-dir ./input --output-dir ./output

# Procesar con modelo específico
python main.py --input-dir ./input --model medium --output-dir ./output
```

### Formatos de Salida

```bash
# Exportar como subtítulos SRT
python main.py --input audio.mp3 --format srt

# Exportar en múltiples formatos
python main.py --input audio.mp3 --format txt json srt vtt

# Solo JSON (con timestamps y metadatos)
python main.py --input audio.mp3 --format json
```

### Traducción a Inglés

```bash
# Transcribir y traducir a inglés
python main.py --input audio_espanol.mp3 --task translate
```

### Opciones Avanzadas

```bash
# Usar CPU en lugar de GPU
python main.py --input audio.mp3 --device cpu

# Ajustar batch size para controlar uso de memoria GPU
python main.py --input audio.mp3 --batch-size 4

# Usar precisión float32 (más preciso pero más lento y más memoria)
python main.py --input audio.mp3 --compute-type float32

# Sin timestamps (solo texto)
python main.py --input audio.mp3 --no-timestamps
```

## ⚙️ Optimización de Memoria GPU: Parámetro batch_size

El parámetro `--batch-size` es **crítico** para controlar el uso de memoria GPU durante la transcripción. 

### ¿Qué es el batch_size?

El `batch_size` determina cuántos fragmentos de audio se procesan simultáneamente en la GPU. Un valor más alto es más rápido pero consume más VRAM, mientras que un valor más bajo es más lento pero más seguro en memoria.

### Configuración por Defecto

```bash
# Valor por defecto optimizado para RTX 4080
--batch-size 8  # Balance entre velocidad y memoria
```

### Cómo Ajustar el batch_size

#### Síntomas de batch_size Demasiado Alto

Si recibes un error como:
```
torch.OutOfMemoryError: CUDA out of memory
```

**Solución**: Reduce el `batch_size` a la mitad:

```bash
# Probar con valores más bajos progresivamente
python main.py --input audio.mp3 --batch-size 4
python main.py --input audio.mp3 --batch-size 2
python main.py --input audio.mp3 --batch-size 1  # Más lento pero más seguro
```

#### Guía de batch_size por Modelo y VRAM

| Modelo | VRAM Total | batch_size Recomendado | VRAM Usada |
|--------|-----------|------------------------|------------|
| tiny   | 2-4 GB    | 32                     | ~1 GB      |
| base   | 2-4 GB    | 24                     | ~1.5 GB    |
| small  | 4-6 GB    | 16                     | ~2.5 GB    |
| medium | 6-8 GB    | 8                      | ~5 GB      |
| medium | 8-12 GB   | 12-16                  | ~6-7 GB    |
| turbo  | 8-12 GB   | 8-12                   | ~6 GB      |
| large  | 10-12 GB  | 4-8                    | ~9-10 GB   |
| large  | 12+ GB    | 8-12                   | ~10-11 GB  |

#### Para tu RTX 4080 (11.73 GB VRAM)

```bash
# Configuraciones optimizadas para tu GPU
# Modelo small - máximo rendimiento
python main.py --input audio.mp3 --model small --batch-size 16

# Modelo medium - recomendado (default)
python main.py --input audio.mp3 --model medium --batch-size 8

# Modelo turbo - excelente calidad
python main.py --input audio.mp3 --model turbo --batch-size 8

# Modelo large - máxima calidad
python main.py --input audio.mp3 --model large --batch-size 4
```

### Variables de Entorno Adicionales

Si experimentas fragmentación de memoria, usa:

```bash
# Configurar antes de ejecutar
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Luego ejecutar normalmente
python main.py --input audio.mp3 --model medium
```

### Monitoreo de Memoria GPU

```bash
# Ver uso de GPU en tiempo real (en otra terminal)
watch -n 1 nvidia-smi

# O verificar memoria antes de ejecutar
python main.py --gpu-info
```

## 📁 Estructura del Proyecto

```
jorge_transcript/
├── main.py                    # Punto de entrada de la aplicación
├── pyproject.toml             # Configuración y dependencias
├── README.md                  # Este archivo
├── src/                       # Código fuente
│   ├── __init__.py
│   ├── transcriber.py        # Clase principal de transcripción
│   └── utils.py              # Funciones de validación y exportación
├── scripts/
│   └── check_gpu.py          # Script de verificación GPU
├── input/                     # Directorio para archivos de entrada
├── output/                    # Directorio para transcripciones
└── tests/                     # Archivos de prueba
```

## 🎵 Formatos de Audio Soportados

- **MP3** (.mp3)
- **M4A** (.m4a)
- **WAV** (.wav)
- **FLAC** (.flac)
- **OGG** (.ogg)
- **Opus** (.opus)
- **WebM** (.webm)

## 🤖 Modelos Whisper Disponibles

| Modelo | Parámetros | VRAM Requerida | batch_size | Velocidad | Precisión | Recomendado para |
|--------|-----------|----------------|------------|-----------|-----------|------------------|
| tiny   | 39M       | ~1 GB          | 32         | Muy rápida | Básica   | Pruebas rápidas |
| base   | 74M       | ~1 GB          | 24         | Rápida     | Buena    | Audio claro |
| small  | 244M      | ~2 GB          | 16         | Media      | Muy buena| Uso general |
| medium | 769M      | ~5 GB          | 8          | Lenta      | Excelente| **Recomendado (RTX 4080)** |
| turbo  | 809M      | ~6 GB          | 8          | Media      | Excelente| Balance óptimo |
| large  | 1550M     | ~10 GB         | 4          | Muy lenta  | Superior | Máxima calidad |

**Para RTX 4080 (11.73 GB VRAM)**: Se recomienda usar `medium` o `turbo` con `batch_size=8`, o `large` con `batch_size=4`.

## 📊 Rendimiento Esperado

Con la GPU RTX 4080:
- **Velocidad**: 10-20x tiempo real (dependiendo del modelo)
- **Ejemplo**: Un audio de 10 minutos → 30-60 segundos de procesamiento
- **Modelo recomendado**: `medium` para balance calidad/velocidad

## 📝 Formatos de Exportación

### TXT (Texto plano)
```
Transcripción completa del audio en texto plano...
```

### JSON (Con metadatos y timestamps)
```json
{
  "text": "Transcripción completa...",
  "chunks": [
    {
      "timestamp": [0.0, 5.2],
      "text": "Primer segmento"
    }
  ],
  "metadata": {
    "model": "medium",
    "language": "spanish",
    "processing_time": 45.2
  }
}
```

### SRT (Subtítulos)
```
1
00:00:00.000 --> 00:00:05.200
Primer segmento de la transcripción

2
00:00:05.200 --> 00:00:10.500
Segundo segmento
```

### VTT (WebVTT)
```
WEBVTT

00:00:00.000 --> 00:00:05.200
Primer segmento de la transcripción

00:00:05.200 --> 00:00:10.500
Segundo segmento
```

## 🔧 Troubleshooting

### CUDA no disponible

```bash
# Verificar drivers NVIDIA
nvidia-smi

# Reinstalar PyTorch con CUDA
uv pip uninstall torch torchvision torchaudio
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verificar instalación
python scripts/check_gpu.py
```

### Error de memoria GPU (Out of Memory)

**Síntoma**: `torch.cuda.OutOfMemoryError: CUDA out of memory`

**Causas**: El modelo y el `batch_size` están consumiendo más VRAM de la disponible.

**Soluciones** (en orden de preferencia):

1. **Reducir batch_size** (más rápido):
   ```bash
   # Reducir a la mitad del valor actual
   python main.py --input audio.mp3 --batch-size 4
   
   # Si persiste, reducir más
   python main.py --input audio.mp3 --batch-size 2
   python main.py --input audio.mp3 --batch-size 1
   ```

2. **Usar un modelo más pequeño**:
   ```bash
   # Modelo small (solo ~2 GB VRAM)
   python main.py --input audio.mp3 --model small
   
   # Modelo turbo (balance óptimo)
   python main.py --input audio.mp3 --model turbo --batch-size 8
   ```

3. **Cerrar otras aplicaciones** que usen GPU:
   ```bash
   # Ver qué está usando la GPU
   nvidia-smi
   
   # Cerrar navegadores, otros procesos de Python, etc.
   ```

4. **Limpiar caché de GPU**:
   ```bash
   python -c "import torch; torch.cuda.empty_cache()"
   ```

5. **Usar fragmentación expandible**:
   ```bash
   PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True python main.py --input audio.mp3
   ```

6. **Como último recurso, usar CPU** (mucho más lento):
   ```bash
   python main.py --input audio.mp3 --device cpu
   ```

### FFmpeg no encuentra el archivo

- Verificar que el path del archivo es correcto (usar paths absolutos si es necesario)
- Verificar que el formato de audio está soportado
- Verificar que FFmpeg está instalado: `ffmpeg -version`

### Modelo tarda mucho en descargar

La primera vez que uses un modelo, se descargará desde Hugging Face. Los modelos se guardan en `~/.cache/huggingface/hub/` y no necesitan descargarse nuevamente.

Tamaños aproximados:
- tiny/base: ~150 MB
- small: ~500 MB
- medium: ~1.5 GB
- large: ~3 GB

### Error al importar módulos

Asegúrate de que el entorno virtual está activado:
```bash
source .venv/bin/activate
```

## 🧪 Ejemplos de Flujo de Trabajo

### Workflow 1: Transcripción Simple
```bash
# 1. Colocar archivos de audio en ./input/
cp mi_audio.mp3 ./input/

# 2. Transcribir
python main.py --input ./input/mi_audio.mp3

# 3. El resultado estará en ./output/mi_audio.txt
```

### Workflow 2: Procesamiento Batch
```bash
# 1. Colocar múltiples archivos en ./input/
# 2. Procesar todos
python main.py --input-dir ./input --format txt json srt

# 3. Todos los resultados estarán en ./output/
```

### Workflow 3: Subtítulos para Video
```bash
# Transcribir y generar SRT
python main.py --input video_audio.mp3 --format srt --model medium

# El archivo .srt puede usarse con cualquier reproductor de video
```

## 🤝 Contribuciones

Este es un proyecto personal, pero las sugerencias y mejoras son bienvenidas.

## 📄 Licencia

Proyecto personal para transcripción de audio.

## 🙏 Agradecimientos

- **OpenAI Whisper**: Modelo de transcripción de audio
- **Hugging Face**: Librería Transformers
- **insanely-fast-whisper**: Optimizaciones para GPU

---

**Desarrollado con 🎯 para análisis de audio con GPU**
