"""
Utilidades para la aplicación de transcripción.
Incluye funciones de validación, formateo y exportación de resultados.
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import timedelta


# Formatos de audio soportados
SUPPORTED_FORMATS = {'.mp3', '.wav', '.flac', '.ogg', '.opus', '.webm'}


def validate_audio_file(file_path: str) -> bool:
    """
    Valida si un archivo existe y tiene un formato de audio soportado.
    
    Args:
        file_path: Ruta al archivo de audio
        
    Returns:
        True si el archivo es válido, False en caso contrario
    """
    path = Path(file_path)
    
    # Verificar que existe
    if not path.exists():
        print(f"✗ Error: El archivo no existe: {file_path}")
        return False
    
    # Verificar que es un archivo (no directorio)
    if not path.is_file():
        print(f"✗ Error: La ruta no es un archivo: {file_path}")
        return False
    
    # Verificar extensión
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        print(f"✗ Error: Formato no soportado: {path.suffix}")
        print(f"  Formatos válidos: {', '.join(SUPPORTED_FORMATS)}")
        return False
    
    return True


def get_audio_files_from_directory(directory: str) -> List[Path]:
    """
    Obtiene todos los archivos de audio válidos de un directorio.
    
    Args:
        directory: Ruta al directorio
        
    Returns:
        Lista de Path con archivos de audio encontrados
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"✗ Error: El directorio no existe: {directory}")
        return []
    
    if not dir_path.is_dir():
        print(f"✗ Error: La ruta no es un directorio: {directory}")
        return []
    
    # Buscar archivos de audio
    audio_files = []
    for ext in SUPPORTED_FORMATS:
        audio_files.extend(dir_path.glob(f"*{ext}"))
        audio_files.extend(dir_path.glob(f"*{ext.upper()}"))
    
    # Ordenar por nombre
    audio_files.sort()
    
    return audio_files


def ensure_directory(directory: str) -> Path:
    """
    Crea un directorio si no existe.
    
    Args:
        directory: Ruta al directorio
        
    Returns:
        Path del directorio creado
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def format_timestamp(seconds: float) -> str:
    """
    Formatea segundos en formato HH:MM:SS.mmm para subtítulos.
    
    Args:
        seconds: Tiempo en segundos
        
    Returns:
        String formateado como HH:MM:SS.mmm
    """
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = td.total_seconds() % 60
    millis = int((secs % 1) * 1000)
    secs = int(secs)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def export_as_txt(transcription: Dict[str, Any], output_path: str) -> None:
    """
    Exporta la transcripción como archivo de texto plano.
    
    Args:
        transcription: Diccionario con los datos de transcripción
        output_path: Ruta del archivo de salida
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(transcription.get('text', ''))
    
    print(f"✓ Transcripción guardada: {output_path}")


def export_as_json(transcription: Dict[str, Any], output_path: str) -> None:
    """
    Exporta la transcripción como archivo JSON con metadatos y segmentos.
    
    Args:
        transcription: Diccionario con los datos de transcripción
        output_path: Ruta del archivo de salida
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(transcription, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Transcripción JSON guardada: {output_path}")


def export_as_srt(transcription: Dict[str, Any], output_path: str) -> None:
    """
    Exporta la transcripción como archivo de subtítulos SRT.
    
    Args:
        transcription: Diccionario con los datos de transcripción
        output_path: Ruta del archivo de salida
    """
    segments = transcription.get('chunks', [])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, start=1):
            # Número de secuencia
            f.write(f"{i}\n")
            
            # Timestamps
            start_time = format_timestamp(segment['timestamp'][0])
            end_time = format_timestamp(segment['timestamp'][1])
            f.write(f"{start_time} --> {end_time}\n")
            
            # Texto
            f.write(f"{segment['text'].strip()}\n")
            f.write("\n")
    
    print(f"✓ Subtítulos SRT guardados: {output_path}")


def export_as_vtt(transcription: Dict[str, Any], output_path: str) -> None:
    """
    Exporta la transcripción como archivo de subtítulos WebVTT.
    
    Args:
        transcription: Diccionario con los datos de transcripción
        output_path: Ruta del archivo de salida
    """
    segments = transcription.get('chunks', [])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")
        
        for i, segment in enumerate(segments, start=1):
            # Timestamps
            start_time = format_timestamp(segment['timestamp'][0])
            end_time = format_timestamp(segment['timestamp'][1])
            f.write(f"{start_time} --> {end_time}\n")
            
            # Texto
            f.write(f"{segment['text'].strip()}\n")
            f.write("\n")
    
    print(f"✓ Subtítulos VTT guardados: {output_path}")


def get_output_path(input_path: str, output_dir: str, format: str) -> str:
    """
    Genera la ruta de salida basada en el archivo de entrada y el formato.
    
    Args:
        input_path: Ruta del archivo de entrada
        output_dir: Directorio de salida
        format: Formato de salida ('txt', 'json', 'srt', 'vtt')
        
    Returns:
        Ruta completa del archivo de salida
    """
    input_file = Path(input_path)
    output_directory = ensure_directory(output_dir)
    
    # Cambiar extensión según el formato
    output_filename = f"{input_file.stem}.{format}"
    output_path = output_directory / output_filename
    
    return str(output_path)


def format_duration(seconds: float) -> str:
    """
    Formatea la duración en segundos a un formato legible.
    
    Args:
        seconds: Duración en segundos
        
    Returns:
        String formateado (ej: "2m 30s" o "1h 15m 30s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def print_transcription_summary(
    input_file: str,
    transcription: Dict[str, Any],
    processing_time: float
) -> None:
    """
    Imprime un resumen de la transcripción realizada.
    
    Args:
        input_file: Nombre del archivo procesado
        transcription: Datos de la transcripción
        processing_time: Tiempo de procesamiento en segundos
    """
    text = transcription.get('text', '')
    chunks = transcription.get('chunks', [])
    
    print("\n" + "=" * 70)
    print(f"Archivo: {Path(input_file).name}")
    print(f"Tiempo de procesamiento: {format_duration(processing_time)}")
    print(f"Caracteres transcritos: {len(text)}")
    print(f"Palabras aproximadas: {len(text.split())}")
    print(f"Segmentos: {len(chunks)}")
    
    # Calcular duración del audio si está disponible
    if chunks and len(chunks) > 0:
        last_chunk = chunks[-1]
        if 'timestamp' in last_chunk and last_chunk['timestamp'][1]:
            audio_duration = last_chunk['timestamp'][1]
            speed_factor = audio_duration / processing_time if processing_time > 0 else 0
            print(f"Duración del audio: {format_duration(audio_duration)}")
            print(f"Velocidad: {speed_factor:.1f}x tiempo real")
    
    print("=" * 70)

