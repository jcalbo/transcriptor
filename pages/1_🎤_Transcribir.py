"""
Página de transcripción individual
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
import time
import json

from src.transcriber import Transcriber
from src.utils import format_timestamp

st.set_page_config(
    page_title="Transcribir Audio",
    page_icon="🎤",
    layout="wide"
)

def generate_srt(result):
    """Genera contenido SRT a partir del resultado."""
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
        
        srt_lines.append(f"{i}")
        srt_lines.append(f"{start_time} --> {end_time}")
        srt_lines.append(text)
        srt_lines.append("")
    
    return "\n".join(srt_lines)


def generate_vtt(result):
    """Genera contenido VTT a partir del resultado."""
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
        
        vtt_lines.append(f"{start_time} --> {end_time}")
        vtt_lines.append(text)
        vtt_lines.append("")
    
    return "\n".join(vtt_lines)


def main():
    st.title("🎤 Transcripción Individual")
    st.markdown("Sube un archivo de audio para transcribirlo a texto")
    st.markdown("---")
    
    # Columnas para upload y preview
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Selecciona un archivo de audio",
            type=['mp3', 'm4a', 'wav', 'flac', 'ogg', 'opus', 'webm'],
            help="Formatos soportados: MP3, M4A, WAV, FLAC, OGG, Opus, WebM"
        )
    
    with col2:
        if uploaded_file:
            st.success(f"✅ Archivo cargado")
            st.info(f"**{uploaded_file.name}**")
            file_size_mb = uploaded_file.size / 1024 / 1024
            st.metric("Tamaño", f"{file_size_mb:.2f} MB")
    
    if not uploaded_file:
        st.info("👆 Sube un archivo de audio para comenzar la transcripción")
        st.stop()
    
    # Configuración
    st.markdown("---")
    st.subheader("⚙️ Configuración de Transcripción")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        model = st.selectbox(
            "🤖 Modelo Whisper",
            ['tiny', 'base', 'small', 'medium', 'turbo', 'large', 'large-v2', 'large-v3'],
            index=3,  # medium por defecto
            help="""
            - tiny/base: Muy rápidos, calidad básica
            - small: Rápido, buena calidad
            - medium: ⭐ Balance perfecto (recomendado)
            - turbo: Rápido, excelente calidad
            - large: Máxima calidad, más lento
            """
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
            'Chino': 'chinese',
            'Japonés': 'japanese',
            'Coreano': 'korean',
            'Ruso': 'russian',
            'Árabe': 'arabic',
        }
        
        language_display = st.selectbox(
            "🌍 Idioma",
            list(language_options.keys()),
            index=0,
            help="Dejar en 'Auto-detección' para que Whisper detecte el idioma automáticamente"
        )
        language = language_options[language_display]
    
    with col3:
        task = st.selectbox(
            "📋 Tarea",
            ['transcribe', 'translate'],
            help="""
            - transcribe: Mantiene el idioma original
            - translate: Transcribe y traduce a inglés
            """
        )
    
    # Opciones avanzadas
    with st.expander("🔧 Opciones Avanzadas"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            batch_size = st.slider(
                "Batch Size",
                min_value=1,
                max_value=32,
                value=8,
                help="Reduce este valor si aparecen errores de memoria GPU"
            )
        
        with col2:
            include_timestamps = st.checkbox(
                "Incluir timestamps",
                value=True,
                help="Necesario para generar subtítulos (SRT/VTT)"
            )
        
        with col3:
            compute_type = st.selectbox(
                "Precisión",
                ['float16', 'float32'],
                help="float16 es más rápido y usa menos memoria"
            )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            formats = st.multiselect(
                "📦 Formatos de exportación",
                ['txt', 'json', 'srt', 'vtt'],
                default=['txt'],
                help="Selecciona uno o más formatos para descargar"
            )
        
        with col2:
            st.info("""
            **Formatos disponibles:**
            - TXT: Texto plano
            - JSON: Con metadatos y timestamps
            - SRT: Subtítulos (video)
            - VTT: Subtítulos web
            """)
    
    # Botón de transcripción
    st.markdown("---")
    
    if st.button("🚀 Iniciar Transcripción", type="primary", use_container_width=True):
        
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Crear transcriptor
            with st.spinner("🔄 Inicializando modelo..."):
                transcriber = Transcriber(
                    model_name=model,
                    language=language,
                    batch_size=batch_size,
                    compute_type=compute_type
                )
            
            # Cargar modelo
            with st.spinner(f"📥 Cargando modelo **{model}**... (puede tardar en la primera vez)"):
                transcriber.load_model()
                st.success(f"✅ Modelo {model} cargado correctamente")
            
            # Transcribir
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            progress_text.text(f"🎙️ Transcribiendo con modelo {model}...")
            progress_bar.progress(50)
            
            start_time = time.time()
            
            result = transcriber.transcribe(
                tmp_path,
                return_timestamps=include_timestamps,
                task=task
            )
            
            processing_time = time.time() - start_time
            
            progress_bar.progress(100)
            progress_text.empty()
            progress_bar.empty()
            
            st.success(f"✅ Transcripción completada en {processing_time:.2f} segundos")
            
            # Métricas
            st.markdown("---")
            st.subheader("📊 Estadísticas")
            
            col1, col2, col3, col4 = st.columns(4)
            
            text_length = len(result.get('text', ''))
            word_count = len(result.get('text', '').split())
            
            col1.metric("📝 Caracteres", f"{text_length:,}")
            col2.metric("💬 Palabras", f"{word_count:,}")
            col3.metric("⏱️ Tiempo", f"{processing_time:.1f}s")
            
            chunks = result.get('chunks', [])
            if chunks:
                col4.metric("🔢 Segmentos", len(chunks))
                
                # Calcular duración de audio
                last_chunk = chunks[-1]
                if 'timestamp' in last_chunk and last_chunk['timestamp'][1]:
                    audio_duration = last_chunk['timestamp'][1]
                    speed_factor = audio_duration / processing_time if processing_time > 0 else 0
                    st.info(f"🎵 Duración del audio: {audio_duration/60:.1f} minutos | " 
                           f"⚡ Velocidad: {speed_factor:.1f}x tiempo real")
            
            # Mostrar transcripción
            st.markdown("---")
            st.subheader("📝 Resultado de la Transcripción")
            
            transcription_text = result.get('text', '')
            
            st.text_area(
                "Texto transcrito",
                transcription_text,
                height=400,
                help="Puedes copiar el texto desde aquí o descargarlo en los formatos disponibles abajo"
            )
            
            # Botones de descarga
            st.markdown("---")
            st.subheader("⬇️ Descargar Transcripción")
            
            if not formats:
                st.warning("⚠️ Selecciona al menos un formato de exportación en las opciones avanzadas")
            else:
                cols = st.columns(len(formats))
                
                base_filename = Path(uploaded_file.name).stem
                
                for idx, fmt in enumerate(formats):
                    with cols[idx]:
                        if fmt == 'txt':
                            st.download_button(
                                label="📄 Descargar TXT",
                                data=transcription_text,
                                file_name=f"{base_filename}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        elif fmt == 'json':
                            json_data = json.dumps(result, ensure_ascii=False, indent=2)
                            st.download_button(
                                label="📊 Descargar JSON",
                                data=json_data,
                                file_name=f"{base_filename}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                        
                        elif fmt == 'srt':
                            if not include_timestamps:
                                st.warning("⚠️ SRT requiere timestamps")
                            else:
                                srt_content = generate_srt(result)
                                if srt_content:
                                    st.download_button(
                                        label="🎬 Descargar SRT",
                                        data=srt_content,
                                        file_name=f"{base_filename}.srt",
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                                else:
                                    st.error("Error generando SRT")
                        
                        elif fmt == 'vtt':
                            if not include_timestamps:
                                st.warning("⚠️ VTT requiere timestamps")
                            else:
                                vtt_content = generate_vtt(result)
                                if vtt_content:
                                    st.download_button(
                                        label="🎬 Descargar VTT",
                                        data=vtt_content,
                                        file_name=f"{base_filename}.vtt",
                                        mime="text/vtt",
                                        use_container_width=True
                                    )
                                else:
                                    st.error("Error generando VTT")
            
            # Limpiar modelo
            with st.spinner("🧹 Liberando recursos..."):
                transcriber.unload_model()
            
            st.success("✅ Proceso completado. Recursos liberados.")
            
        except Exception as e:
            st.error(f"❌ Error durante la transcripción")
            st.exception(e)
            
            with st.expander("💡 Posibles soluciones"):
                st.markdown("""
                Si el error menciona "Out of Memory" o "CUDA":
                - Reduce el **batch_size** (prueba con 4, 2 o 1)
                - Usa un modelo más pequeño (**small** en vez de medium)
                - Cierra otras aplicaciones que usen GPU
                - Consulta la [documentación de optimización](https://github.com/tu-usuario/jorge-transcript/blob/main/MEMORY_OPTIMIZATION.md)
                
                Para otros errores:
                - Verifica que el archivo de audio no esté corrupto
                - Prueba con otro archivo para descartar problemas de formato
                - Revisa los [issues en GitHub](https://github.com/tu-usuario/jorge-transcript/issues)
                """)
        
        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == "__main__":
    main()

