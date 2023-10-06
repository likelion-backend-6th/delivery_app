from django.urls import path
from .views import *
from .webhook import *

app_name = "customer"

urlpatterns = [
    path("home/", CustomerHomeView.as_view(), name="customer_home"),
    # path(
    #     "home?category=<int:category_id>/",
    #     CustomerSearchCategoryView.as_view(),
    #     name="search_category",
    # ),
    path("address/", CustomerAddressView.as_view(), name="customer_address"),
    path("address/add/", CustomerAddressAddView.as_view(), name="customer_address_add"),
    path(
        "address/<int:address_id>/",
        CustomerAddressDetailView.as_view(),
        name="customer_address_detail",
    ),
    path(
        "address/<int:address_id>/edit/",
        CustomerAddressEditView.as_view(),
        name="customer_address_edit",
    ),
    path(
        "address/<int:address_id>/delete/",
        CustomerAddressDeleteView.as_view(),
        name="customer_address_delete",
    ),
    path("cart/", CustomerCartView.as_view(), name="customer_cart"),
    path("orders/", CustomerOrderView.as_view(), name="customer_orders"),
    path(
        "<int:customer_id>/order_create/",
        CustomerOrderCreateView.as_view(),
        name="customer_order_create",
    ),
    path("store/", CustomerStoreView.as_view(), name="store"),
    path(
        "store/<int:store_id>/", CustomerStoreDetailView.as_view(), name="store_detail"
    ),
    path(
        "store/<int:store_id>/menu/", CustomerStoreMenuView.as_view(), name="store_menu"
    ),
    path(
        "store/<int:store_id>/menu/<int:menu_id>/",
        CustomerMenuDetailView.as_view(),
        name="customer_menu_detail",
    ),
    path("category/", CustomerCategoryView.as_view(), name="customer_category"),
    path(
        "category/<int:category_id>/",
        CustomerCategoryDetailView.as_view(),
        name="category_detail",
    ),
    path(
        "order/<int:order_id>/",
        CustomerOrderDetailView.as_view(),
        name="customer_order_detail",
    ),
    path("payment/<int:order_id>", CustomerPaymentView.as_view(), name="customer_payment"),
    path("pay_complete/", CustomerPayCompletedView.as_view(), name="customer_pay_complete",
    ),
    path("pay_cancel/", CustomerPayCancleView.as_view(), name="customer_pay_calcle"),
    path("payment/webhook", stripe_webhook, name='stripe-webhook'), 
]
