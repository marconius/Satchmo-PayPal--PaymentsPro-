"""Simple wrapper for standard checkout as implemented in payment.views"""
import logging
from decimal import Decimal
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from livesettings import config_get_group, config_value
from payment.views import confirm, payship
from paypal.pro.views import PayPalPro
from satchmo_utils.views import bad_or_missing
from satchmo_store.shop.models import Cart, Order, OrderPayment, Config
from satchmo_utils.dynamic import lookup_url
from payment.utils import get_processor_by_key

log = logging.getLogger()
STORE_NAME = Config.objects.get_current().store_name

def pay_ship_info(request):
    payment_module = config_get_group('PAYMENT_PAYMENTSPRO')
    
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return redirect(url)
    
    item = {
        "amt": "%.2f" % order.total,
        "invnum": order.id,
        "cancelurl": lookup_url(payment_module, 'satchmo_checkout-step1'),
        "returnurl": payment_module.RETURN_ADDRESS.value,
        "currencycode": payment_module.CURRENCY_CODE.value,
        }
    
    kw = { "item": item,
           "payment_template": "shop/checkout/paymentspro/pay_ship.html",
           "confirm_template": "shop/checkout/paymentspro/confirm.html",
           "success_url": lookup_url(payment_module, 
                                     'PAYMENTS_PRO_satchmo_checkout-success'),
         }
    
    ppp = PayPalPro(**kw)
    return ppp(request)
pay_ship_info = never_cache(pay_ship_info)

def success(request):
    """
    The order has been succesfully processed.
    """    
    
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        return bad_or_missing(request, _('Your order has already been processed.'))
    
    # register the transaction
    order.add_status(status='New', notes=_("Paid on ")+STORE_NAME)
    #processor = get_processor_by_key('PAYMENT_PAYMENTSPRO')
    #payment = processor.record_payment(order=order, amount=gross, transaction_id=txn_id)
    
    
    # Added to track total sold for each product
    for item in order.orderitem_set.all():
        product = item.product
        product.total_sold += item.quantity
        product.items_in_stock -= item.quantity
        product.save()

    # Clean up cart now, (TODO:the rest of the order will be cleaned on paypal IPN)
    #for cart in Cart.objects.filter(customer=order.contact):
    #    cart.empty()
    cart = Cart.objects.from_request(request)
    cart.empty()

    del request.session['orderID']
    context = RequestContext(request, {'order': order})
    return render_to_response('shop/checkout/success.html', context)
success = never_cache(success)
