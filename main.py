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
  
  # Batch screenshot
  python main.py --symbols BTCUSDT,ETHUSDT,SOLUSDT --exchange BINANCE
  
  # Multi-timeframe
  python main.py --symbol BTCUSDT --exchange BINANCE --timeframes 1H,4H,1D
  
  # Light theme, headed mod
  python main.py --symbol AAPL --exchange NASDAQ --theme light --no-headless
        """
    )
    
    # Sembol seçenekleri
    symbol_group = parser.add_mutually_exclusive_group(required=True)
    symbol_group.add_argument(
        "--symbol", "-s",
        type=str,
        help="Tek sembol (ör: BTCUSDT)"
    )
    symbol_group.add_argument(
        "--symbols",
        type=str,
        help="Çoklu sembol (virgülle ayrılmış, ör: BTCUSDT,ETHUSDT)"
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
    
    parser.add_argument(
        "--timeframes",
        type=str,
        help="Çoklu timeframe (virgülle ayrılmış, ör: 1H,4H,1D)"
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
    
    if args.timeframes:
        # Multi-timeframe
        timeframes = [tf.strip() for tf in args.timeframes.split(",")]
        logger.info(f"Multi-timeframe screenshot: {args.symbol} @ {timeframes}")
        
        results = bot.batch_screenshot_multi_timeframe(
            symbols=[args.symbol],
            exchange=args.exchange,
            timeframes=timeframes
        )
        
        # Sonuçları kontrol et
        all_success = all(
            success for tf_results in results.values() 
            for success, _ in tf_results.values()
        )
    else:
        # Single timeframe
        success, filepath = bot.take_screenshot(
            symbol=args.symbol,
            exchange=args.exchange,
            timeframe=args.timeframe
        )
        all_success = success
        
        if success:
            logger.info(f"Screenshot kaydedildi: {filepath}")
    
    return 0 if all_success else 1


def run_batch_screenshot(bot: TradingViewBot, args: argparse.Namespace) -> int:
    """
    Batch screenshot alır.
    
    Returns:
        Exit code
    """
    logger = get_logger()
    
    symbols = [s.strip() for s in args.symbols.split(",")]
    logger.info(f"Batch screenshot: {len(symbols)} sembol")
    
    if args.timeframes:
        timeframes = [tf.strip() for tf in args.timeframes.split(",")]
        results = bot.batch_screenshot_multi_timeframe(
            symbols=symbols,
            exchange=args.exchange,
            timeframes=timeframes
        )
    else:
        results = bot.batch_screenshot(
            symbols=symbols,
            exchange=args.exchange,
            timeframe=args.timeframe
        )
    
    stats = bot.get_stats()
    return 0 if stats["failed"] == 0 else 1


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
            
            if args.symbol:
                return run_single_screenshot(bot, args)
            else:
                return run_batch_screenshot(bot, args)
                
    except KeyboardInterrupt:
        logger.warning("İşlem kullanıcı tarafından iptal edildi.")
        return 130
        
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
