"""
Clase principal de transcripción usando insanely-fast-whisper.
Gestiona la carga del modelo y el procesamiento de archivos de audio.
"""

import os
import time
import torch
from pathlib import Path
from typing import Dict, Any, Optional, List
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available


class Transcriber:
    """
    Clase para transcribir archivos de audio usando Whisper con aceleración GPU.
    """
    
    # Modelos disponibles
    AVAILABLE_MODELS = {
        'tiny': 'openai/whisper-tiny',
        'base': 'openai/whisper-base',
        'small': 'openai/whisper-small',
        'medium': 'openai/whisper-medium',
        'large': 'openai/whisper-large-v3',
        'large-v2': 'openai/whisper-large-v2',
        'large-v3': 'openai/whisper-large-v3',
        'turbo': 'openai/whisper-large-v3-turbo',
    }
    
    def __init__(
        self,
        model_name: str = 'medium',
        device: Optional[str] = None,
        language: Optional[str] = None,
        batch_size: int = 8,
        compute_type: str = 'float16',
        use_flash_attention: bool = True
    ):
        """
        Inicializa el transcriptor con el modelo especificado.
        
        Args:
            model_name: Nombre del modelo ('tiny', 'base', 'small', 'medium', 'large', 'turbo')
            device: Dispositivo a usar ('cuda', 'cpu', o None para auto-detectar)
            language: Idioma del audio (None para auto-detección, o 'spanish', 'english', etc.)
            batch_size: Tamaño del batch para procesamiento
            compute_type: Tipo de precisión ('float16', 'float32')
            use_flash_attention: Usar Flash Attention 2 si está disponible
        """
        self.model_name = model_name
        self.language = language
        self.batch_size = batch_size
        self.compute_type = compute_type
        
        # Determinar dispositivo
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        # Verificar disponibilidad de GPU
        if self.device == 'cuda' and not torch.cuda.is_available():
            print("⚠ Advertencia: CUDA no disponible, usando CPU (será más lento)")
            self.device = 'cpu'
        
        # Verificar Flash Attention
        self.use_flash_attention = use_flash_attention and is_flash_attn_2_available()
        
        # Pipeline de transcripción (se cargará cuando sea necesario)
        self.pipe = None
        
        print(f"Transcriptor inicializado:")
        print(f"  Dispositivo: {self.device}")
        print(f"  Modelo: {model_name}")
        print(f"  Idioma: {language if language else 'auto-detección'}")
        print(f"  Batch size: {batch_size}")
        print(f"  Flash Attention: {self.use_flash_attention}")
    
    def _get_model_id(self) -> str:
        """
        Obtiene el ID completo del modelo en Hugging Face.
        
        Returns:
            ID del modelo
        """
        model_id = self.AVAILABLE_MODELS.get(self.model_name.lower())
        if model_id is None:
            # Si no está en el diccionario, asumir que es un path completo
            model_id = self.model_name
        return model_id
    
    def load_model(self) -> None:
        """
        Carga el modelo de Whisper en memoria.
        """
        if self.pipe is not None:
            print("✓ Modelo ya cargado")
            return
        
        print(f"\nCargando modelo '{self.model_name}'...")
        print("(La primera vez descargará el modelo, puede tardar varios minutos)")
        
        model_id = self._get_model_id()
        
        try:
            # Configurar torch dtype
            torch_dtype = torch.float16 if self.compute_type == 'float16' and self.device == 'cuda' else torch.float32
            
            # Configuración del modelo
            model_kwargs = {
                "torch_dtype": torch_dtype,
            }
            
            # Agregar Flash Attention si está disponible
            if self.use_flash_attention and self.device == 'cuda':
                model_kwargs["attn_implementation"] = "flash_attention_2"
                print("  Usando Flash Attention 2 para mayor velocidad")
            
            # Crear pipeline de transcripción
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=model_id,
                device=self.device,
                model_kwargs=model_kwargs,
            )
            
            # Mostrar información de GPU si está disponible
            if self.device == 'cuda':
                gpu_name = torch.cuda.get_device_name(0)
                memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
                print(f"\n✓ Modelo cargado en GPU: {gpu_name}")
                print(f"  Memoria GPU usada: {memory_allocated:.2f} GB")
                
                # Limpiar caché de GPU para liberar memoria no utilizada
                torch.cuda.empty_cache()
            else:
                print(f"\n✓ Modelo cargado en CPU")
            
        except Exception as e:
            print(f"\n✗ Error al cargar el modelo: {e}")
            raise
    
    def transcribe(
        self,
        audio_file: str,
        return_timestamps: bool = True,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """
        Transcribe un archivo de audio.
        
        Args:
            audio_file: Ruta al archivo de audio
            return_timestamps: Si True, incluye timestamps de cada segmento
            task: 'transcribe' o 'translate' (traducir a inglés)
            
        Returns:
            Diccionario con la transcripción y metadatos
        """
        # Cargar modelo si no está cargado
        if self.pipe is None:
            self.load_model()
        
        # Verificar que el archivo existe
        if not Path(audio_file).exists():
            raise FileNotFoundError(f"Archivo no encontrado: {audio_file}")
        
        print(f"\nTranscribiendo: {Path(audio_file).name}")
        
        # Configurar parámetros de generación
        generate_kwargs = {
            "task": task,
        }
        
        # Solo especificar idioma si se proporcionó explícitamente
        # Si es None, Whisper auto-detectará el idioma
        if self.language is not None:
            generate_kwargs["language"] = self.language
        
        # Iniciar tiempo
        start_time = time.time()
        
        try:
            # Realizar transcripción
            result = self.pipe(
                audio_file,
                chunk_length_s=30,  # Procesar en chunks de 30 segundos
                batch_size=self.batch_size,
                return_timestamps=return_timestamps,
                generate_kwargs=generate_kwargs,
            )
            
            # Calcular tiempo de procesamiento
            processing_time = time.time() - start_time
            
            # Agregar metadatos
            result['metadata'] = {
                'file': str(audio_file),
                'model': self.model_name,
                'language': self.language,
                'device': self.device,
                'processing_time': processing_time,
            }
            
            print(f"✓ Transcripción completada en {processing_time:.2f}s")
            
            return result
            
        except torch.cuda.OutOfMemoryError as e:
            print(f"\n✗ Error: Memoria GPU insuficiente")
            print(f"  Memoria requerida excede la disponible en la GPU")
            print(f"  Soluciones:")
            print(f"    1. Reducir batch size: --batch-size {max(1, self.batch_size // 2)}")
            print(f"    2. Usar un modelo más pequeño: --model small")
            print(f"    3. Usar CPU (más lento): --device cpu")
            
            # Limpiar memoria y relanzar error
            if self.device == 'cuda':
                torch.cuda.empty_cache()
            raise
            
        except Exception as e:
            print(f"✗ Error durante la transcripción: {e}")
            raise
    
    def transcribe_batch(
        self,
        audio_files: List[str],
        return_timestamps: bool = True,
        task: str = "transcribe"
    ) -> List[Dict[str, Any]]:
        """
        Transcribe múltiples archivos de audio.
        
        Args:
            audio_files: Lista de rutas a archivos de audio
            return_timestamps: Si True, incluye timestamps de cada segmento
            task: 'transcribe' o 'translate'
            
        Returns:
            Lista de diccionarios con transcripciones
        """
        results = []
        total_files = len(audio_files)
        
        print(f"\nIniciando transcripción de {total_files} archivo(s)")
        print("=" * 70)
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n[{i}/{total_files}]")
            
            try:
                result = self.transcribe(
                    audio_file,
                    return_timestamps=return_timestamps,
                    task=task
                )
                results.append(result)
                
            except Exception as e:
                print(f"✗ Error procesando {audio_file}: {e}")
                # Continuar con el siguiente archivo
                results.append({
                    'text': '',
                    'chunks': [],
                    'metadata': {
                        'file': str(audio_file),
                        'error': str(e)
                    }
                })
        
        print("\n" + "=" * 70)
        print(f"✓ Transcripción batch completada: {len(results)}/{total_files} archivos")
        
        return results
    
    def unload_model(self) -> None:
        """
        Libera el modelo de la memoria.
        """
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
            
            if self.device == 'cuda':
                torch.cuda.empty_cache()
                print("✓ Modelo liberado de la GPU")
            else:
                print("✓ Modelo liberado de la memoria")
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Obtiene información del dispositivo actual.
        
        Returns:
            Diccionario con información del dispositivo
        """
        info = {
            'device': self.device,
            'cuda_available': torch.cuda.is_available(),
        }
        
        if self.device == 'cuda' and torch.cuda.is_available():
            info.update({
                'gpu_name': torch.cuda.get_device_name(0),
                'gpu_count': torch.cuda.device_count(),
                'cuda_version': torch.version.cuda,
                'memory_total': torch.cuda.get_device_properties(0).total_memory / (1024**3),
                'memory_allocated': torch.cuda.memory_allocated(0) / (1024**3),
                'memory_reserved': torch.cuda.memory_reserved(0) / (1024**3),
            })
        
        return info
    
    @classmethod
    def list_available_models(cls) -> None:
        """
        Imprime la lista de modelos disponibles.
        """
        print("\nModelos Whisper disponibles:")
        print("=" * 70)
        print(f"{'Nombre':<15} {'ID de Hugging Face':<45} {'Tamaño'}")
        print("-" * 70)
        
        model_sizes = {
            'tiny': '~39M parámetros (~1 GB VRAM)',
            'base': '~74M parámetros (~1 GB VRAM)',
            'small': '~244M parámetros (~2 GB VRAM)',
            'medium': '~769M parámetros (~5 GB VRAM)',
            'large': '~1550M parámetros (~10 GB VRAM)',
            'large-v2': '~1550M parámetros (~10 GB VRAM)',
            'large-v3': '~1550M parámetros (~10 GB VRAM)',
            'turbo': '~809M parámetros (~6 GB VRAM)',
        }
        
        for name, model_id in cls.AVAILABLE_MODELS.items():
            size = model_sizes.get(name, 'N/A')
            print(f"{name:<15} {model_id:<45} {size}")
        
        print("=" * 70)

