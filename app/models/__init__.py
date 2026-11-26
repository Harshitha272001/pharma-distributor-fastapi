from app.models.user import User
from app.models.invoice import Invoice
from app.models.batch import Batch
from app.models.line_items import LineItem
from app.models.qa_review import QAReview

'''Invoice is the main record, LineItem contains its individual products, Batch provides traceability, QAReview records the verification outcome, and User represents the application user.'''