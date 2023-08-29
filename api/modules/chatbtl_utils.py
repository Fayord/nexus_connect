import os
import pickle
import logging
from typing import List, Sized, Tuple
from dotenv import load_dotenv


import openai
import tiktoken
import chromadb
import requests

from langchain import PromptTemplate, LLMChain
from langchain.callbacks import get_openai_callback
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryBufferMemory, ChatMessageHistory
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.schema.document import Document
from langchain.vectorstores.base import VectorStore
from langchain.memory.chat_memory import BaseChatMemory

# from pythainlp import thai_characters
# thai_characters from pythainlp
thai_characters = "กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮฤฦะัาำิีึืุูเแโใไๅํ็่้๊๋ฯฺๆ์ํ๎๏๚๛\
๐๑๒๓๔๕๖๗๘๙฿"
dir_path = os.path.dirname(os.path.realpath(__file__))
credential_path = f"{dir_path}/../../.credential"
# check is credential_path exist
assert os.path.exists(credential_path) is True
load_dotenv(credential_path)

openai.api_key = os.environ["OPENAI_API_KEY"]

gpt_model = "gpt-3.5-turbo"
max_tokens = 1000


def filter_source_document_metadatas(source_documents: List[Document]) -> List[dict]:
    source_documents_dict = []
    for source_document in source_documents:
        source_documents_dict.append(source_document.metadata)
    return source_documents_dict


# custom Exception fail load vectorstore db
class LoadDBException(Exception):
    pass


def load_db(
    persist_directory: str = f"{dir_path}/new_data/db",
    embeddings=OpenAIEmbeddings(),
) -> VectorStore:
    db = None
    try:
        assert os.path.exists(persist_directory) is True

        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        print("\tLoad chroma index success")
    except Exception:
        raise LoadDBException("Load chroma index failed")
    return db


def get_chromadb_setting():
    setting = chromadb.config.Settings()
    setting["persist_directory"] = f"../../vector_db/chroma"
    return setting


def load_db_api(
    collection_name,
    embeddings=OpenAIEmbeddings(),
) -> VectorStore:
    db = None
    # try:
    #     url = f"http://localhost:8000/api/v1/collections/{collection_name}"
    #     response = requests.get(url)
    #     assert response.status_code == 200
    #     db = Chroma(
    #         collection_name=collection_name,
    #         client=chromadb.HttpClient(),
    #         embedding_function=embeddings,
    #     )

    #     print("\tLoad chroma index success")
    # except Exception:
    #     raise LoadDBException("Load chroma index failed")
    # url = f"http://localhost:8000/api/v1/collections/{collection_name}"
    print("\n\there,")
    try:
        url = f"http://localhost:8000/api/v1/collections/{collection_name}"
        response = requests.get(url)
        print("\n\there,", response.status_code, url)
    except:
        pass
    try:
        url = f"http://chroma_server:8000/api/v1/collections/{collection_name}"
        response = requests.get(url)
        print("\n\there,", response.status_code, url)
    except:
        pass
    try:
        url = f"http://server:8000/api/v1/collections/{collection_name}"
        response = requests.get(url)
        print("\n\there,", response.status_code, url)
    except:
        pass
    assert response.status_code == 200

    db = Chroma(
        collection_name=collection_name,
        client=chromadb.HttpClient(
            host="chroma_server", settings=get_chromadb_setting()
        ),
        embedding_function=embeddings,
    )

    print("\tLoad chroma index success")
    return db


