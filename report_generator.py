from datetime import datetime
from database_manager import DatabaseManager

class ReportGenerator:
    def __init__(self):
        self.db = DatabaseManager()
    
    def generate_daily_report(self):
        today = datetime.now().strftime('%Y-%m-%d')
        props_df = self.db.get_recommended_props()
        
        if props_df.empty:
            return f"📊 Daily Report - {today}\n\nNo props analyzed today."
        
        total_props = len(props_df)
        
        report = f"""📊 Daily Prop Analysis Report
📅 Date: {today}

📈 Summary:
• Total Props Analyzed: {total_props}
• System Status: ✅ Operational

🔥 Recent Analysis Available
"""
        return report
