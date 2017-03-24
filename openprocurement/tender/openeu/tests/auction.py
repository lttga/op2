# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_features_tender_data,
    test_bids
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_organization,
    test_lots
)

from openprocurement.tender.openeu.tests.auction_blanks import (
    # TenderFeaturesAuctionResourceTest
    get_tender_features_auction,
    # TenderMultipleLotAuctionResourceTest
    get_tender_2lot_auction,
    post_tender_2lot_auction,
    patch_tender_2lot_auction,
    post_tender_2lot_auction_document,
    # TenderLotAuctionResourceTest
    get_tender_lot_auction,
    post_tender_lot_auction,
    patch_tender_lot_auction,
    post_tender_lot_auction_document,
    # TenderSameValueAuctionResourceTest
    post_tender_auction_not_changed,
    post_tender_auction_reversed,
    # TenderAuctionResourceTest
    get_tender_auction_not_found,
    get_tender_auction,
    post_tender_auction,
    patch_tender_auction,
    post_tender_auction_document,
)


class TenderAuctionResourceTest(BaseTenderContentWebTest):
    #initial_data = tender_data
    initial_auth = ('Basic', ('broker', ''))
    initial_bids = test_bids

    def shift_to_auction_period(self):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        self.time_shift('active.auction')
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.auction")
        self.app.authorization = auth

    def setUp(self):
        super(TenderAuctionResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification")

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        for qualific in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualific['id'], self.tender_token), {'data': {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        # # switch to active.pre-qualification.stand-still

    test_get_tender_auction_not_found = snitch(get_tender_auction_not_found)
    test_get_tender_auction = snitch(get_tender_auction)
    test_post_tender_auction = snitch(post_tender_auction)
    test_patch_tender_auction = snitch(patch_tender_auction)
    test_post_tender_auction_document = snitch(post_tender_auction_document)


class TenderSameValueAuctionResourceTest(BaseTenderContentWebTest):

    initial_status = 'active.auction'
    tenderer_info = deepcopy(test_organization)
    initial_bids = [
        {
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
        }
        for i in range(3)
    ]

    def setUp(self):
        super(TenderSameValueAuctionResourceTest, self).setUp()
        auth = self.app.authorization
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification")
        self.app.authorization = auth

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        for qualific in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(
                self.tender_id, qualific['id']), {'data': {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status('active.auction', {'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.auction")
        self.app.authorization = auth

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderLotAuctionResourceTest(TenderAuctionResourceTest):
    initial_lots = test_lots
    # initial_data = test_tender_data

    test_get_tender_auction = snitch(get_tender_lot_auction)
    test_post_tender_auction = snitch(post_tender_lot_auction)
    test_patch_tender_auction = snitch(patch_tender_lot_auction)
    test_post_tender_auction_document = snitch(post_tender_lot_auction_document)


class TenderMultipleLotAuctionResourceTest(TenderAuctionResourceTest):
    initial_lots = 2 * test_lots

    test_get_tender_auction = snitch(get_tender_2lot_auction)
    test_post_tender_auction = snitch(post_tender_2lot_auction)
    test_patch_tender_auction = snitch(patch_tender_2lot_auction)
    test_post_tender_auction_document = snitch(post_tender_2lot_auction_document)


class TenderFeaturesAuctionResourceTest(BaseTenderContentWebTest):
    initial_data = test_features_tender_data
    initial_status = 'active.auction'
    tenderer_info = deepcopy(test_organization)
    initial_bids = [
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.1,
                }
                for i in test_features_tender_data['features']
            ],
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
        },
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.15,
                }
                for i in test_features_tender_data['features']
            ],
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 479,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
        }
    ]

    test_get_tender_auction = snitch(get_tender_features_auction)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSameValueAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderFeaturesAuctionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
