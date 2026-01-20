import time
import schedule
from .bot import ChartCapture
from .logger import get_logger

def run_single_screenshot(bot: ChartCapture, args) -> int:
    """Tek sembol için screenshot alır."""
    logger = get_logger()
    success, filepath = bot.take_screenshot(
        symbol=args.symbol,
        exchange=args.exchange,
        timeframe=args.timeframe,
        mode=args.mode
    )
    if success:
        logger.info(f"Screenshot kaydedildi: {filepath}")
    return 0 if success else 1

def start_app(args):
    """Uygulamayı başlatır (Tekli veya periyodik)."""
    logger = get_logger()
    try:
        with ChartCapture(
            headless=not args.no_headless,
            theme=args.theme,
            output_dir=args.output,
            login_mode=args.login,
            width=args.width,
            height=args.height
        ) as bot:
            if args.interval > 0:
                logger.info(f"Oto-screenshot başlatıldı. Her {args.interval} dakikada bir çalışacak.")
                run_single_screenshot(bot, args) # İlkini hemen al
                schedule.every(args.interval).minutes.do(run_single_screenshot, bot, args)
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            else:
                return run_single_screenshot(bot, args)
    except KeyboardInterrupt:
        logger.warning("İşlem kullanıcı tarafından iptal edildi.")
        return 130
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        return 1
