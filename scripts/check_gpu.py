#!/usr/bin/env python3
"""
Script de verificación de GPU y CUDA para la aplicación de transcripción.
Verifica que PyTorch puede acceder a la GPU y muestra información relevante.
"""

import sys


def check_gpu():
    """Verifica la disponibilidad y configuración de GPU/CUDA."""
    
    print("=" * 70)
    print("VERIFICACIÓN DE GPU Y CUDA")
    print("=" * 70)
    
    # Importar PyTorch
    try:
        import torch
        print(f"\n✓ PyTorch instalado correctamente")
        print(f"  Versión: {torch.__version__}")
    except ImportError as e:
        print(f"\n✗ Error al importar PyTorch: {e}")
        return False
    
    # Verificar disponibilidad de CUDA
    cuda_available = torch.cuda.is_available()
    print(f"\n{'✓' if cuda_available else '✗'} CUDA disponible: {cuda_available}")
    
    if not cuda_available:
        print("\n⚠ CUDA no está disponible. La transcripción usará CPU (más lento).")
        print("  Verifica la instalación de drivers NVIDIA y PyTorch con CUDA.")
        return False
    
    # Información de CUDA
    print(f"\n✓ Versión de CUDA: {torch.version.cuda}")
    print(f"✓ cuDNN disponible: {torch.backends.cudnn.is_available()}")
    print(f"  Versión cuDNN: {torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else 'N/A'}")
    
    # Información de GPU(s)
    num_gpus = torch.cuda.device_count()
    print(f"\n✓ Número de GPUs detectadas: {num_gpus}")
    
    for i in range(num_gpus):
        print(f"\n  GPU {i}:")
        print(f"    Nombre: {torch.cuda.get_device_name(i)}")
        print(f"    Compute Capability: {torch.cuda.get_device_capability(i)}")
        
        # Memoria GPU
        total_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
        print(f"    Memoria Total: {total_memory:.2f} GB")
        
        # Memoria disponible actualmente
        torch.cuda.set_device(i)
        allocated = torch.cuda.memory_allocated(i) / (1024**3)
        reserved = torch.cuda.memory_reserved(i) / (1024**3)
        print(f"    Memoria Asignada: {allocated:.2f} GB")
        print(f"    Memoria Reservada: {reserved:.2f} GB")
        print(f"    Memoria Disponible: {total_memory - reserved:.2f} GB")
    
    # Test de operación en GPU
    print("\n" + "=" * 70)
    print("TEST DE OPERACIÓN EN GPU")
    print("=" * 70)
    
    try:
        # Crear tensor en GPU y realizar operación
        device = torch.device("cuda:0")
        x = torch.randn(1000, 1000, device=device)
        y = torch.randn(1000, 1000, device=device)
        
        # Operación matricial
        import time
        start = time.time()
        z = torch.matmul(x, y)
        torch.cuda.synchronize()  # Esperar a que termine la operación
        elapsed = time.time() - start
        
        print(f"\n✓ Operación matricial (1000x1000) completada")
        print(f"  Tiempo: {elapsed*1000:.2f} ms")
        print(f"  Resultado en GPU: {z.device}")
        
        # Limpiar memoria
        del x, y, z
        torch.cuda.empty_cache()
        
    except Exception as e:
        print(f"\n✗ Error durante test de GPU: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✓ VERIFICACIÓN COMPLETADA - GPU LISTA PARA TRANSCRIPCIÓN")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    success = check_gpu()
    sys.exit(0 if success else 1)


