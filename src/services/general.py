from src.utils.helpers import upload_to_s3

def upload_files(files: list) -> dict:
    file_urls = {}
    for file in files:
        try:
            file_urls[file.filename] = upload_to_s3(file)
        except Exception as e:
            file_urls[file.filename] = str(e)
    return file_urls
