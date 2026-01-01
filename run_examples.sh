#!/bin/bash
# Script de ejemplo para facilitar el uso de la aplicación de transcripción

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   TRANSCRIPTOR DE AUDIO - EJEMPLOS${NC}"
echo -e "${BLUE}========================================${NC}"

# Activar entorno virtual
source .venv/bin/activate

# Función para mostrar ejemplos
show_examples() {
    echo -e "\n${GREEN}Ejemplos de uso:${NC}\n"
    
    echo -e "${YELLOW}1. Transcripción básica:${NC}"
    echo "   python main.py --input audio.mp3"
    
    echo -e "\n${YELLOW}2. Con modelo específico:${NC}"
    echo "   python main.py --input audio.mp3 --model medium"
    
    echo -e "\n${YELLOW}3. Generar subtítulos:${NC}"
    echo "   python main.py --input audio.mp3 --format srt"
    
    echo -e "\n${YELLOW}4. Procesamiento batch:${NC}"
    echo "   python main.py --input-dir ./input --output-dir ./output"
    
    echo -e "\n${YELLOW}5. Múltiples formatos:${NC}"
    echo "   python main.py --input audio.mp3 --format txt json srt"
    
    echo -e "\n${YELLOW}6. Ver modelos disponibles:${NC}"
    echo "   python main.py --list-models"
    
    echo -e "\n${YELLOW}7. Ver información de GPU:${NC}"
    echo "   python main.py --gpu-info"
}

# Función para verificación rápida
quick_check() {
    echo -e "\n${GREEN}Verificación rápida del sistema:${NC}\n"
    
    echo -e "${YELLOW}GPU:${NC}"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    
    echo -e "\n${YELLOW}Python:${NC}"
    python --version
    
    echo -e "\n${YELLOW}PyTorch CUDA:${NC}"
    python -c "import torch; print(f'CUDA disponible: {torch.cuda.is_available()}')"
    
    echo -e "\n${YELLOW}FFmpeg:${NC}"
    ffmpeg -version | head -n 1
}

# Procesar argumentos
case "$1" in
    "check")
        quick_check
        ;;
    "examples")
        show_examples
        ;;
    "help")
        python main.py --help
        ;;
    "models")
        python main.py --list-models
        ;;
    "gpu")
        python scripts/check_gpu.py
        ;;
    *)
        show_examples
        echo -e "\n${GREEN}Comandos disponibles en este script:${NC}"
        echo "  ./run_examples.sh check     - Verificación rápida del sistema"
        echo "  ./run_examples.sh examples  - Mostrar ejemplos de uso"
        echo "  ./run_examples.sh help      - Ayuda completa de la aplicación"
        echo "  ./run_examples.sh models    - Listar modelos disponibles"
        echo "  ./run_examples.sh gpu       - Verificación detallada de GPU"
        ;;
esac

echo ""

