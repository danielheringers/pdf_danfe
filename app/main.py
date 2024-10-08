from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import uuid
from app.api.router.routes import router
from app.schemas.errors.custom_exception import HeaderMissingException

app = FastAPI()

@app.exception_handler(HeaderMissingException)
async def header_missing_exception_handler(request: Request, exc: HeaderMissingException):
    print(f"Missing headers detected: {exc.missing_headers}")
    errors = []
    for header in exc.missing_headers:
        errors.append({
            "code_error": 400,
            "msg": f"{header} is required",
            "location": "header",
            "property_errors": [{
                "value": None,
                "type": "technical-error",
                "code_error": f"PDF_H_000{exc.missing_headers.index(header) + 1}",
                "msg": f"{header} is required",
                "property": header
            }]
        })
    
    response = {
        "code": 400,
        "message": "Bad Request",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "requestid": str(uuid.uuid4()),
        "errors": errors
    }
    return JSONResponse(status_code=400, content=response)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    
    for err in exc.errors():
        loc = err['loc']
        msg = err['msg']
        typ = err['type']
        
        if loc[0] == "body":
            errors.append({
                "code_error": "PDF_0001_Body",
                "msg": msg,
                "location": "body",
                "property_errors": [{
                    "value": err['ctx'].get('value') if 'ctx' in err else None,
                    "type": "validation-error",
                    "code_error": f'PDF_0001_Body',
                    "msg": msg,
                    "property": ".".join(map(str, loc[1:]))
                }]
            })
    
    response = {
        "code": 422,
        "message": "Bad Request",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "requestid": str(uuid.uuid4()),
        "errors": errors
    }
    return JSONResponse(status_code=422, content=response)

app.include_router(router)
