from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.db.models import Subquery
from django.contrib.auth.models import Group, User
from django.core.serializers import serialize

from sajjang.models import DeliveryHistory, RejectedOrder
from sajjang.models import Order, Stores
from delivery_crew.models import DeliveryLocation
from common.utils import DeliveryCrewRequiredMixin

import requests


# delivery_crew/home
class DeliveryCrewHomeView(DeliveryCrewRequiredMixin, TemplateView):
    template_name = "/app/delivery_crew/templates/home.html"

    def get(self, request):
        crew_active_area = None
        crew_deactivate_area = None
        try:
            crew_locations = DeliveryLocation.objects.filter(user_id=request.user.pk)

            for location in crew_locations:
                if location.active_area:
                    crew_active_area = location.address.split(" ")[1]
                else:
                    crew_deactivate_area = location.address.split(" ")[1]

            print("crew_active_area", crew_active_area)

            orders = (
                Order.objects.filter(order_status="sajjang_accepted")
                .exclude(crew_rejected_order=request.user.id)
                .filter(store_id__address__icontains=crew_active_area)
            )
            # orders = Order.objects.filter(order_status="sajjang_accepted").exclude(
            #     crew_rejected_order=request.user.id
            # )
        except Exception as e:
            print(e)

            orders = Order.objects.filter(order_status="sajjang_accepted").exclude(
                crew_rejected_order=request.user.id
            )

        stores = Stores.objects.filter(id__in=Subquery(orders.values("store_id")))

        context = {
            "orders": orders,
            "orders_JSON": serialize("json", orders),
            "stores": stores,
            "my_locations": crew_locations,
            "address_a": crew_active_area,
            "address_b": crew_deactivate_area,
        }
        return render(request, self.template_name, context)


# delivery_crew/address
class DeliveryCrewAddressView(DeliveryCrewRequiredMixin, TemplateView):
    template_name = "/app/delivery_crew/templates/address/search.html"

    def get(self, request):
        addresses = DeliveryLocation.objects.filter(user_id=request.user.pk).order_by(
            "-active_area"
        )
        context = {"addresses": addresses}
        return render(request, self.template_name, context)


# delivery_crew/address/add
class DeliveryCrewAddressAddView(DeliveryCrewRequiredMixin, TemplateView):
    template_name = "/app/delivery_crew/templates/address/add.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        try:
            user = User.objects.get(id=request.user.pk)
            address_name = request.POST["address_name"]
            postcode = request.POST["postcode"]
            base_address = request.POST["address"]
            detail_address = request.POST["detailAddress"]
            extra_address = request.POST["extraAddress"]
            active_area = request.POST.get("active_area", None)

            if active_area:
                active_area = True
            else:
                active_area = False

            new_location = DeliveryLocation(
                delivery_crew_id=user,
                address_name=address_name,
                address=f"{base_address}, {detail_address} {extra_address}",
                postcode=postcode,
                base_address=base_address,
                detail_address=detail_address,
                extra_address=extra_address,
                active_area=active_area,
            )
            new_location.save()

            if active_area:
                new_location.set_is_default()

            return redirect("delivery_crew:delivery_crew_address")
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# /delivery_crew/address/<int:address_id>
class DeliveryCrewAddressDetailView(DeliveryCrewRequiredMixin, TemplateView):
    template_name = "/app/delivery_crew/templates/address/detail.html"

    def get(self, request, address_id):
        address = get_object_or_404(DeliveryLocation, id=address_id)
        print("address", address)
        context = {"address": address}
        return render(request, self.template_name, context)


