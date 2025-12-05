from decimal import Decimal

from django.test import TestCase

from apps.payment.models import PaymentTransaction, Refund


class PaymentModelUnitTests(TestCase):
    def test_recalculate_refund_status_no_refunds(self):
        p = PaymentTransaction.objects.create(amount=Decimal('50.00'), currency='USD', status=PaymentTransaction.STATUS_SUCCEEDED)
        # no refunds -> refunded_amount 0, status remains succeeded
        p.recalculate_refund_status()
        p.refresh_from_db()
        self.assertEqual(p.refunded_amount, 0)
        self.assertEqual(p.status, PaymentTransaction.STATUS_SUCCEEDED)

    def test_partial_and_full_refunds(self):
        p = PaymentTransaction.objects.create(amount=Decimal('100.00'), currency='USD', status=PaymentTransaction.STATUS_SUCCEEDED)
        # create a succeeded refund of 30
        r1 = Refund.objects.create(payment=p, amount=Decimal('30.00'), status=Refund.STATUS_SUCCEEDED)
        p.recalculate_refund_status()
        p.refresh_from_db()
        self.assertEqual(p.refunded_amount, Decimal('30.00'))
        self.assertEqual(p.status, PaymentTransaction.STATUS_PARTIALLY_REFUNDED)

        # add another refund to reach total
        r2 = Refund.objects.create(payment=p, amount=Decimal('70.00'), status=Refund.STATUS_SUCCEEDED)
        p.recalculate_refund_status()
        p.refresh_from_db()
        self.assertEqual(p.refunded_amount, Decimal('100.00'))
        self.assertEqual(p.status, PaymentTransaction.STATUS_REFUNDED)
