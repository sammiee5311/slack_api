from flask import Response


class EndpointAction:
    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.action()
        return self.response


class FlaskAppWrapper:
    def __init__(self, flask):
        self.app = flask
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test-slack-api.db"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["TESTING"] = True

    def run(self):
        self.app.run()

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler), methods=methods)
