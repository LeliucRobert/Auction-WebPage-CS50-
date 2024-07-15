from django.contrib import admin
from .models import Bid, User, Category, Comment,  Listing
# Register your models here.

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Comment)
admin.site.register(Bid)