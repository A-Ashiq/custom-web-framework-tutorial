from api import API

app = API()


@app.route("/home")
def home(request, response):
    response.text = "Hello from the HOME page"



@app.route("/hello/{name}")
def hello(request, response, name):
    response.text = f"Hello, {name}"
