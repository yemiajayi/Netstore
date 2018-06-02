from django.test import TestCase
from django.test import RequestFactory
from netstore.views import *
from netstore.models import Auction
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib.messages.storage.fallback import FallbackStorage


# Create your tests here.

# TR2.1: Functional testing for UC3
class TestUC3(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='tester', password='test1234', email='tester@user.com'
        )

    def test_created_auction(self):
        Auction.objects.create(title='Title', seller=self.user, description='Description', min_price=1.00,
                               deadline=timezone.now()+timedelta(hours=72))
        request = self.factory.get('auction_detail')
        request.user = self.user
        response = auction_detail(request, '1')
        self.assertEqual(response.status_code, 200)     # status code(value) 200 represents OK
        auction = Auction.objects.all().filter(id=1).first()    # Search requested auction object
        self.assertEqual(Auction.objects.all().count(), 1)
        self.assertIsNotNone(auction)

    def test_post_auction(self):
        request = self.factory.post('/create_auction/', {'title': 'new auction', 'seller': self.user, 'version'
                                    : 'bd5332ed064b38f31a18551950281b68', 'description':
                                    'latest auction item','min_price': str(1.00),
                                                         'deadline': str(timezone.now()+timedelta(hours=73))})

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = self.user
        response = create_auction(request)
        auction = Auction.objects.all().filter(title='new auction').first()  # Search requested auction object
        print(response)
        self.assertIsNone(auction)

        request2 = self.factory.post('/confirm_auction/', {'title': 'new auction', 'seller': self.user,
                                                           'version': 'bd5332ed064b38f31a18551950281b68',
                                                           'description': 'latest auction item', 'min_price':
                                                               str(1.00), 'deadline':
                                                               str(timezone.now()+timedelta(hours=73)),
                                                           'saveAuction': 'saveAuction'})

        request2.user = self.user
        setattr(request2, 'session', 'session')
        messages = FallbackStorage(request2)
        setattr(request2, '_messages', messages)
        response = confirm_auction(request2)
        auctions = Auction.objects.filter(title='new auction')
        auction = auctions.first()  # Search requested auction object
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(auction)


# TR2.2 and TR2.3: UC6 and UC10
class TestUC6and10(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(username='tester', password='pass1234', email='tester@user.com')
        self.user2 = User.objects.create_user(username='tester2', password='pass1234', email='tester2@user.com')
        self.user3 = User.objects.create_user(username='tester3', password='pass1234', email='tester3@user.com')

        Auction.objects.create(title='Title', seller=self.user1, description='Description', deadline=timezone.now() +
                               timedelta(hours=72), min_price=1.00, version='bd5332ed064b38f31a18551950281b68',
                               active=True)
        Auction.objects.create(title='Title', seller=self.user1, description='Description', deadline=timezone.now() +
                               timedelta(hours=72), min_price=1.00, version='cd5332ed064b38f31a18551950281b68',
                               active=True)
        Auction.objects.create(title='Title', seller=self.user1, description='Description', deadline=timezone.now() +
                               timedelta(hours=72), min_price=1.00, version='dd5332ed064b38f31a18551950281b68',
                               active=True)
        Auction.objects.create(title='Title', seller=self.user1, description='Description', deadline=timezone.now() +
                               timedelta(hours=72), min_price=1.00, version='ed5332ed064b38f31a18551950281b68',
                               active=True)

    # A seller shouldn't bid on own auction
    def test_own_bid(self):

        request = self.factory.post('/bidding/', {'bid': str(3.00), 'version': 'bd5332ed064b38f31a18551950281b68'})
        request.user = self.user1
        response = bidding(request, 1)
        # print(response.status_code)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Auction.objects.get(id=1).min_price, 1.00)  # seller's own bid should not be added to be = 4.00

    # Bid from a user other than the seller, should be accepted
    def test_others_bid(self):

        request = self.factory.post('/bidding/', {'bid': str(3.00), 'version': 'cd5332ed064b38f31a18551950281b68'})
        request.user = self.user2
        response = bidding(request, 2)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Auction.objects.get(id=2).min_price, 4.00)

    # TR2.3: concurrency test: Should fail if version is altered/changed
    def test_bid_concurrency(self):
        request1 = self.factory.post('/bidding/', {'bid': str(3.00), 'version': 'dd5332ed064b38f31a18551950281b68'})
        request1.user = self.user2
        response = bidding(request1, 3)
        self.assertEqual(response.status_code, 302)     # Will redirect on successful post
        request2 = self.factory.post('/bidding/', {'bid': str(5.00), 'version': 'dd5332ed064b38f31a18551950281b68'})
        setattr(request2, 'session', 'session')
        messages = FallbackStorage(request2)
        setattr(request2, '_messages', messages)
        request2.user = self.user3
        response = bidding(request2, 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Auction.objects.get(id=3).min_price, 4.00)

    # A bid lower than the minimum bid should not change the current value of the auction
    def test_min_bid(self):
        request = self.factory.post('/bidding/', {'bid': str(0.009), 'version': 'ed5332ed064b38f31a18551950281b68'})
        request.user = self.user2
        response = bidding(request, 4)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Auction.objects.get(id=4).min_price, 1.00)