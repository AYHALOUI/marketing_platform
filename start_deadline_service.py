# start_deadline_service.py - Script to start the deadline monitoring service

import os
import sys
import logging
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deadline_service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to start the deadline service"""
    try:
        logger.info("=" * 60)
        logger.info("🚀 STARTING DEADLINE MONITORING SERVICE")
        logger.info("=" * 60)
        
        # Import the deadline monitor
        from routes.deadline_monitor import EnhancedDeadlineMonitor
        
        # Check if N8N is running
        from services.n8n_service import check_n8n_health
        
        n8n_health = check_n8n_health()
        logger.info(f"🔍 N8N Health Check: {n8n_health['status']}")
        
        if n8n_health['status'] != 'healthy':
            logger.warning("⚠️ N8N service is not healthy, but continuing with deadline monitoring")
            logger.warning(f"N8N Status: {n8n_health.get('error', 'Unknown error')}")
        
        # Create and start the deadline monitor
        logger.info("🔧 Initializing Enhanced Deadline Monitor...")
        monitor = EnhancedDeadlineMonitor()
        
        # Run initial check
        logger.info("📋 Running initial deadline check...")
        monitor.run_once()
        
        # Start continuous monitoring
        logger.info("⏰ Starting continuous deadline monitoring...")
        logger.info("📧 Email notifications will be sent for:")
        logger.info("   • Tasks due tomorrow (urgent)")
        logger.info("   • Tasks due in 3 days (high priority)")
        logger.info("   • Tasks due in 1 week (medium priority)")
        logger.info("   • Overdue tasks (critical)")
        logger.info("   • Project deadlines approaching")
        
        logger.info("🔄 Schedule:")
        logger.info("   • Full checks: 9:00 AM and 5:00 PM daily")
        logger.info("   • Overdue checks: Every 2 hours")
        
        logger.info("=" * 60)
        logger.info("✅ DEADLINE MONITORING SERVICE STARTED")
        logger.info("Press Ctrl+C to stop the service")
        logger.info("=" * 60)
        
        # This will run indefinitely
        monitor.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("🛑 SHUTDOWN REQUESTED BY USER")
        logger.info("=" * 60)
        logger.info("💾 Saving any pending data...")
        logger.info("✅ Deadline monitoring service stopped gracefully")
        sys.exit(0)
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error("❌ CRITICAL ERROR IN DEADLINE SERVICE")
        logger.error("=" * 60)
        logger.error(f"Error: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == '__main__':
    main()