
from django.core.files.uploadhandler import FileUploadHandler, StopUpload, StopFutureHandlers

class MaxSizeUploadHandler(FileUploadHandler):
    def __init__(self, request=None, max_bytes=10 * 1024 * 1024):
        super().__init__(request)
        self.max_bytes = max_bytes
        self.bytes_received = 0

    def receive_data_chunk(self, raw_data, start):
        self.bytes_received += len(raw_data)
        if self.bytes_received > self.max_bytes:
            raise StopUpload(connection_reset=True)
        return raw_data

    def file_complete(self, file_size):
        return None
