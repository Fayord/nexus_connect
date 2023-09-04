from fastapi import FastAPI, Response
from starlette.requests import Request
from starlette.status import HTTP_200_OK
from middlewares.gateway import QueryParamsMiddleware
from schemas.chat_btl_schemas import (
    ChatRequest,
    ChatResponseModel,
    ChatHistoryResponseModel,
    DisplaySourceDataResponseModel,
)
import traceback
from modules.chatbtl_utils import (
    create_qa,
    qa_complete,
    create_logger,
    get_memory,
    load_chat_memory,
    load_db,
    load_db_api,
)
import os
import time

app = FastAPI()

# Apply the middleware
app.add_middleware(QueryParamsMiddleware)


test = None
dir_path = os.path.dirname(os.path.realpath(__file__))
# db_folder = f"{dir_path}/../db_folder"
# assert os.path.exists(db_folder), f"db_folder {db_folder} does not exist"


# Define a function to run at startup
def startup_event():
    print("FastAPI application has started!")
    global test
    test = "test"


# Register the startup event function
app.add_event_handler("startup", startup_event)


@app.get("/")
async def root():
    global test
    return {"message": f"{test}"}


@app.post(
    "/chat",
    response_model=ChatResponseModel,
    summary="Chat post endpoint",
    status_code=HTTP_200_OK,
)
async def chat_with_bot(
    request: Request, request_body: ChatRequest, response: Response
):
    # Access product_id and client_id from the request state
    product_id = request.state.product_id
    client_id = request.state.client_id
    request_id = request.state.request_id
    chat_session_id = request.state.chat_session_id
    status = "success"
    response_text = "please contact admin"
    start_time = time.time()
    # db_path = os.path.join(db_folder, product_id)
    # print(db_path)
    # print(os.path.exists(db_path))
    try:
        # db_loaded = load_db(db_path)
        db_loaded = load_db_api(product_id)
        memory = get_memory(
            client_id=client_id,
            product_id=product_id,
            chat_session_id=chat_session_id,
        )
        print("db_loaded", db_loaded)
        print(db_loaded.get()["metadatas"][:3])
        qa = create_qa(db=db_loaded, memory=memory, db_params={})
        print("load db time: {}".format(time.time() - start_time))
        logger = create_logger(
            client_id=client_id,
            product_id=product_id,
            chat_session_id=chat_session_id,
        )

        input_dict = request_body.dict()
        message = input_dict["message"]
        (
            response_text,
            source_documents_metadatas,
        ) = qa_complete(
            qa,
            message,
            logger=logger,
            client_id=client_id,
            product_id=product_id,
            chat_session_id=chat_session_id,
        )
    except Exception as e:
        print(traceback.format_exc())
        status = "fail"

    response_dict = {}
    response_dict["status"] = status
    response_dict["request_id"] = request_id

    data_dict = {}
    data_dict["message"] = response_text
    print("\n\tsource_documents_metadatas", source_documents_metadatas)
    # print("/opt/db_folder/", os.listdir("/opt/db_folder/"))
    # print("/opt/db_folder/product_a/", os.listdir("/opt/db_folder/product_a/"))
    # print("/opt/db_folder/product_a/db/", os.listdir("/opt/db_folder/product_a/db/"))
    if len(source_documents_metadatas) > 0:
        data_dict["source_data"] = source_documents_metadatas
    else:
        data_dict["source_data"] = []
    response_dict["data"] = data_dict
    return response_dict


@app.get(
    "/chat_history",
    response_model=ChatHistoryResponseModel,
    summary="Chat history get endpoint",
    status_code=HTTP_200_OK,
)
async def chat_history(request: Request, response: Response):
    # Access product_id and client_id from the request state
    product_id = request.state.product_id
    client_id = request.state.client_id
    chat_session_id = request.state.chat_session_id
    request_id = request.state.request_id

    loaded_chat_memory = load_chat_memory(client_id, product_id, chat_session_id)
    chat_history = []
    for chat in loaded_chat_memory.messages:
        chat_history.append(chat.content)
    data_dict = {}
    data_dict["chat_history"] = chat_history
    response_dict = {}
    response_dict["status"] = "success"
    response_dict["request_id"] = request_id
    response_dict["data"] = data_dict

    return response_dict


@app.get(
    "/source_data_metadata",
    response_model=DisplaySourceDataResponseModel,
    summary="source data's metadatas get endpoint",
    status_code=HTTP_200_OK,
)
async def source_data_metadata(request: Request, response: Response):
    # Access product_id and client_id from the request state
    product_id = request.state.product_id
    request_id = request.state.request_id

    data_dict = {}
    response_dict = {}
    response_dict["status"] = "success"
    response_dict["request_id"] = request_id
    response_dict["data"] = data_dict

    return response_dict
