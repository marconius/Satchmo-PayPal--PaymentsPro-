from django import forms
from django.utils.translation import ugettext as _
from livesettings import config_get_group, config_value
from paypal.pro.forms import PaymentForm
from payment.forms import SimplePayShipForm
from satchmo_store.shop.models import Order

class SatchmoPaymentsProPaymentForm(PaymentForm):
    '''
    TODO: The ideal is to merge the paypal.pro PaymentForm and the 
    satchmo.payment SimplePayShipForm into this here child form. The 
    problem is that those two are incompatible as SimplePayShipForm 
    requires request and pro does not pass request to the form.
    
    One way around having to force these two to play nice may be to 
    seperate pay_ship into ship-then-pay, so that the client chooses the 
    shipping method before advancing to the payment view. 
    
    Another way is to fork django-paypal and use its gizzards to build
    a proper satchmo payment module ourselves. this works, because django-
    paypal is not being worked too much
    '''
    notes = forms.CharField(widget=forms.Textarea, 
                            label=_("Special Instructions"),
                            required=False)
    
    def __init__(self, *args, **kwargs):
        super(SatchmoPaymentsProPaymentForm, self).__init__(*args, **kwargs)
        self.fields['countrycode'].initial = 'CA'
    
    def process(self, request, item):
        order = Order.objects.from_request(request)
        order.notes = self.cleaned_data['notes']
        print order
        order.save()
        return super(SatchmoPaymentsProPaymentForm, self).process(request, item)
