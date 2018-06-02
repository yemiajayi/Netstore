from rest_framework import serializers
from .models import Auction, Bid


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('title', 'description', 'min_price', 'deadline')


class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ('bid', 'auction')
