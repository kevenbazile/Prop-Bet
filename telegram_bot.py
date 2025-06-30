import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config
from database_manager import DatabaseManager
from prop_parser import PropParser
from data_fetcher import DataFetcher
from analysis_engine import AnalysisEngine

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.parser = PropParser()
        self.fetcher = DataFetcher()
        self.analyzer = AnalysisEngine()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        keyboard = [
            ['/sports', '/props'],
            ['/analyze', '/help']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        
        await update.message.reply_text(
            "🏆 Welcome to Multi-Sport Prop Bot!\\n\\n"
            "I can help you analyze sports props across MLB, NFL, NBA, and more.\\n\\n"
            "Use the commands below to get started:",
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command handler"""
        help_text = """
🤖 **Multi-Sport Prop Bot Commands**

📊 **Analysis Commands:**
/analyze - Analyze a specific prop
/props - Get today's best props  
/sports - List supported sports

📝 **How to use:**
1. Send me prop text like: "Mike Trout Over 1.5 Hits +120"
2. I'll parse and analyze it automatically
3. Get detailed analysis and recommendations

🏈 **Supported Sports:**
• MLB (Baseball)
• NFL (Football) 
• NBA (Basketball)
• NHL (Hockey)
• Soccer
• Tennis

💡 **Tips:**
- Send multiple props at once (one per line)
- Include odds when available
- Use standard formats like "Player Over/Under X.X Stat +/-XXX"
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def sports_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sports command handler"""
        sports_text = "🏆 **Supported Sports:**\\n\\n"
        
        for sport_code, sport_info in Config.SUPPORTED_SPORTS.items():
            sports_text += f"**{sport_code}** - {sport_info['name']}\\n"
            sports_text += f"Props: {', '.join(sport_info['prop_types'])}\\n\\n"
        
        await update.message.reply_text(sports_text, parse_mode='Markdown')
    
    async def props_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Props command handler"""
        # Get recommended props from database
        recommended_props = self.db.get_recommended_props()
        
        if recommended_props.empty:
            await update.message.reply_text(
                "📊 No analyzed props available yet.\\n\\n"
                "Send me some prop data to analyze!"
            )
            return
        
        props_text = "🔥 **Today's Best Props:**\\n\\n"
        
        for _, prop in recommended_props.head(5).iterrows():
            confidence = prop['confidence_score'] * 100
            props_text += f"**{prop['player_name']}** ({prop['sport']})\\n"
            props_text += f"{prop['prop_type'].title()}: {prop['line_value']}\\n"
            props_text += f"Confidence: {confidence:.1f}%\\n"
            props_text += f"Recommendation: {prop['recommendation']}\\n\\n"
        
        await update.message.reply_text(props_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages (prop analysis)"""
        message_text = update.message.text
        
        # Parse the prop(s)
        props = self.parser.parse_manual_input(message_text)
        
        if not props:
            await update.message.reply_text(
                "❌ I couldn't parse that prop format.\\n\\n"
                "Try something like: 'Mike Trout Over 1.5 Hits +120'"
            )
            return
        
        await update.message.reply_text(f"🔍 Analyzing {len(props)} prop(s)...")
        
        results = []
        for prop in props:
            # Add to database
            prop_id = self.db.add_prop(prop)
            prop['id'] = prop_id
            
            # Fetch player stats
            player_stats = self.fetcher.fetch_player_stats(
                prop['player_name'], 
                prop['sport']
            )
            
            # Analyze the prop
            analysis = self.analyzer.analyze_prop(prop, player_stats)
            results.append(analysis)
            
            # Update database with analysis
            self.db.update_prop_analysis(prop_id, {
                'recommended': analysis.get('recommendation') in ['STRONG_BET', 'MODERATE_BET'],
                'confidence_score': analysis.get('confidence_score', 0),
                'expected_value': 0  # Placeholder
            })
        
        # Send results
        await self.send_analysis_results(update, results)
    
    async def send_analysis_results(self, update: Update, results: list):
        """Send analysis results to user"""
        for analysis in results:
            if 'error' in analysis:
                await update.message.reply_text(f"❌ Analysis error: {analysis['error']}")
                continue
            
            confidence = analysis['confidence_score'] * 100
            recommendation = analysis['recommendation']
            
            # Emoji based on recommendation
            emoji_map = {
                'STRONG_BET': '🔥',
                'MODERATE_BET': '👍',
                'WEAK_BET': '🤔',
                'AVOID': '❌'
            }
            emoji = emoji_map.get(recommendation, '📊')
            
            result_text = f"""
{emoji} **Analysis Complete**

**Player:** {analysis['player_name']}
**Prop:** {analysis['prop_type'].title()} {analysis['line_value']}
**Sport:** {analysis.get('sport', 'Unknown')}

**📊 Results:**
• Confidence: {confidence:.1f}%
• Recommendation: {recommendation}

**💡 Analysis Notes:**
Based on available player statistics and recent performance trends.
            """
            
            await update.message.reply_text(result_text, parse_mode='Markdown')
    
    def run(self):
        """Run the telegram bot"""
        # Create application
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("sports", self.sports_command))
        application.add_handler(CommandHandler("props", self.props_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Run the bot
        print("🤖 Starting Telegram Bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main entry point for telegram bot"""
    bot = TelegramBot()
    bot.run()

if __name__ == '__main__':
    main()
