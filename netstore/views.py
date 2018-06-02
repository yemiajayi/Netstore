from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader
from django.views import generic
import hashlib
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.views.generic import View
from .forms import *
from .models import Auction, Bid
from .serializers import AuctionSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from django_filters.rest_framework import *
from rest_framework import filters
from django.utils.translation import ugettext as _
import schedule


##########################################################################################

# Create your views here.

# Enable concurrency
salt = "(cap&otto1632)"


# Index view
class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'all_auctions'

    def get_queryset(self):
        return Auction.objects.all().order_by('-pk')


# Detail view
# class DetailView(generic.DetailView):
#    model = Auction
#    template_name = 'bid.html'


def auction_detail(request, pk):
    form = BiddingForm()
    auction = Auction.objects.get(pk=pk)
    return render(request, "bid.html", {'form': form, 'auction': auction})


# create user view (UC1)
class CreateUser(View):
    form_class = UserForm
    template_name = 'create_user.html'

    # display a blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # process form data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            # normalize data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user.set_password(password)
            user.save()

            # verify if credentials are correct and return User objects
            user = authenticate(username=username, password=password, first_name=first_name, last_name=last_name)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    return redirect('index')

        return render(request, self.template_name, {'form': form})


# edit user view (UC2)
def edit_user(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = EditUserForm(request.POST, instance=request.user)

            if form.is_valid():
                form.save()
                return redirect('index')
        else:
            form = EditUserForm(instance=request.user)
            args = {'form': form}
            return render(request, 'edit_user.html', args)
    else:
        messages.add_message(request, messages.INFO, _(u'log in to edit account'))
        return redirect('index')


# User login view (UC2 continues...)
class Login(View):
    form_class = LoginForm
    template_name = 'login.html'

    # display blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # process form data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            # normalize data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # verify credentials are correct and return user objects
            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    return redirect('index')

        # show form if credentials invalid
        return render(request, self.template_name, {'form': form})


# User logout (UC2 continues...)
def logout_view(request):
    logout(request)
    return redirect('index')


# Change password view (UC2 continues...)
def change_pw(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = PasswordChangeForm(data=request.POST, user=request.user)

            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                return redirect('index')
            else:
                return redirect('change_pw')
        else:
            form = PasswordChangeForm(user=request.user)

            args = {'form': form}
            return render(request, 'change_pw.html', args)
    else:
        messages.add_message(request, messages.INFO, _(u'log in to change password'))
        return redirect('index')


# Create auction view (UC3)
def create_auction(request):

    if not request.user.is_authenticated():
        messages.add_message(request, messages.INFO, _(u'Login to add auction'))
        return redirect('index')
        # return render(request, "login.html", {"login": login})
    else:

        if request.method == "POST":
            form = CreateAuctionForm(data=request.POST)
            if form.is_valid():
                auction = Auction()
                auction.title = request.POST["title"]
                auction.seller = request.user
                auction.description = request.POST["description"]
                auction.deadline = request.POST["deadline"]
                auction.min_price = request.POST["min_price"]
                auction.email = request.user.email

                md5 = hashlib.md5(
                    (str(auction.title) + str(auction.description) + str(auction.deadline) + str(auction.min_price) +
                     str(auction.seller.username) + salt).encode('utf-8'))

                # add current version to obj.
                auction.version = md5.hexdigest()

                return render(request, "confirm_auction.html", {'auction': auction})
            else:
                messages.add_message(request, messages.INFO, _(u'Oops! Something went wrong'))
                return render(request, "create_auction.html", {'form': form})
        else:
            form = CreateAuctionForm()
            return render(request, "create_auction.html", {'form': form})


# Confirm auction view (UC3...continues)
def confirm_auction(request):
    if not request.user.is_authenticated():
        print('User not authenticated')
        messages.add_message(request, messages.INFO, _(u'Log in to create auction'))
        return redirect('index')
    else:
        if request.method == "POST":
            print('POST request')
            if 'save_auction' in request.POST:
                print('saved')
                auction = Auction()
                auction.title = request.POST["title"]
                auction.seller = request.user
                auction.description = request.POST["description"]
                auction.min_price = request.POST["min_price"]
                auction.deadline = request.POST["deadline"]
                auction.active = True
                print(request.user)
                auction.email = request.user.email

                md5 = hashlib.md5(
                    (str(auction.title) + str(auction.description) + str(auction.deadline) + str(auction.min_price) +
                     str(auction.seller.username) + salt).encode('utf-8'))

                # add current version to obj.
                auction.version = md5.hexdigest()

                auction.save()

                send_mail(
                    'New auction posted',
                    'You have just created an auction '+auction.title +
                    '. You can edit your auction with this link: '
                    'http://127.0.0.1:8000/edit/'+auction.version +
                    'The above link is no longer valid after a bid is placed or description edited',
                    'info@netstore.com',
                    [auction.email],
                    fail_silently=False,
                )

                messages.add_message(request, messages.INFO, 'Auction saved')
                return redirect('index')
            else:
                messages.add_message(request, messages.INFO, 'Auction discarded')
                return redirect('index')

        else:
            messages.add_message(request, messages.INFO, 'Action not allowed')
            return redirect('index')


# Edit auction description view (UC4)
def edit_auction(request, pk):

    if request.user.is_authenticated():
        if request.method == "POST":
            auction = Auction.objects.get(pk=pk)

            if auction.seller == request.user and auction is not None:
                auction.description = request.POST["description"]
                md5 = hashlib.md5(
                    (str(auction.title) + str(auction.description) + str(auction.deadline) + str(auction.min_price) +
                     str(auction.seller.username) + salt).encode('utf-8'))
                auction.version = md5.hexdigest()
                auction.save()
            return redirect('auction_detail', auction.id)
        else:
            template = loader.get_template('edit_auction.html')
            context = {'auction': Auction.objects.get(pk=pk)}
            return HttpResponse(template.render(context, request))
    else:
        messages.add_message(request, messages.INFO, 'Please login to edit auction')
        return redirect('index')


# search auction view (UC5)
def search_auction(request):
    if request.method == 'GET':
        form = SearchForm(data=request.GET)
        if form.is_valid():
            matching_auctions = form.search()
            return render_to_response('search_result.html', {'matching_auctions': matching_auctions})
        else:
            return redirect('index')
    else:
        return redirect('index')


# Bid (UC6)
def bidding(request, pk):

    if request.user.is_authenticated():

        if request.method == "GET":
            form = BiddingForm()
            auction = Auction.objects.get(pk=pk)
            return render(request, 'bid.html', {'form': form, 'auction': auction})

        if request.method == "POST":  # bid an auction

            form = BiddingForm(data=request.POST)   # bidding form
            auction = Auction.objects.get(pk=pk)
            if not form.is_valid():
                return render(request, "bid.html", {'form': form, 'auction': auction})
            bid = Bid()

            auction = Auction.objects.get(pk=pk)
            user = request.user
            bid.auction = auction
            bid.bidder = user
            bid.bid = Decimal(form.data['bid'])  # add bid amount to bid

            # OP2: Soft deadline for bidding
            if timedelta(seconds=0) < auction.deadline - timezone.now() < timedelta(minutes=5):  # deadline is in 5mins
                auction.deadline += timedelta(minutes=5)  # add 5mins to deadline
                messages.add_message(request, messages.INFO, 'Deadline extended by 5mins')

            if auction.version != request.POST['version']:  # Check for concurrency
                messages.add_message(request, messages.INFO, 'someone edited the auction/placed a bid')
                return render(request, "bid.html", {'form': form, 'auction': auction})  # render form again

            # Auction must be active, not banned, not your own
            if auction is not None and form.is_valid() and user is not auction.seller and \
                    auction.banned is False and auction.active is True:
                print('bid accepted')
                if auction.bid_set.count() > 0:  # if bids exist already
                    currentwinner = auction.bid_set.first().bidder
                    print(auction.bid_set.first().bidder)
                    if auction.bid_set.first().bidder != user:  # prevents current winner from raising bid
                        auction.min_price += bid.bid
                        bid.bid = auction.min_price
                        bid.save()
                        auction.winner = bid.bidder.username
                        md5 = hashlib.md5(
                            (str(auction.title) + str(auction.description) + str(auction.deadline) +
                             str(auction.min_price) + str(auction.seller.username) + salt).encode('utf-8'))
                        auction.version = md5.hexdigest()  # add current version to object
                        auction.save()

                        send_mail(
                            'New bid placed',
                            'The auction ' + auction.title + ' has a new bid of ' + str(auction.min_price) +
                            'euros by ' + auction.winner,
                            'info@netstore.com',
                            [auction.seller.email, bid.bidder.email, currentwinner.email],
                            fail_silently=False,
                        )
                else:  # if its the first bid
                    auction.min_price += bid.bid
                    bid.bid = auction.min_price
                    bid.save()
                    auction.winner = bid.bidder.username
                    md5 = hashlib.md5(
                        (str(auction.title) + str(auction.description) + str(auction.deadline) +
                         str(auction.min_price) + str(auction.seller.username) + salt).encode('utf-8'))
                    auction.version = md5.hexdigest()
                    auction.save()

                    send_mail(
                        'New bid placed',
                        'Auction ' + auction.title + ' has a new bid of ' + str(auction.min_price) + 'euros by ' +
                        auction.winner,
                        'info@netstore.com',
                        [auction.seller.email, bid.bidder.email],
                        fail_silently=False,
                    )
                return redirect('auction_detail', auction.pk)
            return render(request, "bid.html", {'form': form, 'auction': auction})
        else:
            return redirect('index')
    else:
        messages.add_message(request, messages.INFO, 'Login to bid auction')
        return redirect('index')


# Ban auction (UC7)
def ban_auction(request, pk):

    if request.user.is_superuser is True:
        auction = Auction.objects.get(pk=pk)
        auction.banned = True
        auction.save()
        email_all_bidders = ''  # get email of all the bidders on the auction

        for bid in auction.bid_set.all():
            if bid.bidder.email not in email_all_bidders:
                email_all_bidders = email_all_bidders+bid.bidder.email+', '

        # Notify seller and all bidders of the ban
        send_mail(
            'Auction banned by Admin',
            'The auction ' + auction.title + ' has been banned by the admin.',
            'info@netstore.com',
            [auction.seller.email, email_all_bidders],
            fail_silently=False,
            )

        messages.add_message(request, messages.INFO, 'Auction successfully banned')
        return redirect('index')


# UC8: Resolve Auction
def resolve_auction(request, pk):

    auctions = Auction.objects.all()

    for auction in auctions:
        bid = auction.bid_set.all()
        email_all_bidders = ''
        if auction.active is True and timezone.now() == auction.deadline:
            auction.active = False
            auction.due = True
            if bid.bidder.email not in email_all_bidders:
                email_all_bidders = email_all_bidders+bid.bidder.email+', '

            send_mail(
                'Auction Resolved',
                'The auction ' + auction.title + ' has now ended and winner selected',
                'info@netstore.com',
                [auction.seller.email, email_all_bidders],
                fail_silently=False,
                )

            send_mail(
                'Congrats, You won!',
                'You have won the ' + auction.title + '. Check seller instruction for payment.',
                'info@netstore.com',
                [auction.winner.email],
                fail_silently=False,
                )

            auction.adjudicated = True
            auction.save()

schedule.every(1).minutes.do(resolve_auction)


# WS1: Search API, filters through auction title and description
class SearchAPIView(generics.ListAPIView):

    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title', 'description')


##########################################################################################


# Optional WS: auction API
class AuctionAPI(APIView):

    def get(self, request):
        auctions = Auction.objects.all()
        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data)
