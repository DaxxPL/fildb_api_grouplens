from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
import mock
from urllib.error import URLError
import zipfile
from io import BytesIO
from django.http import HttpResponse


class PostRequests(APITestCase):

    def test_no_source_in_request(self):
        url = reverse('db')
        response = self.client.post(url)
        self.assertEqual((response.data, response.status_code),
                         ('no source data in body', status.HTTP_400_BAD_REQUEST))

    def test_wrong_source_in_request(self):
        url = reverse('db')
        response = self.client.post(url, {'source': 'bbppg'})
        self.assertEqual((response.data, response.status_code),
                         ('This source is not available', status.HTTP_404_NOT_FOUND))

    def test_timeout_external_server(self):
        with mock.patch('movies.views.FetchFromExternalApi.fetch_from_url') as mock_fetch:
            mock_fetch.side_effect = URLError('bleble')
            url = reverse('db')
            response = self.client.post(url, {'source': 'ml-latest-small'})
            self.assertEqual((response.data, response.status_code),
                             ("External server respond time out", status.HTTP_504_GATEWAY_TIMEOUT))

    def test_bad_response(self):

        class FakeResponse:

            def __init__(self, body, status):
                self.body = body
                self.status = status
                self.content = self.body

        with mock.patch('movies.views.FetchFromExternalApi.fetch_from_url') as mock_fetch:
            fake_response = FakeResponse(body="Some expected data body", status=200)
            mock_fetch.return_value = fake_response
            url = reverse('db')
            response = self.client.post(url, {'source': 'ml-latest-small'})
            self.assertEqual((response.data, response.status_code),
                            ("External server provided wrong file", status.HTTP_500_INTERNAL_SERVER_ERROR))

    def test_bad_zipfile(self):

        class FakeResponse:

            def __init__(self, body, status):
                self.body = body
                self.status = status
                self.content = self.body

        with mock.patch('movies.views.FetchFromExternalApi.fetch_from_url') as mock_fetch:
            fake_response = FakeResponse(body="Some expected data body", status=200)
            mock_fetch.return_value = fake_response
            url = reverse('db')
            response = self.client.post(url, {'source': 'ml-latest-small'})
            self.assertEqual((response.data, response.status_code),
                            ("External server provided wrong file", status.HTTP_500_INTERNAL_SERVER_ERROR))

    def test_zipfile_without_needed_files(self):

        class FakeResponse:
            def __init__(self):
                response = HttpResponse(content_type='application/zip')
                response['Content-Disposition'] = 'filename=%s' % 'fake.zip'
                in_memory = BytesIO()
                zipped = zipfile.ZipFile(in_memory, 'w', zipfile.ZIP_DEFLATED)
                zipped.writestr('fake.csv', 'fake file')
                zipped.close()
                in_memory.flush()
                ret_zip = in_memory.getvalue()
                in_memory.close()
                self.content = ret_zip

        with mock.patch('movies.views.FetchFromExternalApi.fetch_from_url') as mock_fetch:
            fake_response = FakeResponse()
            mock_fetch.return_value = fake_response
            url = reverse('db')
            response = self.client.post(url, {'source': 'ml-latest-small'})
            self.assertEqual((response.data, response.status_code), ("Failed to read CSV file",
                            status.HTTP_500_INTERNAL_SERVER_ERROR))


