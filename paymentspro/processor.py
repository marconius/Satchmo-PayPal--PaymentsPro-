"""
All processing done by django-paypal in views
"""
from django.utils.translation import ugettext_lazy as _
from payment.modules.base import BasePaymentProcessor, ProcessorResult

class PaymentProcessor(BasePaymentProcessor):

    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('paymentspro', settings)
    
    def capture_payment(self, testing=False, amount=None):
        """
        Process the payment in Satchmo
        """
        orderpayment = self.record_payment(amount=amount, reason_code="0")
        return ProcessorResult(self.key, True, _('Success'), orderpayment)
