from starlette.requests import Request

def get_translator(request: Request):
    return request.app.state.translator.get(
        request.headers.get("lang", "en"), None
    )