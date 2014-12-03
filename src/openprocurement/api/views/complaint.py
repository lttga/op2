# -*- coding: utf-8 -*-
from cornice.resource import resource, view
from openprocurement.api.models import Complaint, STAND_STILL_TIME, get_now
from openprocurement.api.utils import (
    apply_data_patch,
    filter_data,
    save_tender,
)
from openprocurement.api.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_tender_complaint_exists,
    validate_tender_exists_by_tender_id,
)


@resource(name='Tender Complaints',
          collection_path='/tenders/{tender_id}/complaints',
          path='/tenders/{tender_id}/complaints/{id}',
          description="Tender complaints")
class TenderComplaintResource(object):

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db

    @view(content_type="application/json", validators=(validate_complaint_data, validate_tender_exists_by_tender_id), renderer='json')
    def collection_post(self):
        """Post a complaint
        """
        tender = self.request.validated['tender']
        if tender.status not in ['active.enquiries', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t add complaint in current tender status')
            self.request.errors.status = 403
            return
        complaint_data = filter_data(self.request.validated['data'], fields=['id', 'date', 'status'])
        complaint = Complaint(complaint_data)
        src = tender.serialize("plain")
        tender.complaints.append(complaint)
        save_tender(tender, src, self.request)
        self.request.response.status = 201
        self.request.response.headers['Location'] = self.request.route_url('Tender Complaints', tender_id=tender.id, id=complaint['id'])
        return {'data': complaint.serialize("view")}

    @view(renderer='json', validators=(validate_tender_exists_by_tender_id,))
    def collection_get(self):
        """List complaints
        """
        return {'data': [i.serialize("view") for i in self.request.validated['tender'].complaints]}

    @view(renderer='json', validators=(validate_tender_complaint_exists,))
    def get(self):
        """Retrieving the complaint
        """
        return {'data': self.request.validated['complaint'].serialize("view")}

    @view(content_type="application/json", validators=(validate_patch_complaint_data, validate_tender_complaint_exists), renderer='json')
    def patch(self):
        """Post a complaint resolution
        """
        tender = self.request.validated['tender']
        if tender.status not in ['active.enquiries', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t update complaint in current tender status')
            self.request.errors.status = 403
            return
        complaint = self.request.validated['complaint']
        if complaint.status != 'accepted':
            self.request.errors.add('body', 'data', 'Can\'t update complaint in current status')
            self.request.errors.status = 403
            return
        complaint_data = filter_data(self.request.validated['data'])
        if complaint_data:
            src = tender.serialize("plain")
            complaint.import_data(apply_data_patch(complaint.serialize(), complaint_data))
            if complaint.status == 'satisfied' and tender.status != 'active.enquiries':
                tender.status = 'cancelled'
            elif complaint.status in ['rejected', 'invalid'] and tender.status == 'active.awarded':
                accepted_complaints = [
                    i
                    for i in self.request.validated['complaints']
                    if i.status == 'accepted'
                ]
                accepted_awards_complaints = [
                    i
                    for a in tender.awards
                    for i in a.complaints
                    if i.status == 'accepted'
                ]
                stand_still_time_expired = tender.awardPeriod.endDate + STAND_STILL_TIME < get_now()
                if not accepted_complaints and not accepted_awards_complaints and stand_still_time_expired:
                    active_awards = [
                        a
                        for a in tender.awards
                        if a.status == 'active'
                    ]
                    if active_awards:
                        tender.status = 'complete'
                    else:
                        tender.status = 'unsuccessful'
            save_tender(tender, src, self.request)
        return {'data': complaint.serialize("view")}