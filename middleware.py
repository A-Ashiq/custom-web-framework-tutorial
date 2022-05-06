import webob


class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = webob.Request(environ)
        response = self.app.handle_request(request)
        return response(environ, start_response)

    def add(self, middleware_cls):
        self.app = middleware_cls(self.app)

    def process_request(self, req):
        ...

    def process_response(self, req, resp):
        ...

    def handle_request(self, request):
        self.process_request(request)
        response = self.app.handle_request(request)
        self.process_response(request, response)

        return response
