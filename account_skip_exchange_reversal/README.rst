.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License LGPL-3

Account Skip Exchange Reversal
==============================
This modules avoid the reversal journal entries creation of currency exchange rate difference when a payment is removed from an invoice

Usage
=====
On account config settings you can configure the parameter named "skip_currency_exchange_difference_reversal".
If this parameter is selected when a invoice full reconciled is ureconciled the currency exchange journal entry (if exists)
will be removed.

Credits
=======

Contributors
------------

* Oscar Ulises Garza Córdova <oscar.garza@jarsa.com.mx>


Maintainer
----------

.. image:: http://www.jarsa.com.mx/logo.png
   :alt: Jarsa Sistemas, S.A. de C.V.
   :target: http://www.jarsa.com.mx

This module is maintained by the Jarsa Sistemas.
