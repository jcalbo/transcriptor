#!/usr/bin/env python3
"""
Aplicación de transcripción de audio usando Whisper con GPU.
Soporta múltiples formatos de audio (mp3, m4a, wav, etc.) y exportación en varios formatos.
"""

import sys
import argparse
from pathlib import Path
from typing import List

from src.transcriber import Transcriber
from src.utils import (
    validate_audio_file,
    get_audio_files_from_directory,
    get_output_path,
    export_as_txt,
    export_as_json,
    export_as_srt,
    export_as_vtt,
    print_transcription_summary,
)


def setup_argparse() -> argparse.ArgumentParser:
    """
    Configura y retorna el parser de argumentos de línea de comandos.
    
    Returns:
        ArgumentParser configurado
    """
    parser = argparse.ArgumentParser(
        description='Transcripción de audio usando Whisper con aceleración GPU',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Transcribir con auto-detección de idioma (recomendado)
  python main.py --input audio.mp3
  
  # Forzar idioma específico si la auto-detección falla
  python main.py --input audio_ingles.mp3 --language english
  python main.py --input audio_espanol.mp3 --language spanish
  
  # Transcribir Y traducir a inglés (cualquier idioma → inglés)
  python main.py --input audio_espanol.mp3 --task translate
  
  # Transcribir con modelo específico
  python main.py --input audio.m4a --model large
  
  # Transcribir múltiples archivos de un directorio
  python main.py --input-dir ./input --output-dir ./output
  
  # Exportar en formato SRT (subtítulos)
  python main.py --input audio.mp3 --format srt
  
  # Exportar en múltiples formatos
  python main.py --input audio.mp3 --format txt json srt
  
  # Listar modelos disponibles
  python main.py --list-models
  
  # Mostrar información de GPU
  python main.py --gpu-info
        """
    )
    
    # Argumentos de entrada
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        '-i', '--input',
        type=str,
        help='Archivo de audio individual a transcribir'
    )
    input_group.add_argument(
        '-d', '--input-dir',
        type=str,
        help='Directorio con archivos de audio a transcribir'
    )
    
    # Argumentos de salida
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Archivo de salida (solo para --input). Si no se especifica, se guarda en ./output/'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./output',
        help='Directorio de salida para transcripciones (default: ./output)'
    )
    
    # Configuración del modelo
    parser.add_argument(
        '-m', '--model',
        type=str,
        default='medium',
        choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3', 'turbo'],
        help='Modelo de Whisper a usar (default: medium)'
    )
    parser.add_argument(
        '-l', '--language',
        type=str,
        default=None,
        help='Idioma del audio para forzar transcripción (default: auto-detección). Ej: spanish, english, french, german'
    )
    parser.add_argument(
        '--task',
        type=str,
        default='transcribe',
        choices=['transcribe', 'translate'],
        help='Tarea: "transcribe" mantiene idioma original, "translate" transcribe y traduce a inglés (default: transcribe)'
    )
    
    # Formato de salida
    parser.add_argument(
        '-f', '--format',
        type=str,
        nargs='+',
        default=['txt'],
        choices=['txt', 'json', 'srt', 'vtt'],
        help='Formato(s) de salida (default: txt). Puede especificar múltiples'
    )
    
    # Configuración de GPU
    parser.add_argument(
        '--device',
        type=str,
        default=None,
        choices=['cuda', 'cpu'],
        help='Dispositivo a usar (default: auto-detectar)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=8,
        help='Tamaño del batch para procesamiento (default: 8). Reduce si hay errores de memoria GPU'
    )
    parser.add_argument(
        '--compute-type',
        type=str,
        default='float16',
        choices=['float16', 'float32'],
        help='Tipo de precisión (default: float16 para GPU)'
    )
    parser.add_argument(
        '--no-flash-attention',
        action='store_true',
        help='Desactivar Flash Attention 2'
    )
    
    # Opciones de transcripción
    parser.add_argument(
        '--no-timestamps',
        action='store_true',
        help='No incluir timestamps en la transcripción'
    )
    
    # Comandos informativos
    parser.add_argument(
        '--list-models',
        action='store_true',
        help='Listar modelos disponibles y salir'
    )
    parser.add_argument(
        '--gpu-info',
        action='store_true',
        help='Mostrar información de GPU y salir'
    )
    
    # Verbosidad
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo verbose (más información de debug)'
    )
    
    return parser


def process_single_file(
    transcriber: Transcriber,
    input_file: str,
    output_path: str,
    output_dir: str,
    formats: List[str],
    return_timestamps: bool,
    task: str
) -> None:
    """
    Procesa un archivo de audio individual.
    
    Args:
        transcriber: Instancia de Transcriber
        input_file: Ruta al archivo de entrada
        output_path: Ruta de salida específica (o None)
        output_dir: Directorio de salida
        formats: Lista de formatos de exportación
        return_timestamps: Si incluir timestamps
        task: 'transcribe' o 'translate'
    """
    import time
    
    # Validar archivo
    if not validate_audio_file(input_file):
        sys.exit(1)
    
    # Realizar transcripción
    start_time = time.time()
    result = transcriber.transcribe(
        input_file,
        return_timestamps=return_timestamps,
        task=task
    )
    processing_time = time.time() - start_time
    
    # Mostrar resumen
    print_transcription_summary(input_file, result, processing_time)
    
    # Exportar en los formatos solicitados
    print(f"\nExportando transcripción...")
    
    for fmt in formats:
        if output_path and len(formats) == 1:
            # Si se especificó output y solo hay un formato, usar ese path
            out_path = output_path
        else:
            # Generar path automático
            out_path = get_output_path(input_file, output_dir, fmt)
        
        # Exportar según el formato
        if fmt == 'txt':
            export_as_txt(result, out_path)
        elif fmt == 'json':
            export_as_json(result, out_path)
        elif fmt == 'srt':
            export_as_srt(result, out_path)
        elif fmt == 'vtt':
            export_as_vtt(result, out_path)


def process_directory(
    transcriber: Transcriber,
    input_dir: str,
    output_dir: str,
    formats: List[str],
    return_timestamps: bool,
    task: str
) -> None:
    """
    Procesa todos los archivos de audio en un directorio.
    
    Args:
        transcriber: Instancia de Transcriber
        input_dir: Directorio con archivos de entrada
        output_dir: Directorio de salida
        formats: Lista de formatos de exportación
        return_timestamps: Si incluir timestamps
        task: 'transcribe' o 'translate'
    """
    import time
    
    # Obtener archivos de audio
    audio_files = get_audio_files_from_directory(input_dir)
    
    if not audio_files:
        print(f"✗ No se encontraron archivos de audio en: {input_dir}")
        sys.exit(1)
    
    print(f"✓ Encontrados {len(audio_files)} archivo(s) de audio")
    
    # Procesar cada archivo
    total_start_time = time.time()
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n{'='*70}")
        print(f"Procesando archivo {i}/{len(audio_files)}")
        print(f"{'='*70}")
        
        try:
            # Transcribir
            start_time = time.time()
            result = transcriber.transcribe(
                str(audio_file),
                return_timestamps=return_timestamps,
                task=task
            )
            processing_time = time.time() - start_time
            
            # Mostrar resumen
            print_transcription_summary(str(audio_file), result, processing_time)
            
            # Exportar
            print(f"\nExportando...")
            for fmt in formats:
                out_path = get_output_path(str(audio_file), output_dir, fmt)
                
                if fmt == 'txt':
                    export_as_txt(result, out_path)
                elif fmt == 'json':
                    export_as_json(result, out_path)
                elif fmt == 'srt':
                    export_as_srt(result, out_path)
                elif fmt == 'vtt':
                    export_as_vtt(result, out_path)
        
        except Exception as e:
            print(f"✗ Error procesando {audio_file.name}: {e}")
            continue
    
    total_time = time.time() - total_start_time
    print(f"\n{'='*70}")
    print(f"✓ Proceso completado")
    print(f"  Archivos procesados: {len(audio_files)}")
    print(f"  Tiempo total: {total_time:.2f}s")
    print(f"{'='*70}")


def main():
    """Función principal de la aplicación."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Comandos informativos (salir después de ejecutar)
    if args.list_models:
        Transcriber.list_available_models()
        sys.exit(0)
    
    if args.gpu_info:
        transcriber = Transcriber()
        info = transcriber.get_device_info()
        
        print("\nInformación del dispositivo:")
        print("=" * 70)
        for key, value in info.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        print("=" * 70)
        sys.exit(0)
    
    # Validar que se proporcionó input
    if not args.input and not args.input_dir:
        parser.print_help()
        print("\n✗ Error: Debe especificar --input o --input-dir")
        sys.exit(1)
    
    # Crear transcriptor
    print("\n" + "=" * 70)
    print("TRANSCRIPTOR DE AUDIO - WHISPER + GPU")
    print("=" * 70)
    
    transcriber = Transcriber(
        model_name=args.model,
        device=args.device,
        language=args.language,
        batch_size=args.batch_size,
        compute_type=args.compute_type,
        use_flash_attention=not args.no_flash_attention
    )
    
    # Cargar modelo
    transcriber.load_model()
    
    # Procesar archivos
    try:
        if args.input:
            # Procesar archivo individual
            process_single_file(
                transcriber=transcriber,
                input_file=args.input,
                output_path=args.output,
                output_dir=args.output_dir,
                formats=args.format,
                return_timestamps=not args.no_timestamps,
                task=args.task
            )
        
        elif args.input_dir:
            # Procesar directorio
            process_directory(
                transcriber=transcriber,
                input_dir=args.input_dir,
                output_dir=args.output_dir,
                formats=args.format,
                return_timestamps=not args.no_timestamps,
                task=args.task
            )
    
    finally:
        # Liberar modelo
        transcriber.unload_model()
    
    print("\n✓ Transcripción finalizada")


if __name__ == "__main__":
    main()
