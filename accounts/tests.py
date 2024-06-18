# accounts/tests/test_email.py

from django.core import mail
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.test import TestCase

from accounts.models import Account  # Adjust the import according to your app structure


class EmailTest(TestCase):
    def setup(self):
        # Create a user with a potentially malicious first name
        self.user = Account.objects.create(
            first_name="<script>alert('XSS');</script>",
            last_name="Test",
            username="testuser",
            email="test@example.com",
            phone_number="1234567890",
            date_joined=datetime.now(),
            last_login=datetime.now(),
            is_admin=False,
            is_staff=False,
            is_active=True,
            is_super_admin=False,
        )

    def test_email_content(self):
        self.assertEqual(2, 4 / 2)
        print("test completed")
        # Render the email content

        user = Account.objects.get(email="test@example.com")
        self.assertEqual(user.first_name, "<script>alert('XSS');</script>")
        #
        # subject = "Account Activation"
        # message = render_to_string(
        #     'accounts/account_verification_email.html',
        #     {'user': self.user, 'activation_link': 'http://example.com/activate'}
        # )
        #
        # # Send the email
        # send_mail(subject, message, 'from@example.com', [self.user.email])
        #
        # # Check that one message has been sent
        # self.assertEqual(len(mail.outbox), 1)
        #
        # # Get the email content
        # email = mail.outbox[0]
        #
        # # Print the email content to inspect manually
        # print(email.body)
        #
        # # Check if the script tag is present in the email body
        # self.assertIn("<script>alert('XSS');</script>", email.body)
        #
        # # Optionally, write the email content to a file for manual inspection
        # with open("test_email_output.html", "w") as f:
        #     f.write(email.body)
