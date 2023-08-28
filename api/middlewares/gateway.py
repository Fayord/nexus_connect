from starlette.middleware.base import BaseHTTPMiddleware
import uuid


class QueryParamsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Directly get the product_id and client_id from the query parameters
        client_id = request.headers.get("X-Client-ID")
        product_id = request.headers.get("X-Product-ID")
        chat_session_id = request.headers.get("X-Chat-Session-ID")
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        # Save the product_id and client_id in the request state
        request.state.product_id = product_id
        request.state.client_id = client_id
        request.state.chat_session_id = chat_session_id
        request.state.request_id = request_id
        return await call_next(request)