def translate_sentence(
    input_sentence: str,
    desired_language: str,
    context_sentence: str = None,
) -> str:
    input_variables = ["input_sentence"]
    desired_language = desired_language.lower()
    langauge_template_dict = {
        "thai": "translate this the following sentences to Thai {input_sentence}, if it already in Thai return {input_sentence}",
        "english": "translate this the following sentences to English {input_sentence}, if it already in English return {input_sentence}",
    }
    if context_sentence is not None:
        for language, template in langauge_template_dict.items():
            # add this "and use context_sentence to help translate context_sentence ####{context_sentence}####" to v

            langauge_template_dict[language] = (
                template
                + "and use context_sentence to help translate context_sentence ####{context_sentence}####"
            )
        input_variables.append("context_sentence")

    langauge_template = langauge_template_dict.get(desired_language, None)
    if langauge_template is None:
        print("desired_language not Thai or English")
        raise NotImplementedError

    prompt = PromptTemplate(
        input_variables=input_variables,
        template=langauge_template,
    )

    chain = LLMChain(
        llm=ChatOpenAI(
            temperature=0.0,
            max_tokens=max_tokens,
            model_name=gpt_model,
        ),
        prompt=prompt,
        verbose=True,
    )

    response = chain.predict(
        input_sentence=input_sentence, context_sentence=context_sentence
    )
    return response


def translate_sentence_old(
    translate_sentence: str,
    desired_language: str,
) -> str:
    function_name = "translate"
    function_description = f"Translate a document into {desired_language} language."
    function_parameters = {}
    function_parameters["properties"] = {}
    function_parameters["properties"]["translated_document"] = {
        "type": "string",
        "description": f"The document translated into {desired_language}.",
    }
    function_parameters["required"] = []
    function_parameters["required"].append("translated_document")
    function_parameters["type"] = "object"
    function_obj = [
        {
            "name": function_name,
            "description": function_description,
            "parameters": function_parameters,
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        # This is the chat message from the user
        messages=[{"role": "user", "content": translate_sentence}],
        functions=function_obj,
        function_call={"name": "translate"},
        temperature=0.1,
    )
    try:
        result_dict = eval(
            response["choices"][0]["message"]["function_call"]["arguments"]
        )
        result = result_dict["translated_document"]
    except Exception:
        print("fail to translate")
        print(response)
        result = translate_sentence + " (translated fail)"
    return result


def load_chat_memory(
    client_id: str,
    product_id: str,
    chat_session_id: str,
) -> ChatMessageHistory:
    chat_memory_folder = f"{dir_path}/../../chat_memory"
    chat_memory_path = os.path.join(
        chat_memory_folder,
        f"{client_id}.{product_id}.{chat_session_id}.pkl",
    )

    if os.path.exists(chat_memory_path) is False:
        return ChatMessageHistory()
    with open(chat_memory_path, "rb") as f:
        chat_memory = pickle.load(f)
    print("success load chat memory")
    return chat_memory


def get_memory(
    client_id: str,
    product_id: str,
    chat_session_id: str,
) -> BaseChatMemory:
    loaded_chat_memory = load_chat_memory(client_id, product_id, chat_session_id)
    memory = ConversationSummaryBufferMemory(
        llm=ChatOpenAI(temperature=0.0, max_tokens=max_tokens, model_name=gpt_model),
        input_key="question",
        output_key="answer",
        memory_key="chat_history",
        return_messages=True,
        max_token_limit=1000,
        chat_memory=loaded_chat_memory,
    )
    return memory


class NoOpLLMChain(LLMChain):
    """No-op LLM chain."""

    def __init__(self):
        """Initialize."""
        super().__init__(
            llm=ChatOpenAI(), prompt=PromptTemplate(template="", input_variables=[])
        )

    def run(self, question: str, *args, **kwargs) -> str:
        return question


def create_qa(
    db: VectorStore,
    memory: BaseChatMemory,
    db_params: dict = {"search_type": "mmr"},
) -> ConversationalRetrievalChain:
    qa = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0.0, max_tokens=max_tokens, model_name=gpt_model),
        chain_type="stuff",
        memory=memory,
        retriever=db.as_retriever(**db_params),
        return_generated_question=True,
        return_source_documents=True,
    )

    no_op_chain = NoOpLLMChain()
    qa.question_generator = no_op_chain
    modified_template = "Use the following pieces of context to answer the users question. \nIf you don't know the answer, just say that you don't know, don't try to make up an answer.\n----------------\n{context}\nChat History:\n{chat_history}"
    system_message_prompt = SystemMessagePromptTemplate.from_template(modified_template)
    qa.combine_docs_chain.llm_chain.prompt.messages[0] = system_message_prompt

    # add chat_history as a variable to the llm_chain's ChatPromptTemplate object
    qa.combine_docs_chain.llm_chain.prompt.input_variables = [
        "context",
        "question",
        "chat_history",
    ]
    return qa


