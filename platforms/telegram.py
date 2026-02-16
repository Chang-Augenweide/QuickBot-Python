"""
QuickBot - Telegram Platform Integration
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from agent import QuickBot

logger = logging.getLogger(__name__)


class TelegramPlatform:
    """Telegram bot integration."""
    
    def __init__(self, bot: QuickBot, token: str, allowed_users: Optional[list] = None):
        self.bot = bot
        self.token = token
        self.allowed_users = allowed_users or []
        self._bot_instance = None
        self._running = False
    
    async def _get_bot(self):
        """Lazy initialize Telegram bot."""
        if self._bot_instance is None:
            try:
                from telegram import Bot
                self._bot_instance = Bot(token=self.token)
            except ImportError:
                raise ImportError("python-telegram-bot package not installed. Run: pip install python-telegram-bot")
        return self._bot_instance
    
    def _is_user_allowed(self, user_id: str) -> bool:
        """Check if user is allowed to interact with the bot."""
        if not self.allowed_users:
            return True  # Allow all if whitelist is empty
        return user_id in self.allowed_users
    
    async def start(self) -> None:
        """Start the Telegram bot."""
        if self._running:
            return
        
        try:
            from telegram.ext import Application, MessageHandler, filters, CommandHandler
            
            bot = await self._get_bot()
            application = Application.builder().token(self.token).build()
            
            # Message handler
            async def handle_message(update, context):
                if not update.message or not update.message.from_user:
                    return
                
                user_id = str(update.message.from_user.id)
                
                if not self._is_user_allowed(user_id):
                    logger.warning(f"Unauthorized user: {user_id}")
                else:
                    session_id = f"telegram:{user_id}"
                    message_text = update.message.text
                    
                    try:
                        response = await self.bot.process_message(
                            session_id=session_id,
                            message=message_text,
                            platform='telegram',
                            user_id=user_id,
                            metadata={'first_name': update.message.from_user.first_name}
                        )
                        
                        await update.message.reply_text(response)
                    
                    except Exception as e:
                        logger.error(f"Error handling message: {e}")
                        await update.message.reply_text("Sorry, I encountered an error.")
            
            # Command handlers
            async def start_command(update, context):
                user_id = str(update.message.from_user.id)
                session_id = f"telegram:{user_id}"
                
                await update.message.reply_text(
                    f"👋 Hi! I'm {self.bot.config.get('bot.name', 'QuickBot')}!\n\n"
                    f"Send /help to see available commands.\n\n"
                    f"Just chat with me naturally!"
                )
            
            async def help_command(update, context):
                help_text = self.bot._get_help_message()
                await update.message.reply_text(help_text)
            
            async def status_command(update, context):
                status_text = self.bot._get_status_message()
                await update.message.reply_text(status_text)
            
            # Register handlers
            application.add_handler(CommandHandler("start", start_command))
            application.add_handler(CommandHandler("help", help_command))
            application.add_handler(CommandHandler("status", status_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            
            self._running = True
            logger.info("Telegram bot started")
            
            # Start polling
            await application.initialize()
            await application.start()
            await application.updater.start_polling(drop_pending_updates=True)
            
        except Exception as e:
            logger.error(f"Error starting Telegram bot: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the Telegram bot."""
        if self._bot_instance and hasattr(self._bot_instance, 'application'):
            await self._bot_instance.application.stop()
        
        self._running = False
        logger.info("Telegram bot stopped")
