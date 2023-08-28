from pydantic import BaseModel, Field
from typing import Tuple, Optional, List, Union
from typing_extensions import Literal


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        description="message from user",
        example="what is the price of this washing machine?",
    )


class Error(BaseModel):
    object: Literal["error"]
    summary: str
    detail: str


class SuccessResponse(BaseModel):
    status: str = Field(..., description="Response status", example="success")
    request_id: str = Field(..., description="Response id", example="123wereqs2")
    error: Optional[List[Error]]
    # confidence: Optional[float]
    data: str


class SourceData(BaseModel):
    data_name: str = Field(..., description="data origin", example="manual.pdf")
    page_index: int = Field(..., description="index of data", example=0)

    # for next phrase


class SectionData(BaseModel):
    section_index: int = Field(..., description="index of section", example=0)
    text_position: List[int] = Field(
        ..., description="text position", example=[0, 0, 0, 0]
    )


class SourceDataV2(SourceData):
    section_data: List[SectionData] = Field(..., description="section index")


class ChatResponseBody(BaseModel):
    message: str = Field(
        ..., description="message from chat BTL", example="its price is 1000 baht"
    )
    source_data: Optional[List[SourceData]] = Field(
        ..., description="source data of this response"
    )


class ChatResponseModel(SuccessResponse):
    data: ChatResponseBody


class ChatHistoryResponseBody(BaseModel):
    chat_history: List[str] = Field(..., description="chat history")


class ChatHistoryResponseModel(SuccessResponse):
    data: ChatHistoryResponseBody


class DisplaySourceData(BaseModel):
    data_name: str = Field(..., description="data origin", example="manual.pdf")


class DisplaySectionData(BaseModel):
    section_type: str


class DisplaySectionDataText(DisplaySectionData):
    section_type: Literal["text"]
    section_id: str = Field(..., description="section id", example="1234")
    text_position: List[float] = Field(
        ...,
        description="text position is represented as [xmin, ymin, xmax, ymax] \
            floating-point values to ensure compatibility with PDF,",
        example=[0.12, 0.23, 0.34, 0.45],
    )
    ori_text_position: List[List[float]] = Field(
        ...,
        description="Original text position is represented as [[xmin, ymin, xmax, ymax], ... ] \
            floating-point values to ensure compatibility with PDF,",
        example=[[0.12, 0.23, 0.34, 0.45], [0.12, 0.23, 0.34, 0.45]],
    )
    ori_text_list: List[str] = Field(
        ...,
        description="Original text list",
        example=["this is", "text data"],
    )

    text: str = Field(..., description="merged text data", example="this is text data")


class DisplaySectionDataTable(DisplaySectionData):
    section_type: Literal["table"]
    # TODO: not implemented


class DisplaySourceDataPDF(DisplaySourceData):
    data_type: Literal["pdf"]
    page_data: List[
        List[Union[DisplaySectionDataText, DisplaySectionDataTable]]
    ] = Field(..., description="page data")


# TODO: think about how to display text data from human review
# because I think we should not display all of our knowledge to user
class DisplaySourceDataText(DisplaySourceData):
    data_type: Literal["text"]
    data: str = Field(..., description="text data")


# for get method to get all display source data
class DisplaySourceDataResponseModel(SuccessResponse):
    data: List[Union[DisplaySourceDataPDF, DisplaySourceDataText]]
