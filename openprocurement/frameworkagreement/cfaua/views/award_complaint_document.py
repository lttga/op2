# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.award_complaint_document import TenderUaAwardComplaintDocumentResource


@optendersresource(name='closeFrameworkAgreementUA:Tender Award Complaint Documents',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
                   procurementMethodType='closeFrameworkAgreementUA',
                   description="Tender award complaint documents")
class TenderEUAwardComplaintDocumentResource(TenderUaAwardComplaintDocumentResource):
    pass
