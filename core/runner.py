import time
from .bot import ChartCapture
from .logger import get_logger
from .scheduler import ScreenshotScheduler

def on_capture_done(success: bool, filepath: str):
    """Screenshot tamamlandığında çağrılan callback."""
    logger = get_logger()
    if success:
        logger.info(f"Screenshot başarıyla kaydedildi: {filepath}")
    else:
        logger.error("Screenshot alınamadı.")

def start_app(args):
    """Uygulamayı başlatır (Tekli veya periyodik)."""
    logger = get_logger()
    try:
        # Botu context manager ile açmıyoruz çünkü scheduler thread'inde de lazım olacak
        # Bunun yerine manuel kontrol ediyoruz veya scheduler sonuna kadar açık tutuyoruz
        bot = ChartCapture(
            headless=not args.no_headless,
            theme=args.theme,
            output_dir=args.output,
            login_mode=args.login,
            width=args.width,
            height=args.height
        )
        
        if not bot.initialize():
            logger.error("Bot başlatılamadı.")
            return 1

        if args.interval > 0:
            logger.info(f"Oto-screenshot başlatıldı. Her {args.interval} dakikada bir çalışacak.")
            
            scheduler = ScreenshotScheduler()
            
            # Parametreleri hazırla
            params = {
                "bot": bot,
                "symbol": args.symbol,
                "exchange": args.exchange,
                "timeframe": args.timeframe,
                "mode": args.mode
            }
            
            # Zamanlayıcıyı başlat
            scheduler.start_schedule(
                interval_minutes=args.interval,
                callback_fn=bot.take_screenshot, # Doğrudan bot metodunu veriyoruz
                run_immediately=True,
                **{k: v for k, v in params.items() if k != "bot"} # bot zaten self olarak geçecek
            )
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                scheduler.stop_schedule()
                bot.close()
                return 0
        else:
            success, filepath = bot.take_screenshot(
                symbol=args.symbol,
                exchange=args.exchange,
                timeframe=args.timeframe,
                mode=args.mode
            )
            bot.close()
            return 0 if success else 1
            
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
