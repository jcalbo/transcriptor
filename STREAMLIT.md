# 🎙️ Jorge Transcript - Interfaz Web (Streamlit)

## 🚀 Inicio Rápido

### Iniciar la Aplicación Web

```bash
# Activar entorno virtual
source .venv/bin/activate

# Iniciar Streamlit
streamlit run streamlit_app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📱 Características de la Interfaz Web

### Página Principal
- Dashboard con información del sistema
- Estado de GPU en tiempo real
- Navegación a las diferentes funcionalidades

### 🎤 Transcripción Individual
- Upload de archivos de audio (drag & drop)
- Selección de modelo y configuración
- Preview del resultado en tiempo real
- Descarga en múltiples formatos
- Métricas de rendimiento

### 📁 Procesamiento Batch
- Upload múltiple de archivos
- Procesamiento automático secuencial
- Barra de progreso por archivo
- Tabla de resultados
- Descarga de ZIP con todos los resultados

### ⚙️ Configuración
- Información detallada de GPU
- Estadísticas de modelos descargados
- Guía de optimización
- Troubleshooting
- Enlaces a documentación

## 🎨 Personalización

### Tema

Edita `.streamlit/config.toml` para cambiar colores y apariencia:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Puerto

Para cambiar el puerto por defecto (8501):

```bash
streamlit run streamlit_app.py --server.port 8502
```

## 🔧 Opciones de Ejecución

```bash
# Modo desarrollo (con hot-reload)
streamlit run streamlit_app.py

# Modo producción (sin recargar automáticamente)
streamlit run streamlit_app.py --server.fileWatcherType none

# Cambiar puerto
streamlit run streamlit_app.py --server.port 8080

# Modo headless (para servidores)
streamlit run streamlit_app.py --server.headless true
```

## 📊 Requisitos Específicos de Streamlit

Las dependencias de Streamlit se instalan automáticamente con:

```bash
uv pip install -e .
```

Incluye:
- `streamlit>=1.30.0`
- `watchdog>=3.0.0`

## 🌐 Despliegue

### Streamlit Cloud (Recomendado)

1. Push del código a GitHub
2. Conecta tu repo en [streamlit.io/cloud](https://streamlit.io/cloud)
3. Configura las variables de entorno si es necesario
4. Deploy automático

### Docker

```dockerfile
FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py"]
```

### Servidor Local (con GPU)

```bash
# Asegúrate de tener CUDA y drivers instalados
# Ejecuta en segundo plano
nohup streamlit run streamlit_app.py > streamlit.log 2>&1 &
```

## 🔒 Seguridad

Para producción, considera:

1. **Autenticación**: Usar Streamlit Cloud o agregar autenticación custom
2. **Rate Limiting**: Limitar transcripciones por usuario/IP
3. **Tamaño de archivo**: Limitar uploads (configurado en Streamlit)
4. **HTTPS**: Usar certificados SSL en producción

## 🐛 Troubleshooting

### "Address already in use"

```bash
# Encuentra el proceso en el puerto 8501
lsof -i :8501

# Mata el proceso
kill -9 <PID>

# O usa otro puerto
streamlit run streamlit_app.py --server.port 8502
```

### Errores de importación

```bash
# Reinstalar dependencias
source .venv/bin/activate
uv pip install -e .
```

### GPU no detectada

Verifica que PyTorch esté instalado con CUDA:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## 📚 Documentación de Streamlit

- [Documentación oficial](https://docs.streamlit.io/)
- [API Reference](https://docs.streamlit.io/library/api-reference)
- [Galería de apps](https://streamlit.io/gallery)

## 🆕 Versión 0.2.0

**Nuevas características:**
- ✅ Interfaz web completa con Streamlit
- ✅ Upload de archivos drag & drop
- ✅ Procesamiento batch con ZIP de resultados
- ✅ Dashboard de configuración
- ✅ Monitoreo de GPU en tiempo real
- ✅ Preview de transcripciones
- ✅ Descarga en múltiples formatos simultáneos

---

**Nota**: La aplicación CLI (`main.py`) sigue disponible y completamente funcional.

