from fastapi import FastAPI, Response
from starlette.requests import Request
from starlette.status import HTTP_200_OK
from fastapi.responses import JSONResponse

from middlewares.gateway import QueryParamsMiddleware
from schemas.chat_btl_schemas import (
    ChatRequest,
    ChatResponseModel,
    ChatHistoryResponseModel,
    DisplaySourceDataResponseModel,
)
from schemas.database_schemas import (
    AddDataTextRequest,
    AddDataFileRequest,
    AddDataWebsiteRequest,
    AddDataTextResponse,
    AddDataFileResponse,
    AddDataWebsiteResponse,
    ClearDataRequest,
    ClearDataResponse,
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
    get_memory_agents,
    create_agent_executor,
    agents_complete,
    get_initial_message,
    add_data_text_to_db,
    add_data_file_to_db,
    add_data_website_to_db,
    clear_data_db,
)
import os
import time

app = FastAPI()

# Apply the middleware
app.add_middleware(QueryParamsMiddleware)

# dir_path = os.path.dirname(os.path.realpath(__file__))
# db_folder = f"{dir_path}/../db_folder"
# assert os.path.exists(db_folder), f"db_folder {db_folder} does not exist"


@app.post(
    "/chat",
    response_model=ChatResponseModel,
    summary="Chat post endpoint",
    status_code=HTTP_200_OK,
)
async def chat_with_bot_api(
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
    source_documents_metadatas = []
    try:
        # db_loaded = load_db(db_path)
        db_loaded = load_db_api(product_id)
        memory = get_memory_agents(
            client_id=client_id,
            product_id=product_id,
            chat_session_id=chat_session_id,
        )
        print("db_loaded", db_loaded)
        # print(db_loaded.get()["metadatas"][:3])
        executor = create_agent_executor(db=db_loaded, memory=memory)
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
        ) = agents_complete(
            executor,
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
    if len(source_documents_metadatas) > 0:
        data_dict["source_data"] = source_documents_metadatas
    else:
        data_dict["source_data"] = []
    response_dict["data"] = data_dict
    return response_dict


@app.post(
    # "/chat",
    "/chat_old",
    response_model=ChatResponseModel,
    summary="Chat post endpoint",
    status_code=HTTP_200_OK,
)
async def chat_with_bot_api(
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
async def chat_history_api(request: Request, response: Response):
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
async def source_data_metadata_api(request: Request, response: Response):
    # Access product_id and client_id from the request state
    product_id = request.state.product_id
    request_id = request.state.request_id

    data_dict = {}
    response_dict = {}
    response_dict["status"] = "success"
    response_dict["request_id"] = request_id
    response_dict["data"] = data_dict

    return response_dict


@app.get(
    "/get_initial_message",
    response_model=ChatResponseModel,
    summary="get initial message",
    status_code=HTTP_200_OK,
)
async def get_initial_message_api(request: Request, response: Response):
    product_id = request.state.product_id
    client_id = request.state.client_id
    request_id = request.state.request_id
    status = "success"
    initial_message = get_initial_message(product_id, client_id)
    response_text = initial_message
    response_dict = {}
    response_dict["status"] = status
    response_dict["request_id"] = request_id

    data_dict = {}
    data_dict["message"] = response_text
    data_dict["source_data"] = []
    response_dict["data"] = data_dict
    return response_dict


def handle_add_data_request(
    product_id,
    client_id,
    request_id,
    knowledge_name,
    request_body,
    add_data_function,
):
    status = "success"
    response_text = f"add data {add_data_function.__name__} success"

    is_success, error_message = add_data_function(
        product_id, client_id, knowledge_name, request_body
    )

    if not is_success:
        status = "fail"
        response_text = f"add data {add_data_function.__name__} fail"

    response_dict = {
        "status": status,
        "request_id": request_id,
        "data": {"message": response_text},
    }
    if status == "fail":
        response_dict["error"] = [{"object": "error", "detail": error_message}]
        # return with Http 500
        return JSONResponse(status_code=500, content=response_dict)

    return response_dict


@app.post(
    "/add_data_text",
    response_model=AddDataTextResponse,
    summary="add data text",
    status_code=HTTP_200_OK,
)
async def add_data_text_api(
    request: Request, request_body: AddDataTextRequest, response: Response
):
    product_id = request.state.product_id
    client_id = request.state.client_id
    request_id = request.state.request_id
    return handle_add_data_request(
        product_id,
        client_id,
        request_id,
        request_body.knowledge_name,
        request_body.text,
        add_data_text_to_db,
    )


@app.post(
    "/add_data_file",
    response_model=AddDataFileResponse,
    summary="add data file",
    status_code=HTTP_200_OK,
)
async def add_data_file_api(
    request: Request, request_body: AddDataFileRequest, response: Response
):
    product_id = request.state.product_id
    client_id = request.state.client_id
    request_id = request.state.request_id
    return handle_add_data_request(
        product_id,
        client_id,
        request_id,
        request_body.knowledge_name,
        request_body.file,
        add_data_file_to_db,
    )


@app.post(
    "/add_data_website",
    response_model=AddDataWebsiteResponse,
    summary="add data website",
    status_code=HTTP_200_OK,
)
async def add_data_website_api(
    request: Request, request_body: AddDataWebsiteRequest, response: Response
):
    product_id = request.state.product_id
    client_id = request.state.client_id
    request_id = request.state.request_id
    return handle_add_data_request(
        product_id,
        client_id,
        request_id,
        request_body.knowledge_name,
        request_body.website,
        add_data_website_to_db,
    )


@app.post(
    "/clear_data",
    response_model=ClearDataResponse,
    summary="clear data",
    status_code=HTTP_200_OK,
)
async def clear_data_api(
    request: Request, request_body: ClearDataRequest, response: Response
):
    product_id = request.state.product_id
    client_id = request.state.client_id
    request_id = request.state.request_id
    status = "success"
    response_text = f"clear data success"

    is_success, error_message = clear_data_db(
        product_id, client_id, request_body.knowledge_name
    )

    if not is_success:
        status = "fail"
        response_text = f"clear data fail"

    response_dict = {
        "status": status,
        "request_id": request_id,
        "data": {"message": response_text},
    }
    if status == "fail":
        response_dict["error"] = [{"object": "error", "detail": error_message}]
        # return with Http 500
        return JSONResponse(status_code=500, content=response_dict)

    return response_dict
