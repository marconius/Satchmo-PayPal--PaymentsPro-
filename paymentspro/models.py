import config
from paypal.pro.signals import payment_was_successful
from paymentspro.listeners import payment_authorized

PAYMENT_PROCESSOR=True

payment_was_successful.connect(payment_authorized)
