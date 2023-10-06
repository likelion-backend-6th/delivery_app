from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import Cart
from sajjang.models import Category, Stores, Order
from django.conf import settings
import stripe
from decimal import Decimal

# Create your views here.


class CustomerHomeView(TemplateView):
    def get(self, request):
        category_query = request.GET.get('category', None)
        categories = Category.objects.all()
        if category_query:
            stores = Stores.objects.filter(category_id=category_query)
        else:
            stores = Stores.objects.all()
    
        return render(request, template_name='home.html', context={'categories':categories, 
                                                                    'stores':stores})

    def post(self, request):
        pass


class CustomerSearchCategoryView(TemplateView):
    def get(self, request, category_id):
        pass

    def post(self, request):
        pass


class CustomerAddressView(TemplateView):
    def get(self, request):
        pass

    def post(self, request):
        pass


class CustomerAddressAddView(TemplateView):
    def get(self, request):
        pass

    def post(self, request):
        pass


class CustomerAddressDetailView(TemplateView):
    def get(self, request, address_id):
        pass


class CustomerAddressEditView(TemplateView):
    def get(self, request, address_id):
        pass

    def post(self, request, address_id):
        pass


class CustomerAddressDeleteView(TemplateView):
    def post(self, request, address_id):
        pass


class CustomerCartView(TemplateView):
    def get(self, request):
        template_name = 'cart/list.html'

        carts = Cart.objects.filter(user_id=request.user.pk)

        context={}
        context['carts']=carts

        return render(request, template_name=template_name, context=context)

    def post(self, request):
        pass


class CustomerOrderView(TemplateView):
    def get(self, request):
        orders = Order.objects.filter(user_id = request.user.pk)

        template_name = 'orders/list.html'

        return render(request, template_name=template_name, context={'orders':orders})
    def post(self, request):
        pass


class CustomerOrderCreateView(TemplateView):
    def post(self, request, id):
        pass


class CustomerStoreView(TemplateView):
    def get(self, request):
        pass

    def post(self, request):
        pass


class CustomerStoreDetailView(TemplateView):
    def get(self, request, stores_id):
        pass


class CustomerStoreMenuView(TemplateView):
    def get(self, request, stores_id):
        pass


class CustomerMenuDetailView(TemplateView):
    def get(self, request, stores_id, menus_id):
        pass

    def post(self, request, stores_id, menus_id):
        pass


class CustomerCategoryView(TemplateView):
    def get(self, request):
        pass

    def post(self, request):
        pass


class CustomerCategoryDetailView(TemplateView):
    def get(self, request, category_id):
        pass

    def post(self, request, category_id):
        pass


class CustomerOrderDetailView(TemplateView):
    def get(self, request, order_id):
        template_name = 'orders/detail.html'
        context = {}
        order = Order.objects.filter(id=order_id)
        context['order'] = order
        context['order_id'] = order_id

        return render(request, template_name=template_name, context=context)


class CustomerPaymentView(TemplateView):
    
    def get(self, request, order_id):
        template_name = 'payment/process.html'
        context = {}
        context['order'] = Order.objects.filter(id=order_id)
        return render(request, template_name=template_name, context=context)

    def post(self, request, order_id):
        STRIPE_PUBLISHABLE_KEY = 'pk_test_51NepG5B0fn5K1LetaHTmMbzoTXQ8oVIqghksgr3HS21HzwzvpqqtOcQz3AVjGfAL9T6aDYrqcyphrKWLPJPGbAcu001cqd6x1W' # Publishable key
        STRIPE_SECRET_KEY = 'sk_test_51NepG5B0fn5K1Letc3oqiMEoxefEIr5HFD7NmjrGU7OhEpSleomv9dyjDnXYXmEbpHN0ubd80ucwSmXfrrfpUdzN00VmZDl1tX' # Secret key
        STRIPE_API_VERSION = '2023-08-16'

        stripe.api_key = STRIPE_SECRET_KEY
        stripe.api_version = STRIPE_API_VERSION

        success_url = request.build_absolute_uri('/customer/pay_complete')
        cancel_url = request.build_absolute_uri('/customer/pay_cancle')

        session_data = {
            'mode': 'payment',
            'client_reference_id': 1,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }

        
        session_data['line_items'].append({
            'price_data': {
                'unit_amount': int(15 * Decimal(100)),
                'currency': 'usd',
                'product_data': {
                    'name': '후라이드',
                }
            },
            'quantity': 2,
        })

        checkout_session = stripe.checkout.Session.create(**session_data)
        return redirect(checkout_session.url, code=303)


class CustomerPayCompletedView(TemplateView):
    def get(self, request):
        template_name = 'payment/complete.html'

        return render(request, template_name=template_name)

class CustomerPayCancleView(TemplateView):
    def get(self, request):
        template_name = 'payment/cancle.html'
        
        return render(request, template_name=template_name)