# /delivery_crew/address/<int:address_id>/edit
class DeliveryCrewAddressEditView(DeliveryCrewRequiredMixin, TemplateView):
    template_name = "/app/delivery_crew/templates/address/edit.html"

    def get(self, request, address_id):
        address = get_object_or_404(DeliveryLocation, id=address_id)
        context = {"address": address}
        return render(request, self.template_name, context)

    def post(self, request, address_id):
        try:
            address = get_object_or_404(DeliveryLocation, id=address_id)
            address.address_name = request.POST["address_name"]
            address.address = f"{request.POST['address']}, {request.POST['detailAddress']} {request.POST['extraAddress']}"
            address.postcode = request.POST["postcode"]
            address.base_address = request.POST["address"]
            address.detail_address = request.POST["detailAddress"]
            address.extra_address = request.POST["extraAddress"]
            try:
                active_area = request.POST["active_area"]
                print("active_area", active_area)
                if active_area == "on":
                    address.set_is_default()
                else:
                    address.active_area = False
                    address.save()

            except Exception as e:
                address.active_area = False
                address.save()

            return redirect(
                "delivery_crew:delivery_crew_address_detail", address_id=address_id
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# /delivery_crew/address/<int:address_id>/delete
class DeliveryCrewAddressDeleteView(DeliveryCrewRequiredMixin, TemplateView):
    template_name = "/app/delivery_crew/templates/address/detail.html"

    def post(self, request, address_id):
        delete_address = DeliveryLocation.objects.get(id=address_id)
        delete_address.delete()
        return redirect("delivery_crew:delivery_crew_address")


class DeliveryCrewDeliveryHistory(DeliveryCrewRequiredMixin, TemplateView):
    template_name = "/app/delivery_crew/templates/history.html"

    def get(self, request):
        order_history = DeliveryHistory.objects.filter(delivery_crew_id=request.user.id)
        print(order_history)
        context = {"order_histories": order_history}
        return render(request, self.template_name, context)


class DeliveryHistoryDetailView(DeliveryCrewRequiredMixin, TemplateView):
    template_name = "/app/delivery_crew/templates/history_detail.html"

    def get(self, request, order_id):
        def get_location_by_address(address):
            url = "https://apis.openapi.sk.com/tmap/pois?version=1&format=json&callback=result"
            params = {
                "appKey": "kyUPwz0Ly2aplTsQ72YKp2EjfDwbI0EJ9KFRwUA4",
                "searchKeyword": address,
                "resCoordType": "WGS84GEO",
                "reqCoordType": "WGS84GEO",
                "count": 1,
            }
            resp = requests.get(url, params=params).json()
            addrInfo = resp["searchPoiInfo"]["pois"]["poi"][0]["newAddressList"][
                "newAddress"
            ][0]
            return (addrInfo["centerLon"], addrInfo["centerLat"])

        order = get_object_or_404(Order, id=order_id)
        context = {"order": order}
        store_address = order.store_id.address
        cus_address = order.address_id.address

        context["store_addrLon"], context["store_addrLat"] = get_location_by_address(
            store_address
        )
        context["cus_addrLon"], context["cus_addrLat"] = get_location_by_address(
            cus_address
        )

        return render(request, self.template_name, context)

    def post(self, request, order_id):
        pass


class DeliveryCrewDeliveryHistoryPickUp(DeliveryCrewRequiredMixin, TemplateView):
    def post(self, request, order_id):
        def get_location_by_address(address):
            url = "https://apis.openapi.sk.com/tmap/pois?version=1&format=json&callback=result"
            params = {
                "appKey": "kyUPwz0Ly2aplTsQ72YKp2EjfDwbI0EJ9KFRwUA4",
                "searchKeyword": address,
                "resCoordType": "WGS84GEO",
                "reqCoordType": "WGS84GEO",
                "count": 1,
            }
            resp = requests.get(url, params=params).json()
            addrInfo = resp["searchPoiInfo"]["pois"]["poi"][0]["newAddressList"][
                "newAddress"
            ][0]
            return (addrInfo["centerLon"], addrInfo["centerLat"])

        def get_eta(store_loaction, cus_location):
            url = "https://apis.openapi.sk.com/tmap/routes?version=3&format=json"
            headers = {"appKey": "kyUPwz0Ly2aplTsQ72YKp2EjfDwbI0EJ9KFRwUA4"}
            data = {
                "startX": store_loaction[0],
                "startY": store_loaction[1],
                "endX": cus_location[0],
                "endY": cus_location[1],
                "reqCoordType": "WGS84GEO",
                "resCoordType": "WGS84GEO",
                "searchOption": "0",
                "trafficInfo": "Y",
                "carType": 7,
                "totalValue": 2,
            }
            resp = requests.post(url, headers=headers, data=data).json()
            eta = resp["features"][0]["properties"]["totalTime"] // 60

            return (10 * (eta // 10)) + 10  # 배달원의 여유시간을 주기 위해 1의 자리 숫자를 없앤 후 10분 추가

        delivery = get_object_or_404(Order, id=order_id)

        store_address = delivery.store_id.address
        store_location = get_location_by_address(store_address)

        cus_address = delivery.address_id.address
        cus_location = get_location_by_address(cus_address)

        eta = get_eta(store_location, cus_location)
        delivery.eta = eta
        delivery.order_status = "delivery_in_progress"
        delivery.save()

        return redirect("delivery_crew:delivery_crew_history")


class DeliveryCrewDeliveryHistoryComplete(DeliveryCrewRequiredMixin, TemplateView):
    def post(self, request, order_id):
        delivery = get_object_or_404(Order, id=order_id)
        delivery.order_status = "delivered"
        delivery.save()
        return redirect("delivery_crew:delivery_crew_history")


class DeliveryCrewAcceptView(DeliveryCrewRequiredMixin, TemplateView):
    # template_name = "/app/delivery_crew/templates/home.html"

    def post(self, request, order_id):
        delivery = get_object_or_404(Order, id=order_id)
        delivery_crew = get_object_or_404(User, id=request.user.id)

        new_order_history = DeliveryHistory.objects.create(
            delivery_crew_id=delivery_crew, order_id=delivery
        )
        delivery.order_status = "crew_accepted"
        delivery.save()
        new_order_history.save()

        return redirect("delivery_crew:delivery_crew_home")


class DeliveryCrewDenyView(DeliveryCrewRequiredMixin, TemplateView):
    # template_name = "/app/delivery_crew/templates/home.html"

    def post(self, request, order_id):
        delivery_order = get_object_or_404(Order, id=order_id)
        delivery_crew = get_object_or_404(User, id=request.user.id)

        reject = RejectedOrder.objects.create(
            delivery_crew_id=delivery_crew, order_id=delivery_order
        )

        reject.save()

        return redirect("delivery_crew:delivery_crew_home")


class DeliveryCrewAlarmView(DeliveryCrewRequiredMixin, TemplateView):
    # template_name = "/app/delivery_crew/templates/home.html"

    def get(self, request, user_id, **kwargs):
        pending_deliveries = Order.objects.filter(order_status="sajjang_accepted")
        context = super().get_context_data(**kwargs)
        context["pending_deliveries"] = pending_deliveries
        return context

    def render_to_response(self, context, **response_kwargs):
        # AJAX 요청의 응답으로 JSON 데이터 반환
        pending_deliveries = context["pending_deliveries"]
        alerts_html = render_to_string(
            "delivery_crew/alert_list.html", {"pending_deliveries": pending_deliveries}
        )
        return JsonResponse({"html": alerts_html})
