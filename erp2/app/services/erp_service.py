import grpc
import logging
import asyncio
from datetime import date, datetime, timedelta
from concurrent import futures
import os

# Import generated gRPC code
from app.protos import erp_service_pb2, erp_service_pb2_grpc

# Import our models and CRUD operations
from app.models.crud import get_product, create_order, update_order_status
from app.models.pydantic_models import OrderCreate, OrderUpdate, OrderStatus
from app.producers.status_producer import send_status_update

# Import logging client
from shared.logging.log_client import SystemInteractionLogger

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'erp_service.log'))
    ]
)
logger = logging.getLogger("erp2.service")

# Initialize logger client
log_client = SystemInteractionLogger(
    service_name="erp2",
    rabbitmq_url=os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/"),
    local_fallback_path="logs/local_system_logs.log"
)

class ERPServiceServicer(erp_service_pb2_grpc.ERPServiceServicer):
    """
    Implementation of the ERPService gRPC service.
    
    Handles order processing and product stock queries.
    """
    
    async def ProcessOrder(self, request, context):
        """
        Process an incoming order.
        
        1. Check if product exists and has enough stock
        2. Create order record
        3. Update product stock
        4. Return shipping date and status
        5. Send status update via RabbitMQ (asynchronous)
        """
        logger.info(f"Processing order: {request.order_id} for product {request.product_id}")
        
        try:
            # Log the incoming request
            await log_client.log_interaction(
                target_system="ecommerce",
                interaction_type="gRPC",
                message={
                    "order_id": request.order_id,
                    "customer_id": request.customer_id,
                    "product_id": request.product_id,
                    "quantity": request.quantity
                },
                status="success"
            )
            
            # Create order using our CRUD operations
            order_data = OrderCreate(
                order_id=request.order_id,
                customer_id=request.customer_id,
                product_id=request.product_id,
                quantity=request.quantity
            )
            
            order = await create_order(order_data)
            
            # Prepare response
            shipping_date_str = ""
            if order.shipping_date:
                shipping_date_str = order.shipping_date.isoformat()
                
            order_status_str = order.order_status.value
                
            # Send status update via RabbitMQ (asynchronously)
            asyncio.create_task(send_status_update_wrapper(request.order_id, order_status_str))
                
            return erp_service_pb2.OrderResponse(
                order_id=request.order_id,
                shipping_date=shipping_date_str,
                order_status=order_status_str
            )
            
        except Exception as e:
            error_message = f"Error processing order: {str(e)}"
            logger.error(error_message)
            
            # Log the failed interaction
            await log_client.log_interaction(
                target_system="ecommerce",
                interaction_type="gRPC",
                message={
                    "order_id": request.order_id,
                    "error": str(e)
                },
                status="error",
                error_message=error_message
            )
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_message)
            return erp_service_pb2.OrderResponse()
    
    async def GetProductStock(self, request, context):
        """
        Get product stock information.
        """
        logger.info(f"Checking stock for product: {request.product_id}")
        
        try:
            product = await get_product(request.product_id)
            
            if not product:
                error_message = f"Product {request.product_id} not found."
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(error_message)
                return erp_service_pb2.ProductResponse()
                
            return erp_service_pb2.ProductResponse(
                product_id=product.product_id,
                product_name=product.product_name,
                stock_level=product.stock_level,
                retail_price=float(product.retail_price)
            )
            
        except Exception as e:
            error_message = f"Error getting product: {str(e)}"
            logger.error(error_message)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_message)
            return erp_service_pb2.ProductResponse()

# Helper function for asynchronous status updates
async def send_status_update_wrapper(order_id, status):
    """Wrapper to call the send_status_update function from our async context."""
    from app.producers.status_producer import send_status_update
    send_status_update(order_id, status)

def start_grpc_server():
    """
    Start the gRPC server in a separate thread.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    erp_service_pb2_grpc.add_ERPServiceServicer_to_server(
        ERPServiceServicer(), server
    )
    
    # Get server host and port from environment or use defaults
    host = os.getenv("GRPC_HOST", "0.0.0.0")
    port = os.getenv("GRPC_PORT", "50051")
    server_addr = f"{host}:{port}"
    
    # Add insecure port for now (in production, you'd want SSL)
    server.add_insecure_port(server_addr)
    server.start()
    
    logger.info(f"gRPC server started on {server_addr}")
    
    return server