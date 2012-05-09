from django.conf.urls.defaults import patterns, include
from satchmo_store.shop.satchmo_settings import get_satchmo_setting

ssl = get_satchmo_setting('SSL', default_value=False)

urlpatterns = patterns('',
    (r'^shipping/$', 'paymentspro.views.pay_ship_info', {'SSL':ssl}, 'PAYMENTSPRO_satchmo_checkout-step2'),
    (r'^payment/$', 'paymentspro.views.get_payment', {'SSL':ssl}, 'PAYMENTSPRO_satchmo_checkout-step3'),
    (r'^success/$', 'paymentspro.views.success', {'SSL':ssl}, 'PAYMENTSPRO_satchmo_checkout-success'),
    (r'^instant/payment/notification/', include('paypal.standard.ipn.urls')),
)
