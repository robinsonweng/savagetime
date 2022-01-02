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

