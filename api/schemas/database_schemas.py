from pydantic import BaseModel, Field
from typing import Tuple, Optional, List, Union
from typing_extensions import Literal
from schemas.chat_btl_schemas import SuccessResponse


class AddDataResponse(SuccessResponse):
    ...


class ClearDataResponse(SuccessResponse):
    ...


class AddDataRequest(BaseModel):
    knowledge_name: str = Field(
        ...,
        description="knowledge name",
        example="knowledge name",
    )


class ClearDataRequest(BaseModel):
    knowledge_name: str = Field(
        ...,
        description="knowledge name",
        example="knowledge name",
    )


# add data have 3 type
# text
# file
# website


class AddDataTextRequest(AddDataRequest):
    text: str = Field(
        ...,
        description="text",
        example="this is text",
    )


class AddDataFileRequest(AddDataRequest):
    file: str = Field(
        ...,
        description="file",
        example="this is file",
    )


class AddDataWebsiteRequest(AddDataRequest):
    website: str = Field(
        ...,
        description="website",
        example="this is website",
    )


class AddDataTextResponse(AddDataResponse):
    ...


class AddDataFileResponse(AddDataResponse):
    ...


class AddDataWebsiteResponse(AddDataResponse):
    ...
