from flask import request, jsonify
from flask_restx import Namespace, Resource, fields

from src.services.general import upload_files
from src.utils.helpers import format_payload_validation_errors, token_required


general_ns = Namespace("general", description="General operations")

upload_model = general_ns.model("UploadFile", {
    "files": fields.List(fields.Raw(description="File to upload", required=True))
})

upload_response_model = general_ns.model("UploadResponse", {
    "file_urls": fields.List(
        fields.Nested(
            general_ns.model('File', {
                "file_name": fields.String(description="Name of the file"),
                "file_url": fields.String(description="URL of the file")
            })
        ),
        description="List of file name and URL pairs"
    )
})


@general_ns.route("/health")
class Health(Resource):
    def get(self):
        """A simple health endpoint"""
        return "healthy", 200

@general_ns.route("/upload")
class Upload(Resource):
    @general_ns.expect(upload_model)
    @general_ns.response(200, "File uploaded successfully", upload_response_model)
    @general_ns.response(400, "No file to upload")
    @general_ns.response(500, "Internal server error")
    @token_required
    def put(self):
        """Upload files endpoint"""
        files = request.files.getlist('files')

        if not files or all(f.filename == "" for f in files):
            return {"error": "No files to upload"}, 400

        try:
            result = upload_files(files)
            return {"file_urls": result}, 200
        except Exception as e:
            return {"error": str(e)}, 500