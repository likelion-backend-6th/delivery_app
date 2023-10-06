import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from sajjang.models import Order

STRIPE_WEBHOOK_SECRET = 'whsec_b2a4441cadc078bd977e0be749b5fdb4dcef55354181e99a8ff5785481a04064'

@csrf_exempt
def stripe_webhook(requset):
    

    payload = requset.body
    sig_header = requset.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                print("Webhook function active")
                Order.objects.get()
            except Order.DoesNotExist:
                return HttpResponse(status=404)
            
    return HttpResponse(status=200)