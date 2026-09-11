from django.shortcuts import render

from django.http import HttpResponse

from internet_shop.models import Product
from internet_shop.models import Category
from internet_shop.models import Customer
from internet_shop.models import Order
from internet_shop.models import OrderDetail

from django.views.generic import TemplateView

# Create your views here.
class ShowProductsView(TemplateView):
    template_name = "products/show_products.html"
    
    def get_context_data(self, **kwargs: any) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        
        return context