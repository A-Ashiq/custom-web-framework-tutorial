from typing import Callable

import webob


class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response) -> webob.Response:
        request = webob.Request(environ)
        response = self.app.handle_request(request)
        return response(environ, start_response)

    def add(self, middleware_cls: Callable) -> None:
        self.app = middleware_cls(self.app)

    def process_request(self, request: webob.Request) -> webob.Request:
        ...

    def process_response(
        self, request: webob.Request, response: webob.Response
    ) -> webob.Response:
        ...

    def handle_request(self, request: webob.Request) -> webob.Response:
        self.process_request(request)
        response = self.app.handle_request(request)
        self.process_response(request, response)

        return response
