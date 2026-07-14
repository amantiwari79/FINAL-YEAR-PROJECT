from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Resume


class ResumePdfPreviewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='preview@example.com', password='test-password'
        )
        self.resume = Resume.objects.create(
            user=self.user,
            title='PDF resume',
            file=SimpleUploadedFile('resume.pdf', b'%PDF-1.4\n', content_type='application/pdf'),
        )

    def test_pdf_preview_is_inline_and_only_available_to_owner(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('preview_resume_pdf', args=[self.resume.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('inline', response['Content-Disposition'])

    def test_docx_does_not_have_a_pdf_preview(self):
        self.resume.file = SimpleUploadedFile(
            'resume.docx', b'placeholder',
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
        self.resume.save()
        self.client.force_login(self.user)

        response = self.client.get(reverse('preview_resume_pdf', args=[self.resume.pk]))

        self.assertEqual(response.status_code, 404)