def check_thai_alphabet(text: str, thai_characters: str = thai_characters) -> bool:
    if any(char in thai_characters for char in text):
        return True
    return False


def count_token(text: str, model: str = "gpt-3.5-turbo") -> int:
    encoding = tiktoken.encoding_for_model(model)

    return len(encoding.encode(text))


def remove_elements_to_limit(text_lengths: Sized, limit: int) -> int:
    total_length = sum(text_lengths)
    if total_length <= limit:
        return 0

    current_sum = 0
    remove_index = 0

    for i, length in enumerate(text_lengths):
        current_sum += length
        if current_sum > limit:
            remove_index = i
            break

    return remove_index


client_loggers = {}


def create_logger(
    client_id: str,
    product_id: str,
    chat_session_id: str,
    log_level: int = logging.DEBUG,
) -> logging.Logger:
    log_file = f"{dir_path}/../../logs/c.{client_id}.p.{product_id}.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger_key = f"{client_id}:{product_id}:{chat_session_id}"

    if logger_key not in client_loggers:
        logger = logging.getLogger(logger_key)
        logger.setLevel(log_level)

        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s  - %(message)s"
        )
        fh.setFormatter(formatter)

        logger.addHandler(fh)
        client_loggers[logger_key] = logger

    return client_loggers[logger_key]


def save_chat_memory(
    chat_message_history: ChatMessageHistory,
    client_id: str = None,
    product_id: str = None,
    chat_session_id: str = None,
) -> None:
    # save retrieved_chat_history to a file
    save_folder = f"{dir_path}/../../chat_memory"
    save_path = os.path.join(
        save_folder,
        f"{client_id}.{product_id}.{chat_session_id}.pkl",
    )
    if os.path.exists(save_folder) is False:
        os.makedirs(save_folder, exist_ok=True)
    with open(save_path, "wb") as f:
        pickle.dump(chat_message_history, f)


def qa_complete(
    qa: ConversationalRetrievalChain,
    query: str,
    database_language: str = "english",
    logger: logging.Logger = None,
    client_id: str = None,
    product_id: str = None,
    chat_session_id: str = None,
) -> Tuple[str, List[dict]]:
    if logger is None:
        logger = logging.getLogger(__name__)
    with get_openai_callback() as cb:
        # check is query has thai alphabet or not
        query_language = "thai" if check_thai_alphabet(query) else "english"

        if database_language == query_language:
            translated_query = query
        else:
            translated_query = translate_sentence(query, database_language)
        result = qa({"question": translated_query})

        if database_language == query_language:
            response = result["answer"]
        else:
            response = translate_sentence(result["answer"], query_language)
        # save chat memory
        save_chat_memory(
            chat_message_history=ChatMessageHistory(messages=result["chat_history"]),
            client_id=client_id,
            product_id=product_id,
            chat_session_id=chat_session_id,
        )
        print('result["source_documents"]', result["source_documents"])
        source_documents_metadatas = filter_source_document_metadatas(
            result["source_documents"]
        )
        logger.info("query: {}, query_language: {}".format(query, query_language))
        logger.info("translated_query: {}".format(translated_query))
        logger.info("source_documents_metadatas: {}".format(source_documents_metadatas))
        logger.info("answer: {}".format(result["answer"]))
        logger.info("translated_answer: {}".format(response))

        logger.info(f"Total Tokens: {cb.total_tokens}")
        logger.info(f"Prompt Tokens: {cb.prompt_tokens}")
        logger.info(f"Completion Tokens: {cb.completion_tokens}")
        logger.info(f"Total Cost (USD): ${cb.total_cost}")

    return response, source_documents_metadatas


def get_source_data_metadata(
    product_id: str,
) -> List[dict]:
    return None


if __name__ == "__main__":
    print(__name__)
