
class NotFoundDocument(Exception):
    """Exception raised for errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, document_id: int):
        self.did = document_id
        self.message = f"Not found document by ID: {document_id}"
        super().__init__(self.message)
