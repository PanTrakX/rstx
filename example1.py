from rstx import Rstx  # We are importing the Rstx class

app = Rstx()  # We are creating an app


# We are creating a function called index with one required 'request' parameter
def index(request):
    # We are returning a tuple, the json response and the status code
    return {'Hello': 'World'}, 200


# We are binding the `index` function to the `/` path
app.add_route('/', index)


if __name__ == "__main__":
    # We run the app
    app.run()
