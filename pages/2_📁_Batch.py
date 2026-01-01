"""
Página de procesamiento batch de múltiples archivos
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
import time
import json
import zipfile
from io import BytesIO

from src.transcriber import Transcriber
from src.utils import format_timestamp

st.set_page_config(
    page_title="Procesamiento Batch",
    page_icon="📁",
    layout="wide"
)


def generate_srt(result):
    """Genera contenido SRT."""
    srt_lines = []
    chunks = result.get('chunks', [])
    
    if not chunks:
        return ""
    
    for i, chunk in enumerate(chunks, start=1):
        if 'timestamp' not in chunk or not chunk['timestamp']:
            continue
        start_time = format_timestamp(chunk['timestamp'][0])
        end_time = format_timestamp(chunk['timestamp'][1])
        text = chunk['text'].strip()
        srt_lines.extend([f"{i}", f"{start_time} --> {end_time}", text, ""])
    
    return "\n".join(srt_lines)


def generate_vtt(result):
    """Genera contenido VTT."""
    vtt_lines = ["WEBVTT", ""]
    chunks = result.get('chunks', [])
    
    if not chunks:
        return "WEBVTT\n"
    
    for chunk in chunks:
        if 'timestamp' not in chunk or not chunk['timestamp']:
            continue
        start_time = format_timestamp(chunk['timestamp'][0])
        end_time = format_timestamp(chunk['timestamp'][1])
        text = chunk['text'].strip()
        vtt_lines.extend([f"{start_time} --> {end_time}", text, ""])
    
    return "\n".join(vtt_lines)


def main():
    st.title("📁 Procesamiento Batch")
    st.markdown("Transcribe múltiples archivos de audio automáticamente")
    st.markdown("---")
    
    # Upload múltiple
    uploaded_files = st.file_uploader(
        "Selecciona uno o más archivos de audio",
        type=['mp3', 'm4a', 'wav', 'flac', 'ogg', 'opus', 'webm'],
        accept_multiple_files=True,
        help="Puedes seleccionar múltiples archivos para procesarlos en batch"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} archivo(s) cargado(s)")
        
        # Mostrar lista de archivos
        with st.expander(f"📋 Ver archivos ({len(uploaded_files)})"):
            for idx, file in enumerate(uploaded_files, 1):
                size_mb = file.size / 1024 / 1024
                st.text(f"{idx}. {file.name} ({size_mb:.2f} MB)")
    else:
        st.info("👆 Sube uno o más archivos de audio para procesamiento batch")
        st.stop()
    
    # Configuración
    st.markdown("---")
    st.subheader("⚙️ Configuración de Batch")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        model = st.selectbox(
            "🤖 Modelo Whisper",
            ['tiny', 'base', 'small', 'medium', 'turbo', 'large'],
            index=2,  # small por defecto para batch
            help="Para batch se recomienda usar 'small' o 'medium' para balance velocidad/calidad"
        )
    
    with col2:
        language_options = {
            'Auto-detección': None,
            'Español': 'spanish',
            'Inglés': 'english',
            'Francés': 'french',
            'Alemán': 'german',
            'Italiano': 'italian',
            'Portugués': 'portuguese',
        }
        
        language_display = st.selectbox(
            "🌍 Idioma",
            list(language_options.keys()),
            index=0
        )
        language = language_options[language_display]
    
    with col3:
        task = st.selectbox(
            "📋 Tarea",
            ['transcribe', 'translate'],
            help="transcribe: idioma original | translate: traduce a inglés"
        )
    
    # Opciones avanzadas
    with st.expander("🔧 Opciones Avanzadas"):
        col1, col2 = st.columns(2)
        
        with col1:
            batch_size = st.slider(
                "Batch Size",
                min_value=1,
                max_value=16,
                value=4,
                help="Valor más bajo = más estable para procesamiento largo"
            )
            
            include_timestamps = st.checkbox(
                "Incluir timestamps",
                value=True
            )
        
        with col2:
            formats = st.multiselect(
                "📦 Formatos de exportación",
                ['txt', 'json', 'srt', 'vtt'],
                default=['txt'],
                help="Todos los archivos se exportarán en estos formatos"
            )
            
            continue_on_error = st.checkbox(
                "Continuar si hay errores",
                value=True,
                help="Si está activado, un error en un archivo no detendrá el proceso"
            )
    
    # Botón de procesamiento
    st.markdown("---")
    
    if st.button("🚀 Iniciar Procesamiento Batch", type="primary", use_container_width=True):
        
        if not formats:
            st.error("❌ Selecciona al menos un formato de exportación")
            return
        
        # Inicializar
        total_files = len(uploaded_files)
        results = []
        temp_files = []
        
        # Contenedores para progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Crear transcriptor
            status_text.text("🔄 Inicializando modelo...")
            transcriber = Transcriber(
                model_name=model,
                language=language,
                batch_size=batch_size
            )
            
            status_text.text(f"📥 Cargando modelo {model}...")
            transcriber.load_model()
            st.success(f"✅ Modelo {model} cargado")
            
            # Procesar cada archivo
            for idx, uploaded_file in enumerate(uploaded_files, 1):
                status_text.text(f"📄 Procesando {idx}/{total_files}: {uploaded_file.name}")
                progress_bar.progress(idx / (total_files + 1))
                
                # Guardar temporalmente
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                    temp_files.append(tmp_path)
                
                try:
                    # Transcribir
                    start_time = time.time()
                    result = transcriber.transcribe(
                        tmp_path,
                        return_timestamps=include_timestamps,
                        task=task
                    )
                    processing_time = time.time() - start_time
                    
                    # Guardar resultado
                    results.append({
                        'filename': uploaded_file.name,
                        'result': result,
                        'processing_time': processing_time,
                        'success': True,
                        'error': None
                    })
                    
                except Exception as e:
                    error_msg = str(e)
                    results.append({
                        'filename': uploaded_file.name,
                        'result': None,
                        'processing_time': 0,
                        'success': False,
                        'error': error_msg
                    })
                    
                    if not continue_on_error:
                        st.error(f"❌ Error en {uploaded_file.name}: {error_msg}")
                        break
            
            progress_bar.progress(1.0)
            status_text.text("🧹 Finalizando...")
            
            # Liberar modelo
            transcriber.unload_model()
            
            # Mostrar resultados
            st.markdown("---")
            st.subheader("📊 Resultados del Procesamiento")
            
            successful = sum(1 for r in results if r['success'])
            failed = sum(1 for r in results if not r['success'])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ Exitosos", successful)
            col2.metric("❌ Fallidos", failed)
            col3.metric("📁 Total", len(results))
            
            # Tabla de resultados
            st.markdown("### 📋 Detalles")
            
            for idx, res in enumerate(results, 1):
                with st.expander(f"{'✅' if res['success'] else '❌'} {idx}. {res['filename']}"):
                    if res['success']:
                        st.success(f"Procesado en {res['processing_time']:.2f}s")
                        
                        result_data = res['result']
                        text = result_data.get('text', '')
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Caracteres", len(text))
                        col2.metric("Palabras", len(text.split()))
                        col3.metric("Segmentos", len(result_data.get('chunks', [])))
                        
                        # Preview del texto
                        preview = text[:500] + "..." if len(text) > 500 else text
                        st.text_area(f"Preview", preview, height=100, key=f"preview_{idx}")
                        
                    else:
                        st.error(f"Error: {res['error']}")
            
            # Generar archivos para descarga
            st.markdown("---")
            st.subheader("⬇️ Descargar Resultados")
            
            if successful > 0:
                # Crear ZIP con todos los resultados
                zip_buffer = BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for res in results:
                        if not res['success']:
                            continue
                        
                        base_name = Path(res['filename']).stem
                        result_data = res['result']
                        text = result_data.get('text', '')
                        
                        # TXT
                        if 'txt' in formats:
                            zip_file.writestr(f"{base_name}.txt", text)
                        
                        # JSON
                        if 'json' in formats:
                            json_content = json.dumps(result_data, ensure_ascii=False, indent=2)
                            zip_file.writestr(f"{base_name}.json", json_content)
                        
                        # SRT
                        if 'srt' in formats and include_timestamps:
                            srt_content = generate_srt(result_data)
                            if srt_content:
                                zip_file.writestr(f"{base_name}.srt", srt_content)
                        
                        # VTT
                        if 'vtt' in formats and include_timestamps:
                            vtt_content = generate_vtt(result_data)
                            if vtt_content:
                                zip_file.writestr(f"{base_name}.vtt", vtt_content)
                
                zip_buffer.seek(0)
                
                st.download_button(
                    label=f"📦 Descargar ZIP con {successful} transcripción/es",
                    data=zip_buffer.getvalue(),
                    file_name="transcripciones_batch.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )
                
                st.success(f"✅ Procesamiento completado: {successful}/{total_files} archivos transcritos correctamente")
            else:
                st.error("❌ No hay resultados exitosos para descargar")
            
        except Exception as e:
            st.error(f"❌ Error durante el procesamiento batch")
            st.exception(e)
        
        finally:
            # Limpiar archivos temporales
            status_text.empty()
            for tmp_file in temp_files:
                if os.path.exists(tmp_file):
                    os.unlink(tmp_file)


if __name__ == "__main__":
    main()

