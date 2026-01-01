# Formatos de Audio Soportados

## ✅ Formatos Totalmente Soportados

Estos formatos funcionan perfectamente sin necesidad de conversión:

| Formato | Extensión | Calidad | Recomendado Para |
|---------|-----------|---------|------------------|
| **MP3** | `.mp3` | Buena | Uso general, archivos compactos |
| **WAV** | `.wav` | Excelente | Máxima calidad, archivos grandes |
| **FLAC** | `.flac` | Excelente | Audio sin pérdida, archivos medianos |
| **OGG** | `.ogg` | Buena | Alternativa a MP3, open source |
| **Opus** | `.opus` | Excelente | Optimizado para voz, archivos pequeños |
| **WebM** | `.webm` | Buena | Audio extraído de videos web |

## ⚠️ Formatos NO Soportados

### M4A (AAC)

**Extensiones**: `.m4a`, `.aac`

**Razón**: Limitaciones en la cadena de procesamiento Transformers + FFmpeg. Los archivos M4A pueden usar diferentes codecs internos (AAC, ALAC, etc.) que no siempre son compatibles con la librería de procesamiento de audio.

**Solución**: Convertir a MP3 o WAV

```bash
# Opción 1: Convertir a MP3 (recomendado)
ffmpeg -i audio.m4a -acodec libmp3lame -ar 16000 -ac 1 audio.mp3

# Opción 2: Convertir a WAV (máxima calidad)
ffmpeg -i audio.m4a -acodec pcm_s16le -ar 16000 -ac 1 audio.wav

# Opción 3: Batch conversion (múltiples archivos)
for file in *.m4a; do
    ffmpeg -i "$file" -acodec libmp3lame -ar 16000 -ac 1 "${file%.m4a}.mp3"
done
```

### WMA, RA, AMR y otros formatos propietarios

Tampoco están soportados. Conviértelos a MP3 o WAV primero.

## 🎯 Recomendaciones por Caso de Uso

### Para Transcripción General
**Formato recomendado**: MP3
- Balance perfecto entre calidad y tamaño
- Universalmente compatible
- Fácil de compartir

```bash
# Convertir cualquier formato a MP3 óptimo para Whisper
ffmpeg -i input.* -acodec libmp3lame -ar 16000 -ac 1 -b:a 128k output.mp3
```

### Para Máxima Calidad
**Formato recomendado**: FLAC o WAV
- Sin pérdida de calidad
- Mejor para audio con mucho detalle

```bash
# Convertir a FLAC
ffmpeg -i input.* -acodec flac -ar 16000 -ac 1 output.flac
```

### Para Archivos Pequeños
**Formato recomendado**: Opus
- Excelente calidad con tamaño reducido
- Optimizado específicamente para voz

```bash
# Convertir a Opus
ffmpeg -i input.* -acodec libopus -ar 16000 -ac 1 -b:a 64k output.opus
```

## 🔧 Parámetros de FFmpeg Explicados

| Parámetro | Descripción | Valor Recomendado |
|-----------|-------------|-------------------|
| `-ar` | Sample rate | `16000` (16kHz, óptimo para Whisper) |
| `-ac` | Canales de audio | `1` (mono, reduce tamaño sin perder info) |
| `-b:a` | Bitrate de audio | `128k` para MP3, `64k` para Opus |
| `-acodec` | Codec de audio | `libmp3lame`, `flac`, `libopus` |

## 📊 Comparación de Formatos

### Archivo de 10 minutos de audio de voz

| Formato | Tamaño | Calidad | Velocidad Transcripción |
|---------|--------|---------|------------------------|
| MP3 (128k) | ~10 MB | ⭐⭐⭐⭐ | Normal |
| MP3 (192k) | ~14 MB | ⭐⭐⭐⭐⭐ | Normal |
| WAV | ~96 MB | ⭐⭐⭐⭐⭐ | Normal |
| FLAC | ~48 MB | ⭐⭐⭐⭐⭐ | Normal |
| Opus (64k) | ~5 MB | ⭐⭐⭐⭐ | Normal |
| M4A | ~8 MB | ⭐⭐⭐⭐ | ❌ No funciona |

## 🐛 Troubleshooting

### Error: "Soundfile is either not in the correct format or is malformed"

**Causa**: Formato no soportado o archivo corrupto

**Soluciones**:
1. Convierte el archivo a MP3:
   ```bash
   ffmpeg -i archivo.m4a -acodec libmp3lame -ar 16000 archivo.mp3
   ```

2. Verifica que el archivo no esté corrupto:
   ```bash
   ffprobe archivo.m4a
   ```

3. Re-codifica el archivo:
   ```bash
   ffmpeg -i archivo.m4a -acodec copy archivo_temp.m4a
   ffmpeg -i archivo_temp.m4a -acodec libmp3lame archivo.mp3
   ```

### FFmpeg no está instalado

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Verificar instalación
ffmpeg -version
```

## 💡 Consejos

1. **Siempre usa mono (`-ac 1`)**: Whisper procesa en mono, así que no hay beneficio en stereo

2. **Sample rate de 16kHz es óptimo**: Whisper fue entrenado con 16kHz, usar más no mejora resultados

3. **MP3 128k es suficiente**: No necesitas bitrates más altos para transcripción de voz

4. **Guarda los originales**: Haz la conversión en copias, no sobrescribas los archivos originales

5. **Batch conversion**: Si tienes muchos archivos M4A, usa un script para convertirlos todos de una vez

## 📚 Recursos Adicionales

- [Documentación de FFmpeg](https://ffmpeg.org/documentation.html)
- [Formatos soportados por FFmpeg](https://ffmpeg.org/general.html#Audio-Codecs)
- [Whisper paper (OpenAI)](https://arxiv.org/abs/2212.04356)

---

**Última actualización**: Enero 2026  
**Versión**: 0.2.1

