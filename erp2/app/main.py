import asyncio
import logging
import os
import signal
import sys

# Import our modules
from app.models.db_models import init_db
from app.models.crud import initialize_demo_data
from app.services.erp_service import start_grpc_server

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'erp2_main.log'))
    ]
)
logger = logging.getLogger("erp2.main")

async def startup():
    """Initialize the application on startup."""
    logger.info("Starting ERP2 system...")
    
    # Initialize database
    try:
        logger.info("Initializing database...")
        await init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        sys.exit(1)
    
    # Initialize demo data
    try:
        logger.info("Creating demo data...")
        await initialize_demo_data()
    except Exception as e:
        logger.warning(f"Failed to create demo data: {str(e)}")
    
    logger.info("ERP2 system started successfully")

def shutdown(server):
    """Handle graceful shutdown."""
    logger.info("Shutting down ERP2 system...")
    
    if server:
        server.stop(None)  # None means stop immediately
        logger.info("gRPC server stopped")
    
    logger.info("ERP2 system shutdown complete")

async def main():
    """Main application entry point."""
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    
    # Initialize application
    await startup()
    
    # Start gRPC server
    server = start_grpc_server()
    
    # Register signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: shutdown(server))
    
    try:
        # Keep the app running
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
    except asyncio.CancelledError:
        # Handle cancellation
        shutdown(server)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)