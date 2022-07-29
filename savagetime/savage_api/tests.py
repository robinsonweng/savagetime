# Unit Test for app savage_api
import os
import sys
import json
import base64
import hashlib

from pathlib import Path

from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.http import HttpRequest
from django.core.cache import caches
from django.contrib.auth.models import AnonymousUser, User

from savage_api.model.models import Series, Video


setattr(settings, "IS_TESTING", True)
setattr(settings, "RESUMEABLE_UPLOADER_CACHE_CONFIG", "unittest")

cache = caches[settings.RESUMEABLE_UPLOADER_CACHE_CONFIG]


class VideoViewTest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # consts
        self.client = Client()
        self.setting = settings

        # fake data
        with open("../api_test_data/series.json", "r") as f:
            self.mock_data = list(json.load(f))

        # dbs
        self.user = User.objects.create(
            username="rob",
            email="example@example.com",
            password="123"
        )

        self.mock_video_data = [row.get('videos') for row in self.mock_data][0]
        self.mock_series_data = [row.get('series') for row in self.mock_data][0]

        series = Series.objects.create(
            uuid=self.mock_data[0]["series"]["uuid"],
            name=self.mock_data[0]["series"]["name"],
            season=self.mock_data[0]["series"]["season"],
            episodes=self.mock_data[0]["series"]["episodes"],
            pub_year=self.mock_data[0]["series"]["pub_year"],
            pub_month=self.mock_data[0]["series"]["pub_month"],
            finale=self.mock_data[0]["series"]["finale"],
        )

        # clean mp4 junk
        path = settings.RESUMEABLE_UPLOADER_DEST_PATH
        for p in os.listdir(path):
            if p.endswith('.mp4'):
                os.remove(os.path.join(path, p))

    def head_request(self, route, data, content_type='', header={}):
        base_header = {}
        if header:
            base_header.update(**header)
        return self.client.head(route, data, content_type=content_type, **base_header)

    def post_request(self, route, data, content_type='application/json', header={}):
        base_header = {}
        if header:
            # ^ if header is not empty
            base_header.update(**header)
        return self.client.post(route, data, content_type='application/json', **base_header)

    def patch_request(self, route, data, headers={}):
        base_header = {}
        if headers:
            base_header.update(**headers)
        return self.client.patch(route,
                                 data,
                                 content_type='application/offset+octet-stream',
                                 **base_header)

    def file_b64_generator(self, index: int):
        filename = self.mock_video_data[0]["path"]
        filename_bin = filename.encode("utf-8")
        filename_b64 = base64.b64encode(filename_bin).decode("utf-8")
        filename_b64 = f"filename {filename_b64}"

        file_ext = filename.split(".")[1]
        file_extbin = file_ext.encode("utf-8")
        file_ext64 = base64.b64encode(file_extbin).decode("utf-8")
        file_ext64 = f"file_ext {file_ext64}"

        return [filename_b64, file_ext64]

    def file_checksum(self):
        pass










    def file_checksum(self):
        pass

    def tearDown(self) -> None:
        from django.core.cache import cache
        cache.clear()

    def test_get_video_stream_normal_case(self):
        pass

    def test_post_video_upload_normal_case(self):
        request = self.client
        route = reverse("api-dev:video_upload")
        post_data = {
            "series_name": "月光下的異世界之旅",
            "episode": "1",
            "file_name": "[Tsuki ga Michibiku Isekai Douchuu][01][1080P].mp4"
        }
        response = request.post(
            route, post_data, content_type='application/json',
            # request header
            HTTP_x_upload_content_length='1000',
            HTTP_x_upload_content_type='video/*',
        )
        self.assertEqual(200, response.status_code, f"{response.content}")

    def test_patch_video_upload_normal_case(self):
        upload_id = "Tea31"
        route = f"{reverse('api-dev:video_upload')}?upload_id={upload_id}"
        path = self.mock_data[0]["videos"][0]["path"]
        total_length = os.path.getsize(path)

        cache_data = {
            "series_id": self.mock_data[0]["series"]["uuid"],
            "x_length": total_length,
            "file_name": "[Tsuki ga Michibiku Isekai Douchuu][02][1080P].mp4",
            "episode": "2"
        }
        cache.add(f"uploader/{upload_id}/metadata", cache_data)
        request = self.client

        chunk_length = 1 * 1024 * 1024  # 1mb
        times = total_length // chunk_length
        if total_length % chunk_length > 0:
            times += 1
        index = 0
        counter = 0
        res_list = []

        def send_request(path, data, index, chunk_len=chunk_length, total_len=total_length, **kwargs):
            return request.patch(
                path, data,
                HTTP_content_type="video/*",
                HTTP_content_length=f"{len(data)}",
                HTTP_content_range=f"bytes {index}-{index + chunk_len}/{total_len}",
                **kwargs,
            )

        with open(path, "rb") as f:
            check_sum = hashlib.new("sha256")
            check_sum.update(f.read())
            check_sum = base64.b64encode(check_sum.digest()).decode()
            while (total_length - index) >= chunk_length:
                f.seek(index)
                patch_data = f.read(chunk_length)

                response = send_request(route, patch_data, index)
                res_list.append(response)
                index += chunk_length
                counter += 1
            else:
                remain = total_length - index
                if remain > 0:
                    patch_data = f.read(remain)
                    response = send_request(
                        route,
                        patch_data,
                        index,
                        chunk_len=remain,
                        HTTP_uploader_checksum=f"sha256 {check_sum}")
                    res_list.append(response)

        self.assertEqual(times, len(res_list), f"{res_list}")
        self.assertEqual(201, response.status_code, f"{response.content}")
        self.assertEqual([204] * (times - 1) + [201], 
                         [r.status_code for r in res_list],
                         f"{res_list}")

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
