from django.contrib.auth import get_user_model
from django.test import TestCase, client

from registration import forms

class RegistrationFormTests(TestCase):
    """
    Test the default registration forms.

    """
    def setUp(self):
        self.factory = client.RequestFactory()
    def test_form_validation(self):
        """
        Test that ``RegistrationForm`` enforces username constraints
        and matching passwords.

        """
        User = get_user_model()
        request = self.factory.get('') # any request will do!
        # Create a user so we can verify that duplicate usernames aren't permitted.
        User.objects.create_user('alice', 'alice@example.com', 'secret')

        invalid_data_dicts = [
            # Non-alphanumeric username.
            {'data': {'username': 'foo/bar',
                      'email': 'foo@example.com',
                      'password1': 'foo',
                      'password2': 'foo'},
            'error': ('username', [u"This value may contain only letters, numbers and @/./+/-/_ characters."])},
            # Already-existing username.
            {'data': {'username': 'alice',
                      'email': 'alice@example.com',
                      'password1': 'secret',
                      'password2': 'secret'},
            'error': ('username', [u"A user with that username already exists."])},
            # Mismatched passwords.
            {'data': {'username': 'foo',
                      'email': 'foo@example.com',
                      'password1': 'foo',
                      'password2': 'bar'},
            'error': ('password2', [u"The two password fields didn't match."])},
            ]

        for invalid_dict in invalid_data_dicts:
            form = forms.RegistrationForm(request,data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

        form = forms.RegistrationForm(request,data={'username': 'foo',
                                                    'email': 'foo@example.com',
                                                    'password1': 'foo',
                                                    'password2': 'foo'})
        self.failUnless(form.is_valid())

    def test_form_save(self):
        request = self.factory.get('')
        form = forms.RegistrationForm(request,data={'username': 'foo2',
                                                    'email': 'foo2@example.com',
                                                    'password1': 'foo',
                                                    'password2': 'foo'})
        form.is_valid()
        form.save()
        User = get_user_model()
        user = User.objects.get(username="foo2")
        profile = user.registrationprofile
        self.assertNotEqual(profile.activation_key,profile.EMPTY_KEY)
