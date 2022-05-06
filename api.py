import inspect
from typing import Callable, List, Optional, Tuple, Union

import requests

import parse
import webob
import wsgiadapter
from middleware import Middleware

class API:
    def __init__(self):
        self.routes = {}
        self.exception_handler = None
        self.middleware = Middleware(self)

    def __call__(self, environ, start_response):
        return self.middleware(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = webob.Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    # Routing

    def route(self, path: str, allowed_methods: Optional[List[str]] = None):
        def wrapper(handler):
            self.add_route(path, handler, allowed_methods)
            return handler

        return wrapper

    def add_route(
        self, path: str, handler: Callable, allowed_methods: Optional[List[str]] = None
    ) -> None:
        assert path not in self.routes, "Such route already exists."

        if allowed_methods is None:
            allowed_methods = ["get", "post", "put", "patch", "delete", "options"]

        self.routes[path] = {"handler": handler, "allowed_methods": allowed_methods}

    def default_response(self, response: webob.Response):
        response.status_code = 404
        response.text = "Not found."

    def find_handler(self, request_path: str) -> Union[Tuple[Callable, str], Tuple[None, None]]:
        for path, handler_data in self.routes.items():
            parse_result = parse.parse(path, request_path)
            if parse_result is not None:
                return handler_data, parse_result.named

        return None, None

    def handle_request(self, request: webob.Request) -> webob.Response:
        response = webob.Response()

        handler_data, kwargs = self.find_handler(request_path=request.path)

        try:
            if handler_data is not None:
                handler = handler_data["handler"]
                allowed_methods = handler_data["allowed_methods"]
                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise AttributeError("Method not allowed", request.method)
                elif request.method.lower() not in allowed_methods:
                    raise AttributeError("Method not allowed", request.method)

                handler(request, response, **kwargs)
            else:
                self.default_response(response)
        except Exception as error:
            if self.exception_handler is None:
                raise error
            else:
                self.exception_handler(request, response, error)
        return response

    # Test tooling

    def test_session(self, base_url: str = "http://testserver"):
        session = requests.Session()
        session.mount(prefix=base_url, adapter=wsgiadapter.WSGIAdapter(self))
        return session

    # Plugins

    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler

    def add_middleware(self, middleware_cls):
        self.middleware.add(middleware_cls)