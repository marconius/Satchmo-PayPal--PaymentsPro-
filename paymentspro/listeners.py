from decimal import Decimal
from paypal.pro.models import PayPalNVP
from satchmo_store.shop.models import Order, OrderPayment
from livesettings import config_get_group

def payment_authorized(sender, **kwargs):
    pp_nvp = PayPalNVP.objects.get(invnum=sender['invnum'])
    response_params = dict(
        [part.split('=') for part in pp_nvp.response.split('&')])
    order = Order.objects.get(id=pp_nvp.invnum)
    payment_module = config_get_group('PAYMENT_PAYMENTSPRO')
    
    op = OrderPayment(
        order = order,
        payment = "PAYMENTSPRO",
        amount = Decimal(response_params['amt']),
        time_stamp = pp_nvp.timestamp,
        transaction_id = response_params['transactionid'],
        details = "",
        reason_code = "",
        )
    op.save()
        

