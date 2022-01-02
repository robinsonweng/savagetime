# Test for app savage_api
import os
import json
import base64
from django.test import TestCase
from django.test import Client
from savage_api.models import Series


class CreateVideoMetadataTest(TestCase):
    def setUp(self):
        self.api = "/api/dev/"
        self.video_route = os.path.join(self.api, 'video') 
        self.upload_url = ""
        self.request = Client()
        Series.objects.create(
            name="月光下的異世界之旅",
            season="spring",
            episodes=12,
            pub_year="2021",
            pub_month="1",
            finale=True,
            subtitle_group="",
        )

    def test_video_post_normal_case(self):
        post_data = {
            "series_name": "月光下的異世界之旅",
            "episode": "1",
            "file_name": "[Tsuki ga Michibiku Isekai Douchuu][01][1080P].mp4"
        }
        response = self.request.post(
            self.video_route, post_data, content_type='application/json',
            # request header
            HTTP_x_upload_content_length='1000',
            HTTP_x_upload_content_type='video/*',
        )
        self.upload_url = json.loads(response.content.decode('utf-8'))["upload_url"]
        self.assertEqual(200, response.status_code)
