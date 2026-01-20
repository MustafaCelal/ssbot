#!/usr/bin/env python3
"""
ChartCapture Pro - Giriş Noktası
"""
import sys
from core.cli import parse_arguments
from core.runner import start_app

def main():
    # 1. Argümanları oku
    args = parse_arguments()
    
    # 2. Çalıştır ve sonucu dön
    exit_code = start_app(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
