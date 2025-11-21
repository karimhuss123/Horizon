from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.errors.messages import messages

## IMPROVE FOR BETTER MESSAGES...
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    default_msg = messages.exception_validation_default_message

    if not errors:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": {"message": default_msg}},
        )

    first = errors[0]
    loc = first.get("loc", [])
    field_name = loc[-1] if loc else "field"
    raw_msg = first.get("msg", default_msg)

    # maybe implement better function to map certain errors to friendlier messages
    friendly_msg = f"Error in '{field_name}': {raw_msg}"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": {"message": friendly_msg}},
    )
