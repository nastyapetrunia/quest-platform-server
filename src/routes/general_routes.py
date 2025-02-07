from flask_restx import Namespace, Resource

general_ns = Namespace("general", description="Simple health check operations")

@general_ns.route("/health")
class Health(Resource):
    def get(self):
        """A simple health endpoint"""
        return "healthy", 200