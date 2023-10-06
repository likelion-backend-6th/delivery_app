from django.contrib.auth.models import User
from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart
from sajjang.models import Category, Stores, Menus, Address
from django.views.generic import TemplateView
from django.http import JsonResponse
import stripe
from decimal import Decimal

# Create your views here.


class CustomerHomeView(TemplateView):
    template_name = "home.html"

    def get(self, request):
        category_query = request.GET.get("category", None)
        categories = Category.objects.all()
        if category_query:
            stores = Stores.objects.filter(category_id=category_query)
        else:
            stores = Stores.objects.all()

        return render(
            request,
            template_name="home.html",
            context={"categories": categories, "stores": stores},
        )


# 미완성
class CustomerSearchCategoryView(TemplateView):
    template_name = "category/category.html"

    def get(self, request, category_id):
        category = Category.objects.get(id=category_id)
        stores = Stores.objects.get(id=category_id)


class CustomerAddressView(TemplateView):
    template_name = "address/search.html"

    def get(self, request):
        addresses = Address.objects.all()
        context = {"addresses": addresses}
        return render(request, self.template_name, context)


class CustomerAddressAddView(TemplateView):
    template_name = "address/add.html"

    def get(self, request, category_id):
        addresses = Address.objects.all()
        context = {"addresses": addresses}
        return render(request, self.template_name, context)

    def post(self, request):
        try:
            user_id = User.object.get(id=user_id)
            address_name = request.POST["address_name"]
            address = request.POST["address"]
            is_default = request.POST["is_default"]
            new_address = Address(
                address_name=address_name,
                address=address,
                is_default=is_default,
            )
            new_address.save()
            return redirect("customer_address")
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class CustomerAddressDetailView(TemplateView):
    template_name = "address/detail.html"

    def get(self, request, address_id):
        address = get_object_or_404(Address, id=address_id)
        context = {"address": address}
        return render(request, self.template_name, context)


class CustomerAddressEditView(TemplateView):
    template_name = "address/edit.html"

    def get(self, request, address_id):
        address = get_object_or_404(Address, id=address_id)
        context = {"address": address}
        return render(request, self.template_name, context)

    def post(self, request, address_id):
        try:
            address = get_object_or_404(Address, id=address_id)
            address.address_name = request.POST["address_name"]
            address.address = request.POST["address"]
            address.is_default = request.POST["is_default"]
            address.save()
            return redirect("customer_address_detail", address_id=address_id)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class CustomerAddressDeleteView(TemplateView):
    def post(self, request, address_id):
        delete_address = Address.objects.get(id=address_id)
        delete_address.delete()

        return redirect("customer_address")


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

# /customer/store/
class CustomerStoreView(TemplateView):
    def get(self, request):
        pass

    def post(self, request):
        pass

# /customer/store/<int:store_id>
class CustomerStoreDetailView(TemplateView):
    template_name = 'store/detail.html'

    def get(self, request, store_id):
        store = get_object_or_404(Stores, id=store_id)
        context = {"store": store}      
        return render(request, self.template_name, context)

# /customer/store/<int:store_id>/menu/
class CustomerStoreMenuView(TemplateView):
    template_name = 'store/menu/list.html'

    def get(self, request, store_id):
        store = get_object_or_404(Stores, id=store_id)
        menus = Menus.objects.filter(store_id=store_id)
        context = {"store": store, "menus": menus}
        return render(request, self.template_name, context)

# /customer/store/<int:stores_id>/menu/{menus_id}
class CustomerMenuDetailView(TemplateView):
    template_name = 'store/menu/detail.html'

    def get(self, request, store_id, menu_id):
        menu = get_object_or_404(Menus, id=menu_id)
        context = {"menu": menu}
        return render(request, self.template_name, context)

    def post(self, request, store_id, menu_id):
        try:
            quantity = request.POST.get('quantity')
            unit_price = request.POST.get('unit_price')
            
            store = get_object_or_404(Stores, id=store_id)
            menu = get_object_or_404(Menus, id=menu_id)

            cart_item = Cart(
                user_id=request.user.pk,
                stores_id=store,
                menus_id=menu,
                order_id=None,
                quantity=quantity,
                unit_price=unit_price
            )
            cart_item.save()
            return redirect("store_menu", store_id=store_id)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# customer/category/
class CustomerCategoryView(TemplateView):
    template_name = "category/category.html"
    
    def get(self, request):
        categories = Category.objects.all()
        context = {"categories": categories}
        return render(request, self.template_name, context)

# customer/category/<int:category_id>
class CustomerCategoryDetailView(TemplateView):
    template_name = "category/category.html"
    
    def get(self, request, category_id):
        category = Category.objects.filter(id=category_id)
        stores = Stores.objects.filter(category_id=category_id)
        context = {"category": category, "stores": stores}
        return render(request, self.template_name, context)


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