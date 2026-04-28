from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

def format_validation_errors(exc: RequestValidationError) -> dict:
    """
    Converts FastAPI/Pydantic validation errors into a clean dictionary:
    {
      "errorPayload": {
        "errors": {
          "field_name": "Error message"
        }
      }
    }
    """
    errors = {}

    for err in exc.errors():
        loc = err.get("loc", [])
        raw_msg = err.get("msg", "Invalid value")
        
        # Use the last part of the location as the field name (e.g., 'month' from ('query', 'month'))
        field = str(loc[-1]) if loc else "general"
        
        # Clean the message (remove Pydantic prefixes like 'Field required' etc. if needed, 
        # but usually 'Field required' is clean enough)
        errors[field] = raw_msg

    return {
        "errorPayload": {
            "errors": errors
        }
    }

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=format_validation_errors(exc),
    )
