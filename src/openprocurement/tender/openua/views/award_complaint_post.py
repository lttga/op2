# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.validation import (
    validate_award_complaint_post_data,
    validate_complaint_post_complaint_status,
    validate_complaint_post,
    validate_complaint_post_review_date,
)
from openprocurement.tender.openua.views.complaint_post import TenderComplaintPostResource


@optendersresource(
    name="aboveThresholdUA:Tender Award Complaint Posts",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender award complaint posts",
)
class TenderAwardComplaintPostResource(TenderComplaintPostResource):
    def generate_location_url(self):
        return  self.request.route_url(
            "{}:Tender Award Complaint Posts".format(self.request.validated["tender"].procurementMethodType),
            tender_id=self.request.validated["tender_id"],
            award_id=self.request.validated["award_id"],
            complaint_id=self.request.validated["complaint_id"],
            post_id=self.request.validated["post"]["id"],
        )

    @json_view(
        content_type="application/json",
        validators=(
                validate_award_complaint_post_data,
                validate_complaint_post,
                validate_complaint_post_complaint_status,
                validate_complaint_post_review_date,
        ),
        permission="edit_complaint",
    )
    def collection_post(self):
        return super(TenderAwardComplaintPostResource, self).collection_post()
