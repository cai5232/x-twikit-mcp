"""Authenticated remote MCP entrypoint for Lumi."""
import hmac
import os
import uvicorn
from starlette.responses import JSONResponse
from server import mcp

token = os.environ.get("MCP_ACCESS_TOKEN", "").strip()
if len(token) < 32:
    raise RuntimeError("MCP_ACCESS_TOKEN must contain at least 32 characters")
inner = mcp.streamable_http_app()

async def app(scope, receive, send):
    if scope["type"] == "http":
        if scope["path"] == "/health" and scope["method"] == "GET":
            await JSONResponse({"ok": True})(scope, receive, send)
            return
        headers = dict(scope.get("headers", []))
        if not hmac.compare_digest(headers.get(b"authorization", b""), ("Bearer " + token).encode()):
            await JSONResponse({"error": "unauthorized"}, status_code=401)(scope, receive, send)
            return
    await inner(scope, receive, send)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), access_log=False)
