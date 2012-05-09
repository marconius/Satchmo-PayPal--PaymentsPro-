from decimal import Decimal
from paypal.pro.models import PayPalNVP
from satchmo_store.shop.models import Order, OrderPayment, OrderAuthorization, OrderPaymentFailure
from livesettings import config_get_group

def payment_authorized(sender, **kwargs):
    pp_nvp = PayPalNVP.objects.filter(invnum=sender['invnum']).latest('timestamp')
    response_params = dict(
        [part.split('=') for part in pp_nvp.response.split('&')])
    query_params = dict(
        [part.split('=') for part in pp_nvp.query.split('&')])
    
    order = Order.objects.get(id=pp_nvp.invnum)
    #payment_module = config_get_group('PAYMENT_PAYMENTSPRO')
    
    if pp_nvp.method == "DoExpressCheckoutPayment":
        details = "Express Checkout"
    else:
        details = query_params['creditcardtype']
    
    op = OrderAuthorization(
        order = order,
        payment = "PAYMENTSPRO",
        amount = Decimal(response_params['amt']),
        time_stamp = pp_nvp.timestamp,
        transaction_id = response_params['transactionid'],
        details = details,
        reason_code = "",
        )
    op.save()
        
'''
def payment_was_flagged(sender, **kwargs):
    pp_nvp = PayPalNVP.objects.filter(invnum=sender['invnum']).latest('timestamp')
    response_params = dict(
        [part.split('=') for part in pp_nvp.response.split('&')])
    query_params = dict(
        [part.split('=') for part in pp_nvp.query.split('&')])
    
    order = Order.objects.get(id=pp_nvp.invnum)
    #payment_module = config_get_group('PAYMENT_PAYMENTSPRO')
    
    of = OrderPaymentFailure(
        order = order,
        payment = "PAYMENTSPRO",
        amount = Decimal(response_params['amt']),
        time_stamp = pp_nvp.timestamp,
        transaction_id = response_params['transactionid'],
        details = query_params['creditcardtype'],
        reason_code = "error code",
        )
    of.save()
'''
