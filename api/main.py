# main.py

from fastapi import FastAPI, Request, Response
from starlette.status import HTTP_200_OK
import time
import traceback

from routes.chatbot_route import app as chatbot_app

app = FastAPI()

# Your startup event and other global variables can remain as they are in your original code.


# Register the startup event function
# Define a function to run at startup
def startup_event():
    print("FastAPI application has started!")
    global alive
    alive = "alive"


app.add_event_handler("startup", startup_event)


# Define your root endpoint
@app.get("/")
async def root():
    global alive
    return {"message": f"{alive}"}


API_PREFIX = "/api/v1"


app.mount(API_PREFIX, chatbot_app)
# Include the chatbot routes
# app.include_router(chatbot_route, prefix=API_PREFIX, tags=["chatbot"])
# app.include_router(chat_history, prefix=API_PREFIX, tags=["chatbot"])
# app.include_router(source_data_metadata, prefix=API_PREFIX, tags=["chatbot"])
