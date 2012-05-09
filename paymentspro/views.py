"""Simple wrapper for standard checkout as implemented in payment.views"""
import logging
from decimal import Decimal
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.conf import settings
from livesettings import config_get_group, config_value, config_value_safe
from payment.views import confirm, payship
from paypal.pro.views import PayPalPro
from satchmo_utils.views import bad_or_missing
from satchmo_store.shop.models import Cart, Order, OrderPayment, Config
from satchmo_utils.dynamic import lookup_url
from payment.utils import get_processor_by_key
from payment.forms import SimplePayShipForm, _get_shipping_choices
from paymentspro.forms import SatchmoPaymentsProPaymentForm
from satchmo_store.contact.models import Contact
from shipping.utils import update_shipping
from canada_tax.processor import Processor

log = logging.getLogger()

STORE_NAME = Config.objects.get_current().store_name
PAYMENT_MODULE = config_get_group('PAYMENT_PAYMENTSPRO')

def pay_ship_info(request, template='shop/checkout/paymentspro/shipping.html'):
    
    results = payship.pay_ship_info_verify(request, PAYMENT_MODULE)
    if not results[0]:
        return results[1]

    contact = results[1]
    working_cart = results[2]

    results = payship.simple_pay_ship_process_form(
        request,
        contact,
        working_cart,
        PAYMENT_MODULE,
        allow_skip=False)
    
    if results[0]:
        return results[1]

    form = results[1]
    return payship.pay_ship_render_form(request, form, template, 
                                        PAYMENT_MODULE, working_cart)
    
pay_ship_info = never_cache(pay_ship_info)
    
def get_payment(request):
    payment_module = config_get_group('PAYMENT_PAYMENTSPRO')
    
    # get necessary order info from satchmo
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return redirect(url)
     
    # now some context hacking:
    order_sub_total = order.sub_total + order.shipping_cost
    
    current_site = Site.objects.get_current().domain
    url = request.build_absolute_uri().split('?')[0]
    if settings.PAYPAL_CHECKOUT_SECURE:
        log.debug("secure paypal checkout")
        url = url.replace('http://', 'https://')
    log.debug("paypal express check out url: {0}".format(url))
    #url = "http://" + current_site + reverse('PAYMENTSPRO_satchmo_checkout-step3')
    
    # === now the django-paypal stuff ===
    
    # Fix of the 0.01 balance problem. 
    # Bug: The payment amount sent to paypal, when formatted to two floating 
    # points, was rounded, but the order.total is not. This would sometimes 
    # cause a balance in 0 < balance < 0.01 which translated to a balance of 
    # 0.01 to remain on the order.
    amt = "{0:.2f}".format(order.total)
    diff = order.total - Decimal(amt)
    if diff > Decimal("0") and diff < Decimal("0.01"):
        order.total = Decimal(amt)
        order.save()
    
    item = {
        "amt": amt,
        "invnum": order.id,
        "cancelurl": url,
        "returnurl": url,
        "currencycode": payment_module.CURRENCY_CODE.value,
        "paymentaction": "Authorization",
        }
    
    kw = { 
        "item": item,
        "payment_form_cls": SatchmoPaymentsProPaymentForm,
        "payment_template": "shop/checkout/paymentspro/payment.html",
        "confirm_template": "shop/checkout/paymentspro/confirm.html",
        "success_url": lookup_url(payment_module, 
                                  'satchmo_checkout-success'),
        "context": {"order": order, "order_sub_total": order_sub_total }}
    
    
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
    order.add_status(status='New', notes=_("Order placed on ")+STORE_NAME)
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
