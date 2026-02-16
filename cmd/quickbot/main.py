"""
QuickBot - Lightweight Personal AI Assistant
Main Entry Point
"""
import asyncio
import signal
import logging
import sys
from pathlib import Path

from agent import QuickBot
from telegram_platform import TelegramPlatform

logger = logging.getLogger(__name__)


class QuickBotRunner:
    """Runner for QuickBot with graceful shutdown."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.bot = None
        self.platforms = []
        self._shutdown_event = asyncio.Event()
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self._shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self) -> None:
        """Run QuickBot."""
        try:
            # Initialize bot
            logger.info("Initializing QuickBot...")
            self.bot = QuickBot(config_path=self.config_path)
            
            # Start bot
            await self.bot.start()
            
            # Initialize platforms
            await self._initialize_platforms()
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
            logger.info("QuickBot is running! Press Ctrl+C to stop.")
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
        
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)
        
        finally:
            logger.info("Shutting down QuickBot...")
            await self._shutdown()
    
    async def _initialize_platforms(self) -> None:
        """Initialize enabled platforms."""
        platforms_config = self.bot.config.get('platforms', {})
        
        # Telegram
        if platforms_config.get('telegram', {}).get('enabled', False):
            telegram_config = platforms_config['telegram']
            token = telegram_config.get('token', '')
            allowed_users = telegram_config.get('allowed_users', [])
            
            if token:
                try:
                    telegram = TelegramPlatform(
                        bot=self.bot,
                        token=token,
                        allowed_users=allowed_users
                    )
                    await telegram.start()
                    self.platforms.append(telegram)
                    logger.info("✓ Telegram platform initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Telegram: {e}")
            
        # Discord (placeholder)
        if platforms_config.get('discord', {}).get('enabled', False):
            logger.info("Discord platform enabled but not implemented yet")
        
        # Slack (placeholder)
        if platforms_config.get('slack', {}).get('enabled', False):
            logger.info("Slack platform enabled but not implemented yet")
    
    async def _shutdown(self) -> None:
        """Shutdown all components."""
        # Stop platforms
        for platform in self.platforms:
            try:
                await platform.stop()
            except Exception as e:
                logger.error(f"Error stopping platform: {e}")
        
        # Stop bot
        if self.bot:
            try:
                await self.bot.stop()
            except Exception as e:
                logger.error(f"Error stopping bot: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='QuickBot - Lightweight Personal AI Assistant')
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize configuration file'
    )
    
    args = parser.parse_args()
    
    # Initialize config if requested
    if args.init:
        from config import Config
        config = Config(args.config)
        print(f"✓ Configuration initialized at {args.config}")
        print(f"✓ Please edit {args.config} to set your API keys and settings")
        return
    
    # Run bot
    runner = QuickBotRunner(config_path=args.config)
    
    try:
        asyncio.run(runner.run())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")


if __name__ == '__main__':
    main()
