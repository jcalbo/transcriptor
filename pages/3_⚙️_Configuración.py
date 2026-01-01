"""
Página de configuración avanzada
"""

import streamlit as st
import torch
import os

st.set_page_config(
    page_title="Configuración",
    page_icon="⚙️",
    layout="wide"
)


def main():
    st.title("⚙️ Configuración Avanzada")
    st.markdown("Ajusta parámetros del sistema y opciones avanzadas")
    st.markdown("---")
    
    # Información del Sistema
    st.subheader("🖥️ Información del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💻 Hardware")
        
        # GPU Info
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_count = torch.cuda.device_count()
            cuda_version = torch.version.cuda
            
            memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
            memory_reserved = torch.cuda.memory_reserved(0) / (1024**3)
            memory_free = memory_total - memory_reserved
            
            st.success("✅ GPU Disponible")
            st.info(f"**{gpu_name}**")
            st.write(f"- GPUs detectadas: {gpu_count}")
            st.write(f"- CUDA versión: {cuda_version}")
            st.write(f"- VRAM total: {memory_total:.2f} GB")
            st.write(f"- VRAM libre: {memory_free:.2f} GB")
            st.write(f"- VRAM usada: {memory_allocated:.2f} GB")
            st.write(f"- VRAM reservada: {memory_reserved:.2f} GB")
            
            # Botón para limpiar caché
            if st.button("🧹 Limpiar Caché GPU"):
                torch.cuda.empty_cache()
                st.success("✅ Caché GPU limpiada")
                st.rerun()
        else:
            st.warning("⚠️ GPU no disponible")
            st.info("La aplicación usará CPU (más lento)")
    
    with col2:
        st.markdown("### 📦 Software")
        
        import sys
        from src.transcriber import Transcriber
        
        st.write(f"- Python: {sys.version.split()[0]}")
        st.write(f"- PyTorch: {torch.__version__}")
        
        try:
            import transformers
            st.write(f"- Transformers: {transformers.__version__}")
        except:
            pass
        
        try:
            import streamlit as st_module
            st.write(f"- Streamlit: {st_module.__version__}")
        except:
            pass
        
        st.markdown("---")
        
        # Modelos disponibles
        st.markdown("### 🤖 Modelos Disponibles")
        models = list(Transcriber.AVAILABLE_MODELS.keys())
        st.write(", ".join(models))
    
    # Configuración de Modelos
    st.markdown("---")
    st.subheader("🤖 Configuración de Modelos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Información de Modelos")
        
        model_info = {
            'tiny': {'params': '39M', 'vram': '~1 GB', 'speed': '⚡⚡⚡⚡⚡', 'quality': '⭐⭐'},
            'base': {'params': '74M', 'vram': '~1 GB', 'speed': '⚡⚡⚡⚡', 'quality': '⭐⭐⭐'},
            'small': {'params': '244M', 'vram': '~2 GB', 'speed': '⚡⚡⚡', 'quality': '⭐⭐⭐⭐'},
            'medium': {'params': '769M', 'vram': '~5 GB', 'speed': '⚡⚡', 'quality': '⭐⭐⭐⭐⭐'},
            'turbo': {'params': '809M', 'vram': '~6 GB', 'speed': '⚡⚡⚡', 'quality': '⭐⭐⭐⭐⭐'},
            'large': {'params': '1550M', 'vram': '~10 GB', 'speed': '⚡', 'quality': '⭐⭐⭐⭐⭐'},
        }
        
        selected_model = st.selectbox(
            "Ver información del modelo:",
            list(model_info.keys())
        )
        
        info = model_info[selected_model]
        st.write(f"**Parámetros:** {info['params']}")
        st.write(f"**VRAM requerida:** {info['vram']}")
        st.write(f"**Velocidad:** {info['speed']}")
        st.write(f"**Calidad:** {info['quality']}")
    
    with col2:
        st.markdown("### Caché de Modelos")
        
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        
        if os.path.exists(cache_dir):
            st.success("✅ Directorio de caché encontrado")
            st.code(cache_dir, language="bash")
            
            # Contar modelos descargados
            try:
                model_dirs = [d for d in os.listdir(cache_dir) if d.startswith("models--openai--whisper")]
                if model_dirs:
                    st.info(f"📦 {len(model_dirs)} modelo(s) descargado(s)")
                    with st.expander("Ver modelos descargados"):
                        for model_dir in model_dirs:
                            st.text(f"• {model_dir}")
                else:
                    st.warning("⚠️ No hay modelos descargados aún")
            except Exception as e:
                st.error(f"Error leyendo caché: {e}")
        else:
            st.info("ℹ️ No hay modelos descargados aún")
            st.write("Los modelos se descargarán automáticamente la primera vez que se usen")
    
    # Optimización GPU
    st.markdown("---")
    st.subheader("⚡ Optimización de GPU")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### batch_size Recomendado")
        st.markdown("""
        El `batch_size` controla cuántos fragmentos de audio se procesan simultáneamente:
        
        | Modelo | batch_size Recomendado |
        |--------|------------------------|
        | tiny/base | 24-32 |
        | small | 16 |
        | medium | 8 |
        | turbo | 8 |
        | large | 4 |
        
        **Para tu RTX 4080 (11.73 GB):**
        - medium: batch_size=8 ✅
        - large: batch_size=4
        """)
    
    with col2:
        st.markdown("### Solución de Problemas")
        
        with st.expander("💡 Error: Out of Memory"):
            st.markdown("""
            Si recibes error de memoria GPU:
            
            1. **Reduce batch_size** (prueba 4, 2, o 1)
            2. **Usa modelo más pequeño** (small en vez de medium)
            3. **Cierra otras apps** que usen GPU
            4. **Limpia caché GPU** (botón arriba)
            """)
        
        with st.expander("🐌 Transcripción Lenta"):
            st.markdown("""
            Si el procesamiento es lento:
            
            1. **Verifica que estés usando GPU** (no CPU)
            2. **Incrementa batch_size** si hay VRAM libre
            3. **Usa modelo más pequeño** (turbo es rápido)
            4. **Cierra apps** en segundo plano
            """)
        
        with st.expander("❓ Auto-detección no funciona"):
            st.markdown("""
            Si el idioma no se detecta bien:
            
            1. **Especifica el idioma manualmente**
            2. **Usa un modelo más grande** (mejor detección)
            3. **Verifica calidad del audio** (sin mucho ruido)
            """)
    
    # Idiomas Soportados
    st.markdown("---")
    st.subheader("🌍 Idiomas Soportados")
    
    st.markdown("""
    Whisper soporta 99+ idiomas. Los más comunes:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        - 🇪🇸 Español
        - 🇬🇧 Inglés
        - 🇫🇷 Francés
        - 🇩🇪 Alemán
        - 🇮🇹 Italiano
        """)
    
    with col2:
        st.markdown("""
        - 🇵🇹 Portugués
        - 🇨🇳 Chino
        - 🇯🇵 Japonés
        - 🇰🇷 Coreano
        - 🇷🇺 Ruso
        """)
    
    with col3:
        st.markdown("""
        - 🇸🇦 Árabe
        - 🇮🇳 Hindi
        - 🇳🇱 Holandés
        - 🇵🇱 Polaco
        - 🇹🇷 Turco
        """)
    
    st.info("💡 La auto-detección funciona para todos estos idiomas y muchos más")
    
    # Enlaces útiles
    st.markdown("---")
    st.subheader("📚 Recursos y Documentación")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📖 Documentación
        - [README](https://github.com/tu-usuario/jorge-transcript)
        - [Guía de Testing](https://github.com/tu-usuario/jorge-transcript/blob/main/TESTING.md)
        - [Optimización GPU](https://github.com/tu-usuario/jorge-transcript/blob/main/MEMORY_OPTIMIZATION.md)
        """)
    
    with col2:
        st.markdown("""
        ### 🔗 Enlaces
        - [GitHub](https://github.com/tu-usuario/jorge-transcript)
        - [Issues](https://github.com/tu-usuario/jorge-transcript/issues)
        - [OpenAI Whisper](https://github.com/openai/whisper)
        """)
    
    with col3:
        st.markdown("""
        ### 💬 Soporte
        - [Crear Issue](https://github.com/tu-usuario/jorge-transcript/issues/new)
        - [Discusiones](https://github.com/tu-usuario/jorge-transcript/discussions)
        - [Email](mailto:tu-email@example.com)
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Jorge Transcript v0.2.0 | "
        "Desarrollado con ❤️ usando Whisper, PyTorch y Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

