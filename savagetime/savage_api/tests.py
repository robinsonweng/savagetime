# Test for app savage_api
import os
import json
import base64
from django.test import TestCase
from django.test import Client

from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser, User

from savage_api.model.models import Series, Video


setattr(settings, "IS_TESTING", True)


class VideoViewTest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # consts
        self.client = Client()
        self.setting = settings

        # fake datas
        with open("../api_test_data/series.json", "r") as f:
            self.mock_data = list(json.load(f))

        # dbs
        self.user = User.objects.create(
            username="rob",
            email="example@example.com",
            password="123"
        )

        series = Series.objects.create(
            name="月光下的異世界之旅",
            season="spring",
            episodes="12",
            pub_year="2021",
            pub_month="1",
            finale=True,
            subtitle_group="",
        )

    def tearDown(self) -> None:
        pass

    def test_get_video_stream_normal_case(self):
        pass

    def test_post_video_upload_normal_case(self):
        

    def test_patch_video_upload_normal_case(self):
        

    def test_delete_video_upload(self):
        pass

    def test_get_video_info(self):
        pass

    def test_post_video_info(self):
        pass

    def test_patch_video_info(self):
        pass

    def test_delete_video_info(self):
        pass

    def test_get_video_series(self):
        pass


class SeriesViewTest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        pass

    def get_series_info(self):
        pass

    def post_series_info(self):
        pass

    def patch_series_info(self):
        pass

    def delete_series_info(self):
        pass
