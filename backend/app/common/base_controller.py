from typing import Any, Dict, List, Union, Optional, Generic, TypeVar, Callable
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import APIRouter
from app.common.router.create_module_router import create_module_router

T = TypeVar('T')

class AlertifyPayload(BaseModel):
    message: str
    theme: str = "success"
    type: str = "alert"

class PaginationLinks(BaseModel):
    self: str
    first: Optional[str] = None
    last: Optional[str] = None
    next: Optional[str] = None
    prev: Optional[str] = None

class DataPayload(BaseModel):
    data: Any
    countOnPage: Optional[int] = None
    totalCount: Optional[int] = None
    perPage: Optional[int] = None
    totalPages: Optional[int] = None
    currentPage: Optional[int] = None
    paginationLinks: Optional[PaginationLinks] = None

class SuccessResponse(BaseModel, Generic[T]):
    dataPayload: Optional[DataPayload] = None
    alertifyPayload: Optional[AlertifyPayload] = None

class ErrorPayload(BaseModel):
    errors: Union[List[str], Dict[str, Any], str]

class ErrorResponse(BaseModel):
    errorPayload: ErrorPayload

class BaseController:
    """
    Standardized Response Wrapper mimicking Yii2 logic for premium API responses.
    """
    module: str = None
    tags: list[str] | None = None
    router: APIRouter = None

    def __init__(self):
        if not self.module:
            raise RuntimeError(f"{self.__class__.__name__} must define `module`")
        
        self.router = create_module_router(module=self.module, tags=self.tags)
        self.register_routes()

    def register_routes(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_route_info"):
                for method, path, options in attr._route_info:
                    getattr(self.router, method)(path, **options)(attr)

    def payload_response(
            self,
            data: Any,
            message: str = None,
            status_code: int = 200,
            one_record: bool = True,
            pagination: Dict = None
    ) -> JSONResponse:
        if one_record:
            payload_data = DataPayload(data=data)
        else:
            if not data or len(data) == 0:
                payload_data = DataPayload(
                    data="No records available",
                    countOnPage=0,
                    totalCount=0,
                    perPage=pagination.get("per_page", 25) if pagination else 25,
                    totalPages=0,
                    currentPage=pagination.get("page", 1) if pagination else 1,
                    paginationLinks=PaginationLinks(self=str(pagination.get("path", "/"))) if pagination else None
                )
            else:
                payload_data = DataPayload(
                    data=data,
                    countOnPage=len(data),
                    totalCount=pagination.get("total", len(data)) if pagination else len(data),
                    perPage=pagination.get("per_page", 25) if pagination else 25,
                    totalPages=pagination.get("total_pages", 1) if pagination else 1,
                    currentPage=pagination.get("page", 1) if pagination else 1,
                    paginationLinks=PaginationLinks(
                        self=str(pagination.get("path", "/")),
                        first=str(pagination.get("first_url")) if pagination else None,
                        last=str(pagination.get("last_url")) if pagination else None
                    ) if pagination else None
                )

        alert_payload = None
        if message:
            alert_payload = AlertifyPayload(message=message)

        response_obj = SuccessResponse(dataPayload=payload_data, alertifyPayload=alert_payload)
        return JSONResponse(content=response_obj.model_dump(exclude_none=True, mode="json"), status_code=status_code)

    def alertify_response(self, message: str, theme: str = "success", type: str = "alert") -> JSONResponse:
        alert_payload = AlertifyPayload(message=message, theme=theme, type=type)
        response_obj = SuccessResponse(alertifyPayload=alert_payload)
        return JSONResponse(content=response_obj.model_dump(exclude_none=True))

    def error_response(self, errors: Union[str, Dict, List], status_code: int = 422) -> JSONResponse:
        alert_msg = errors if isinstance(errors, str) else "Validation failed. Please check the fields."
        # If errors is a list of strings, join them
        if isinstance(errors, list):
            alert_msg = " | ".join([str(e) for e in errors])
            
        response_obj = ErrorResponse(
            errorPayload=ErrorPayload(errors=errors),
            alertifyPayload=AlertifyPayload(message=alert_msg, theme="error", type="alert")
        )
        return JSONResponse(content=response_obj.model_dump(exclude_none=True, mode="json"), status_code=status_code)

def route(method: str, path: str, **options):
    method = method.lower()
    def decorator(func: Callable):
        if not hasattr(func, "_route_info"):
            func._route_info = []
        func._route_info.append((method, path, options))
        return func
    return decorator
