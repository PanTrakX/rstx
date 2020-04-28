from rstx import Rstx

x = Rstx()


def index(r):
    if r.method == 'GET':
        return {"Hello": "World"}, 200

    if r.method == 'POST':
        return {"World": "Hello"}, 200


def re(r):
    return r.header, 200


def le(r):
    return {'len': len(r.raw)}, 200


def api(r):

    if r.method == 'GET':
        return {"API": "YES"}, 200

    if r.method == 'POST':
        print(r.body)
        return r.body, 200


def something(r):
    return {"API?": "YES"}, 404


def teapot(r):
    return {"status": "im a teapot"}, 418

# routes = {
#     '/': index,
#     '/api/': api,
#     '/something/': something,
# }

# x.add_routes(routes)


x.add_route('/', index)
x.add_route('/api/', api)
x.add_route('/something/', something)
x.add_route('/teapot/', teapot)
x.add_route('/r/', re)
x.add_route('/le/', le)

if __name__ == "__main__":
    x.run()
