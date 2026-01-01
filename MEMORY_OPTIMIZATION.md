# Guía de Optimización de Memoria GPU

Esta guía explica cómo optimizar el uso de memoria GPU para obtener el mejor rendimiento en la transcripción de audio.

## 📊 Entendiendo el Uso de Memoria GPU

La memoria GPU se distribuye en:
- **Modelo Whisper**: Pesos del modelo (fijo según el modelo elegido)
- **Batch Processing**: Memoria temporal para procesar chunks de audio
- **Caché de Atención**: Memoria usada durante la generación de tokens
- **Overhead de PyTorch**: Memoria reservada por el sistema

## 🎯 El Parámetro batch_size

### ¿Qué Hace el batch_size?

El `batch_size` determina cuántos fragmentos de audio (chunks) se procesan **simultáneamente** en la GPU:

- **batch_size alto** (16-32):
  - ✅ Procesamiento más rápido
  - ✅ Mejor utilización de la GPU
  - ❌ Requiere más VRAM
  - ❌ Puede causar Out of Memory

- **batch_size bajo** (1-4):
  - ✅ Menor uso de VRAM
  - ✅ Más estable para archivos largos
  - ❌ Procesamiento más lento
  - ❌ GPU subutilizada

### Valor por Defecto Optimizado

```python
batch_size = 8  # Balance óptimo para RTX 4080
```

Este valor se eligió porque:
- Funciona bien con modelos medium/turbo en una RTX 4080
- Balance entre velocidad y seguridad
- Permite procesar la mayoría de archivos sin problemas

## 📈 Tabla de Configuraciones Recomendadas

### Por Modelo (RTX 4080 - 11.73 GB VRAM)

| Modelo | VRAM Base | batch_size | VRAM Total | Audio Max | Velocidad |
|--------|-----------|------------|------------|-----------|-----------|
| tiny   | 0.5 GB    | 32         | ~2 GB      | Sin límite | Muy rápida |
| base   | 0.8 GB    | 24         | ~2.5 GB    | Sin límite | Rápida |
| small  | 1.5 GB    | 16         | ~4 GB      | > 2 horas  | Media |
| medium | 3.0 GB    | 8          | ~6 GB      | > 1 hora   | Media-Lenta |
| turbo  | 3.5 GB    | 8          | ~6.5 GB    | > 1 hora   | Media |
| large  | 6.0 GB    | 4          | ~10 GB     | ~30-60 min | Lenta |
| large  | 6.0 GB    | 2          | ~8 GB      | > 1 hora   | Muy Lenta |

### Por Duración de Audio

| Duración Audio | Modelo Recomendado | batch_size | Comando |
|----------------|-------------------|------------|---------|
| < 5 minutos    | medium/turbo      | 8-12       | `--model medium --batch-size 12` |
| 5-15 minutos   | medium/turbo      | 8          | `--model medium` (default) |
| 15-30 minutos  | medium/turbo      | 4-8        | `--model medium --batch-size 6` |
| 30-60 minutos  | medium/small      | 4          | `--model medium --batch-size 4` |
| 1-2 horas      | small/medium      | 2-4        | `--model small --batch-size 4` |
| > 2 horas      | small             | 2-4        | `--model small --batch-size 4` |

## 🔧 Proceso de Optimización

### Paso 1: Comenzar con Configuración Segura

```bash
# Primera prueba con modelo small
python main.py --input audio.mp3 --model small
```

### Paso 2: Si Funciona, Incrementar Calidad

```bash
# Probar con modelo medium (default batch_size=8)
python main.py --input audio.mp3 --model medium
```

### Paso 3: Si Falla (Out of Memory), Reducir batch_size

```bash
# Reducir a la mitad
python main.py --input audio.mp3 --model medium --batch-size 4

# Si aún falla, reducir más
python main.py --input audio.mp3 --model medium --batch-size 2
```

### Paso 4: Encontrar el Punto Óptimo

```bash
# Una vez encontrado un valor que funciona, puedes incrementar ligeramente
# Si batch_size=4 funciona, prueba con 6
python main.py --input audio.mp3 --model medium --batch-size 6
```

## 🚨 Síntomas y Soluciones

### Error: "CUDA out of memory"

**Diagnóstico**:
```
torch.OutOfMemoryError: CUDA out of memory. 
Tried to allocate XXX MiB. GPU has a total capacity of 11.73 GiB 
of which XXX MiB is free.
```

**Solución Inmediata**:
```bash
# Opción 1: Reducir batch_size (RECOMENDADO)
python main.py --input audio.mp3 --batch-size 4

# Opción 2: Modelo más pequeño
python main.py --input audio.mp3 --model small

# Opción 3: Combinar ambos
python main.py --input audio.mp3 --model small --batch-size 8
```

