#!/usr/bin/env python3
"""
TradingView Screenshot Bot - Main Entry Point
CLI arayüzü ve örnek kullanımlar.
"""

import argparse
import sys
from typing import List

from tradingview_bot import TradingViewBot
from config import SUPPORTED_EXCHANGES, Timeframe
from logger import get_logger


def parse_arguments() -> argparse.Namespace:
    """
    CLI argümanlarını parse eder.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="TradingView Screenshot Bot - Otomatik chart screenshot aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  # Tekli screenshot
  python main.py --symbol BTCUSDT --exchange BINANCE --timeframe 1D
  
  # Light theme, headed mod
  python main.py --symbol AAPL --exchange NASDAQ --theme light --no-headless
        """
    )
    
    # Sembol seçeneği
    parser.add_argument(
        "--symbol", "-s",
        type=str,
        required=True,
        help="Sembol adı (ör: BTCUSDT)"
    )
    
    # Borsa
    parser.add_argument(
        "--exchange", "-e",
        type=str,
        default="BINANCE",
        choices=SUPPORTED_EXCHANGES,
        help="Borsa adı (default: BINANCE)"
    )
    
    # Timeframe
    parser.add_argument(
        "--timeframe", "-t",
        type=str,
        default="1D",
        help="Zaman dilimi (ör: 1H, 4H, 1D, 1W)"
    )
    
    # Görünüm
    parser.add_argument(
        "--theme",
        type=str,
        choices=["light", "dark"],
        default="dark",
        help="Tema seçimi (default: dark)"
    )
    
    # Browser modu
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Browser'ı görünür modda çalıştır"
    )
    
    # Login
    parser.add_argument(
        "--login",
        action="store_true",
        help="TradingView'a giriş yap (TV_USERNAME, TV_PASSWORD env vars gerekli)"
    )
    
    # Çıktı
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Screenshot çıktı klasörü (default: ./screenshots)"
    )
    
    return parser.parse_args()


def run_single_screenshot(bot: TradingViewBot, args: argparse.Namespace) -> int:
    """
    Tek sembol için screenshot alır.
    
    Returns:
        Exit code (0: success, 1: failure)
    """
    logger = get_logger()
    
    # Single timeframe
    success, filepath = bot.take_screenshot(
        symbol=args.symbol,
        exchange=args.exchange,
        timeframe=args.timeframe
    )
    
    if success:
        logger.info(f"Screenshot kaydedildi: {filepath}")
    
    return 0 if success else 1


def main() -> int:
    """
    Ana çalıştırma fonksiyonu.
    
    Returns:
        Exit code
    """
    args = parse_arguments()
    logger = get_logger()
    
    try:
        # Bot'u oluştur
        with TradingViewBot(
            headless=not args.no_headless,
            theme=args.theme,
            output_dir=args.output,
            login_mode=args.login
        ) as bot:
            
            return run_single_screenshot(bot, args)
                
    except KeyboardInterrupt:
        logger.warning("İşlem kullanıcı tarafından iptal edildi.")
        return 130
        
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
