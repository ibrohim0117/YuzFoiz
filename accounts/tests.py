import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import User

TEMP_MEDIA = tempfile.mkdtemp()

REGISTER = reverse('accounts:register')
LOGIN = reverse('accounts:login')
LOGOUT = reverse('accounts:logout')
PROFILE = reverse('accounts:profile')
PASSWORD = 'Kuchli-parol-2026'


def make_image(name='face.jpg'):
    buf = io.BytesIO()
    Image.new('RGB', (20, 20), 'gray').save(buf, 'JPEG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/jpeg')


class RegisterTests(TestCase):
    def test_all_fields_required(self):
        r = self.client.post(REGISTER, {})
        form = r.context['form']
        for field in ('first_name', 'last_name', 'username', 'password1', 'password2'):
            self.assertIn(field, form.errors, field)
        self.assertFalse(User.objects.exists())

    def test_success_logs_in_and_redirects_to_profile(self):
        r = self.client.post(REGISTER, {
            'first_name': 'Ali', 'last_name': 'Valiyev', 'username': 'ali',
            'password1': PASSWORD, 'password2': PASSWORD,
        })
        self.assertRedirects(r, PROFILE)
        user = User.objects.get(username='ali')
        self.assertEqual((user.first_name, user.last_name), ('Ali', 'Valiyev'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_messages_are_uzbek(self):
        User.objects.create_user('ali', password=PASSWORD)
        r = self.client.post(REGISTER, {
            'first_name': 'A', 'last_name': 'B', 'username': 'ALI',
            'password1': '123', 'password2': '123',
        })
        errors = r.context['form'].errors
        self.assertIn('Bu username band. Boshqasini tanlang.', errors['username'])
        self.assertIn("Parol juda qisqa. Kamida 8 ta belgi bo'lishi kerak.", errors['password2'])


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ali', password=PASSWORD)

    def test_login_success(self):
        r = self.client.post(LOGIN, {'username': 'ali', 'password': PASSWORD})
        self.assertRedirects(r, PROFILE)

    def test_login_wrong_password(self):
        r = self.client.post(LOGIN, {'username': 'ali', 'password': 'xato'})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['form'].non_field_errors())

    def test_login_returns_to_next(self):
        r = self.client.get(PROFILE)
        self.assertRedirects(r, f'{LOGIN}?next={PROFILE}')

    def test_logged_in_user_redirected_from_login_and_register(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(LOGIN), PROFILE)
        self.assertRedirects(self.client.get(REGISTER), PROFILE)

    def test_logout_post(self):
        self.client.force_login(self.user)
        r = self.client.post(LOGOUT)
        self.assertRedirects(r, LOGIN)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_get_not_allowed(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(LOGOUT).status_code, 405)


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class ProfileImageTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user('ali', password=PASSWORD, first_name='Ali')
        self.client.force_login(self.user)

    def upload(self, name='face.jpg'):
        return self.client.post(PROFILE, {'image': make_image(name)})

    def refresh(self):
        self.user.refresh_from_db()
        return self.user

    def test_first_upload_is_pending(self):
        self.assertContains(self.client.get(PROFILE), 'Siz hali rasm yuklamagansiz')
        self.assertRedirects(self.upload(), PROFILE)
        self.assertEqual(self.refresh().image_status, User.ImageStatus.PENDING)

        r = self.client.get(PROFILE)
        self.assertContains(r, 'Kutilmoqda')
        self.assertNotContains(r, 'enctype="multipart/form-data"')  # forma yashirin

    def test_cannot_replace_pending_or_approved(self):
        self.upload('a.jpg')
        first = self.refresh().image.name

        r = self.upload('b.jpg')
        self.assertEqual(r.status_code, 200)
        self.assertIn('ko\'rib chiqilmoqda', r.context['form'].errors['image'][0])
        self.assertEqual(self.refresh().image.name, first)

        User.objects.filter(pk=self.user.pk).update(image_status=User.ImageStatus.APPROVED)
        r = self.upload('c.jpg')
        self.assertIn('tasdiqlangan', r.context['form'].errors['image'][0])
        self.assertEqual(self.refresh().image.name, first)

    def test_rejected_shows_reason_and_allows_new_upload(self):
        self.upload('a.jpg')
        User.objects.filter(pk=self.user.pk).update(
            image_status=User.ImageStatus.REJECTED, rejection_reason="Yuz aniq ko'rinmayapti",
        )
        r = self.client.get(PROFILE)
        self.assertContains(r, 'Bekor qilingan')
        self.assertContains(r, 'Yuz aniq ko&#x27;rinmayapti')
        self.assertContains(r, 'enctype="multipart/form-data"')

        self.assertRedirects(self.upload('b.jpg'), PROFILE)
        user = self.refresh()
        self.assertEqual(user.image_status, User.ImageStatus.PENDING)
        self.assertEqual(user.rejection_reason, '')

    def test_rejected_empty_submit_is_error(self):
        self.upload('a.jpg')
        User.objects.filter(pk=self.user.pk).update(
            image_status=User.ImageStatus.REJECTED, rejection_reason='Sabab',
        )
        r = self.client.post(PROFILE, {})
        self.assertEqual(r.context['form'].errors['image'], ['Rasm tanlang.'])
        self.assertEqual(self.refresh().image_status, User.ImageStatus.REJECTED)

    def test_not_an_image(self):
        fake = SimpleUploadedFile('x.jpg', b'not an image', content_type='image/jpeg')
        r = self.client.post(PROFILE, {'image': fake})
        self.assertIn('image', r.context['form'].errors)
        self.assertFalse(self.refresh().image)
