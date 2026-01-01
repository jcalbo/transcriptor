"""
Aplicación Web de Transcripción con Streamlit
Jorge Transcript - Whisper + GPU
"""

import streamlit as st
import torch
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Jorge Transcript - Whisper + GPU",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/tu-usuario/jorge-transcript',
        'Report a bug': 'https://github.com/tu-usuario/jorge-transcript/issues',
        'About': '# Jorge Transcript\nTranscripción de audio con Whisper y aceleración GPU'
    }
)

def main():
    """Página principal de la aplicación."""
    
    # Título principal
    st.title("🎙️ Jorge Transcript")
    st.markdown("### Transcripción de Audio con Whisper + GPU")
    st.markdown("---")
    
    # Sidebar con información del sistema
    with st.sidebar:
        st.markdown("## 📊 Estado del Sistema")
        
        # Verificar GPU
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
            memory_free = memory_total - memory_allocated
            
            st.success("✅ GPU Disponible")
            st.info(f"**{gpu_name}**")
            st.metric("VRAM Total", f"{memory_total:.2f} GB")
            st.metric("VRAM Libre", f"{memory_free:.2f} GB")
        else:
            st.warning("⚠️ GPU no disponible")
            st.info("Usando CPU (más lento)")
        
        st.markdown("---")
        st.markdown("## 🚀 Características")
        st.markdown("""
        - ✅ Auto-detección de idioma
        - ✅ 8 modelos Whisper
        - ✅ Aceleración GPU (CUDA)
        - ✅ Múltiples formatos
        - ✅ Procesamiento batch
        - ✅ Interfaz web intuitiva
        """)
        
        st.markdown("---")
        st.markdown("## 📚 Recursos")
        st.markdown("""
        - [GitHub](https://github.com/tu-usuario/jorge-transcript)
        - [Documentación](https://github.com/tu-usuario/jorge-transcript/blob/main/README.md)
        - [Reportar Bug](https://github.com/tu-usuario/jorge-transcript/issues)
        """)
    
    # Contenido principal - Tarjetas de navegación
    st.markdown("## 🎯 Selecciona una Opción")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("### 🎤 Transcripción Individual")
            st.markdown("Transcribe un archivo de audio a texto")
            st.markdown("")
            st.markdown("**Ideal para:**")
            st.markdown("- Entrevistas")
            st.markdown("- Podcasts")
            st.markdown("- Conferencias")
            st.markdown("- Notas de voz")
            st.markdown("")
            if st.button("🚀 Comenzar", key="btn_single", use_container_width=True, type="primary"):
                st.switch_page("pages/1_🎤_Transcribir.py")
    
    with col2:
        with st.container():
            st.markdown("### 📁 Procesamiento Batch")
            st.markdown("Procesa múltiples archivos automáticamente")
            st.markdown("")
            st.markdown("**Ideal para:**")
            st.markdown("- Múltiples grabaciones")
            st.markdown("- Archivos de un proyecto")
            st.markdown("- Transcripciones masivas")
            st.markdown("- Automatización")
            st.markdown("")
            if st.button("🚀 Comenzar", key="btn_batch", use_container_width=True, type="primary"):
                st.switch_page("pages/2_📁_Batch.py")
    
    with col3:
        with st.container():
            st.markdown("### ⚙️ Configuración")
            st.markdown("Ajusta parámetros avanzados del sistema")
            st.markdown("")
            st.markdown("**Configura:**")
            st.markdown("- Modelos predeterminados")
            st.markdown("- Parámetros de GPU")
            st.markdown("- Formatos de exportación")
            st.markdown("- Opciones avanzadas")
            st.markdown("")
            if st.button("🚀 Abrir", key="btn_config", use_container_width=True, type="primary"):
                st.switch_page("pages/3_⚙️_Configuración.py")
    
    # Sección de guía rápida
    st.markdown("---")
    st.markdown("## 📖 Guía Rápida")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("🆕 ¿Primera vez? Comienza aquí"):
            st.markdown("""
            ### Pasos para transcribir
            
            1. **Haz clic en "🎤 Transcripción Individual"**
            2. **Sube tu archivo de audio** (mp3, m4a, wav, etc.)
            3. **Selecciona el modelo** (recomendado: `medium`)
            4. **Haz clic en "Transcribir"**
            5. **Espera** mientras se procesa (verás el progreso)
            6. **Descarga** el resultado en tu formato preferido
            
            ---
            
            ### Primera ejecución
            
            ⏱️ La primera vez que uses un modelo, se descargará automáticamente desde Hugging Face.
            Esto puede tardar 1-5 minutos dependiendo de tu conexión.
            
            Los modelos quedan guardados y no necesitan descargarse nuevamente.
            """)
    
    with col2:
        with st.expander("❓ Preguntas Frecuentes"):
            st.markdown("""
            ### ¿Qué modelo debo usar?
            
            - **`tiny`**: Muy rápido, calidad básica (pruebas)
            - **`small`**: Rápido, buena calidad (recomendado para probar)
            - **`medium`**: ⭐ **Balance perfecto** (recomendado)
            - **`large`**: Máxima calidad, más lento
            - **`turbo`**: Rápido con excelente calidad
            
            ---
            
            ### ¿Necesito especificar el idioma?
            
            **No es necesario.** La auto-detección funciona muy bien para la mayoría de idiomas.
            Solo especifica el idioma si la detección falla.
            
            ---
            
            ### ¿Qué hacer si hay error de memoria GPU?
            
            1. Reduce el `batch_size` (en Configuración)
            2. Usa un modelo más pequeño (`small` en vez de `medium`)
            3. Cierra otras aplicaciones que usen GPU
            4. Consulta la [documentación completa](https://github.com/tu-usuario/jorge-transcript/blob/main/MEMORY_OPTIMIZATION.md)
            """)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<div style='text-align: center; color: gray;'>"
            "Desarrollado con ❤️ usando Whisper, PyTorch y Streamlit<br>"
            "v0.2.0 | "
            "<a href='https://github.com/tu-usuario/jorge-transcript' target='_blank'>GitHub</a>"
            "</div>",
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()