### Síntoma: Procesamiento Muy Lento

**Causa**: batch_size demasiado bajo o modelo en CPU

**Diagnóstico**:
```bash
# Verificar que estás usando GPU
python main.py --gpu-info

# Debería mostrar: device: cuda
```

**Solución**:
```bash
# Incrementar batch_size si hay VRAM disponible
python main.py --input audio.mp3 --batch-size 12

# O usar modelo más rápido
python main.py --input audio.mp3 --model turbo
```

### Síntoma: GPU al 100% pero Lento

**Causa**: Modelo muy grande para el batch_size

**Solución**: Incrementar batch_size progresivamente:
```bash
python main.py --input audio.mp3 --batch-size 10
python main.py --input audio.mp3 --batch-size 12
python main.py --input audio.mp3 --batch-size 16
# Continuar hasta encontrar el límite
```

## 🧪 Pruebas de Benchmark

### Script de Prueba para Encontrar Configuración Óptima

```bash
# Crear archivo test_batch.sh
cat > test_batch.sh << 'EOF'
#!/bin/bash
echo "Probando diferentes configuraciones de batch_size"
for batch in 16 12 8 4 2; do
    echo ""
    echo "=== Probando batch_size=$batch ==="
    python main.py --input input/test.mp3 --model medium --batch-size $batch
    if [ $? -eq 0 ]; then
        echo "✓ batch_size=$batch FUNCIONA"
        break
    else
        echo "✗ batch_size=$batch FALLÓ"
    fi
done
EOF

chmod +x test_batch.sh
./test_batch.sh
```

## 📝 Recomendaciones por Caso de Uso

### Caso 1: Desarrollo/Pruebas (Velocidad Prioritaria)

```bash
# Modelo pequeño, batch alto
python main.py --input audio.mp3 --model small --batch-size 16
```

### Caso 2: Producción (Balance Calidad/Velocidad)

```bash
# Modelo medium, batch óptimo
python main.py --input audio.mp3 --model medium --batch-size 8
```

### Caso 3: Máxima Calidad (Tiempo No Importante)

```bash
# Modelo large, batch conservador
python main.py --input audio.mp3 --model large --batch-size 4
```

### Caso 4: Procesamiento Batch de Muchos Archivos

```bash
# Balance para procesar múltiples archivos sin fallos
python main.py --input-dir ./input --model medium --batch-size 4
```

### Caso 5: Archivos Muy Largos (> 1 hora)

```bash
# Configuración conservadora
python main.py --input audio_largo.mp3 --model small --batch-size 4
```

## 🎓 Tips Avanzados

### 1. Monitorear Uso de GPU en Tiempo Real

```bash
# En una terminal separada
watch -n 1 nvidia-smi
```

### 2. Variable de Entorno para Fragmentación

```bash
# Agregar a ~/.bashrc o ejecutar antes del comando
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

### 3. Limpiar Memoria Entre Ejecuciones

```bash
# Limpiar caché de GPU
python -c "import torch; torch.cuda.empty_cache()"
```

### 4. Cerrar Aplicaciones que Usan GPU

```bash
# Ver qué procesos usan GPU
nvidia-smi

# Cerrar navegadores, otros procesos Python, etc.
# Esto puede liberar 1-2 GB de VRAM adicional
```

## 📊 Registro de Optimizaciones

Anota tus configuraciones exitosas:

```
Archivo: [nombre]
Duración: [minutos]
Modelo: [tiny/base/small/medium/turbo/large]
batch_size: [valor]
VRAM usada: [GB]
Tiempo procesamiento: [segundos]
Estado: [✓ Exitoso / ✗ Falló]
```

Ejemplo:
```
Archivo: entrevista_podcast.mp3
Duración: 45 minutos
Modelo: medium
batch_size: 6
VRAM usada: 7.2 GB
Tiempo procesamiento: 180s (3 min)
Estado: ✓ Exitoso
```

## 🎯 Resumen Ejecutivo

**Para RTX 4080 (11.73 GB):**

1. **Configuración por defecto** (recomendada para la mayoría de casos):
   ```bash
   python main.py --input audio.mp3 --model medium
   # batch_size=8 automático
   ```

2. **Si falla con Out of Memory**:
   ```bash
   python main.py --input audio.mp3 --model medium --batch-size 4
   ```

3. **Para máxima velocidad** (archivos cortos):
   ```bash
   python main.py --input audio.mp3 --model small --batch-size 16
   ```

4. **Para máxima calidad** (archivos no muy largos):
   ```bash
   python main.py --input audio.mp3 --model large --batch-size 4
   ```

¡Experimenta y encuentra la configuración óptima para tus archivos específicos! 🚀

