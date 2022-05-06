import inspect
import webob
import parse
import requests
import wsgiadapter


class API:
    def __init__(self):
        self.routes = {}

    def __call__(self, environ, start_response):
        request = webob.Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    def route(self, path):
        def wrapper(handler):
            self.add_route(path, handler)
            return handler

        return wrapper

    def add_route(self, path, handler):
        assert path not in self.routes, "That route already exists."
        self.routes[path] = handler

    def default_response(self, response: webob.Response):
        response.status_code = 404
        response.text = "Not found."

    def find_handler(self, request_path: str):
        for path, handler in self.routes.items():
            parse_result = parse.parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named

        return None, None

    def handle_request(self, request: webob.Request):
        response = webob.Response()

        handler, kwargs = self.find_handler(request_path=request.path)

        if handler is not None:
            if inspect.isclass(handler):
                handler = getattr(handler(), request.method.lower())
                if handler is None:
                    raise AttributeError("Method not allowed", request.method)

            handler(request, response, **kwargs)
        else:
            self.default_response(response)

        return response

    def test_session(self, base_url: str = "http://testserver"):
        session = requests.Session()
        session.mount(prefix=base_url, adapter=wsgiadapter.WSGIAdapter(self))
        return session
