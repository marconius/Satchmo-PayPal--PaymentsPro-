from livesettings import *
from django.utils.translation import ugettext_lazy as _

# this is so that the translation utility will pick up the string
gettext = lambda s: s

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_PAYMENTSPRO',
    _('PayPal Payments Pro Module Settings'),
    ordering = 102)

config_register_list(
    StringValue(PAYMENT_GROUP,
        'CURRENCY_CODE',
        description=_('Currency Code'),
        help_text=_('Currency code for Paypal transactions.'),
        default = 'CAD'),

    StringValue(PAYMENT_GROUP,
        'POST_URL',
        description=_('Post URL'),
        help_text=_('The Paypal URL for real transaction posting.'),
        default="https://www.paypal.com/cgi-bin/webscr"),

    StringValue(PAYMENT_GROUP,
        'POST_TEST_URL',
        description=_('Post URL'),
        help_text=_('The Paypal URL for test transaction posting.'),
        default="https://www.sandbox.paypal.com/cgi-bin/webscr"),

    StringValue(PAYMENT_GROUP,
        'BUSINESS',
        description=_('Paypal account email'),
        help_text=_('The email address for your paypal account'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'BUSINESS_TEST',
        description=_('Paypal test account email'),
        help_text=_('The email address for testing your paypal account'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'API_USER',
        description=_('Paypal API username'),
        help_text=_('The API username as it appears in your API credentials'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'API_USER_TEST',
        description=_('Paypal sandbox API user name'),
        help_text=_('The API username as it appears in your sandbox API credentials'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'API_PASSWORD',
        description=_('Paypal API password'),
        help_text=_('The API password as it appears in your API credentials'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'API_PASSWORD_TEST',
        description=_('Paypal sandbox API password'),
        help_text=_('The API password as it appears in your sandbox API credentials'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'API_SIGNATURE',
        description=_('Paypal API signature'),
        help_text=_('The signature as it appears in your API credentials'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'API_SIGNATURE_TEST',
        description=_('Paypal sandbox API signature'),
        help_text=_('The signature as it appears in your sandbox API credentials'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'RETURN_ADDRESS',
        description=_('Return URL'),
        help_text=_('Where Paypal will return the customer after the purchase is complete.  This can be a named url and defaults to the standard checkout success.'),
        default="satchmo_checkout-success"),

    BooleanValue(PAYMENT_GROUP,
        'LIVE',
        description=_("Accept real payments"),
        help_text=_("False if you want to be in test mode"),
        default=False),

    ModuleValue(PAYMENT_GROUP,
        'MODULE',
        description=_('Implementation module'),
        hidden=True,
        default = 'payment.modules.paypal'),

    StringValue(PAYMENT_GROUP,
        'KEY',
        description=_("Module key"),
        hidden=True,
        default = 'PAYMENTSPRO'),

    StringValue(PAYMENT_GROUP,
        'LABEL',
        description=_('English name for this group on the checkout screens'),
        default = 'PayPal Payments Pro',
        dummy = _('PayPal Payments Pro'), # Force this to appear on po-files
        help_text = _('This will be passed to the translation utility')),


    StringValue(PAYMENT_GROUP,
        'URL_BASE',
        description=_('The url base used for constructing urlpatterns which will use this module'),
        default = '^pppro/'),

    BooleanValue(PAYMENT_GROUP,
        'EXTRA_LOGGING',
        description=_("Verbose logs"),
        help_text=_("Add extensive logs during post."),
        default=False)
)

PAYMENT_GROUP['TEMPLATE_OVERRIDES'] = {
    'shop/checkout/confirm.html' : 'shop/checkout/paymentspro/confirm.html',
}
