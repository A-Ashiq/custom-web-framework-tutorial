from api import API

app = API()


def home(request, response):
    response.text = "Hello from the HOME page"
