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

        """
        # TODO: clean mp4 junk under /var/tmp
        path = settings.RESUMEABLE_UPLOADER_DEST_PATH
        for p in os.listdir(path):
            if p.endswith('.mp4'):
                os.remove(os.path.join(path, p))
        """

    # TODO: Remove the "content_type header"
    def head_request(self, route, content_type='', header={}):
        base_header = {}
        if header:
            base_header.update(**header)
        return self.client.head(route, content_type=content_type, **base_header)

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

    def checksum_generator(self, binary: bytes):
        checksum = hashlib.new("sha1")
        checksum.update(binary)
        checksum = base64.b64encode(checksum.digest()).decode("utf-8")
        return checksum

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

    def upload_file_segs(self,
                         url,
                         filename=None,
                         headers={},
                         offset=0,
                         chunk_size=1_000_000,
                         stop_at=0):

        # make sure value is bigger or equal to zero
        self.assertEqual(offset < 0, False)
        self.assertEqual(chunk_size < 0, False)
        self.assertEqual(stop_at < 0, False)
        length = os.path.getsize(filename)

        with open(filename, "rb") as f:
            if offset > 0:
                f.seek(offset)
                index = offset

            if stop_at > 0:
                length = stop_at

            index = 0
            rounds = (length - offset) // chunk_size
            if (length % chunk_size) != 0:
                rounds += 1
                for _ in range(rounds):
                    if (length - index) < chunk_size:
                        chunk_size = length - index
                    temp = f.read(chunk_size)

                    index += chunk_size
                    checksum = self.checksum_generator(temp)
                    headers["HTTP_Upload-Offset"] = f"{index}"
                    headers["HTTP_Upload-Checksum"] = f"sha1 {checksum}"
                    headers["HTTP_Content_Length"] = f"{chunk_size}"
                    res = self.patch_request(route=url, data=temp, headers=headers)

                    # probably shouldn't test here
                    self.assertEqual(res.status_code, 204, f"status: {res.status_code}, {res}")

                    resp_offset = res.headers.get("upload-offset")
                    self.assertEqual(int(resp_offset), index, f"offset: {resp_offset}")

                    self.assertEqual(res.headers.get("Tus-Resumable"), "1.0.0")
                    # use checksum to check upload result

    def tearDown(self) -> None:
        from django.core.cache import cache
        cache.clear()

    def test_create_resource(self):
        filename_b64, fileext_b64 = self.file_b64_generator(0)
        upload_meta = f"{filename_b64}, {fileext_b64}"
        filename = self.mock_video_data[0]["path"]

        series_id = self.mock_data[0]["series"]["uuid"]
        episode = self.mock_data[0]["videos"][0]["episode"]
        file_size = os.path.getsize(os.path.join("../api_test_data", filename))
        header = {
            "HTTP_Upload_Metadata": f"{upload_meta}",
            "HTTP_Upload_Length": str(file_size),
            "HTTP_Tus_resumeable": "1.0.0",
        }

        post_data = {
            "series_name": "月光下的異世界之旅",
            "episode": f"{episode}",
            "filename": f"{filename}",
            "series_id": series_id
        }

        # get url for upload
        route = f"{reverse('api-dev:tus_post')}"

        # send request
        result = self.post_request(route, post_data, header=header)

        self.assertEqual(201, result.status_code, f"{result.content}")

        # check header

    def test_patch_video_upload_normal_case(self):
        filename_b64, file_ext64 = self.file_b64_generator(1)

        filepath = self.mock_data[0]["videos"][1]["path"]
        filename = filepath.split("/")[-1]
        episode = self.mock_data[0]["videos"][1]["episode"]

        upload_meta = f"{filename_b64}, {file_ext64}"

        file_size = os.path.getsize(filepath)
        header = {
            "HTTP_Upload_Metadata": f"{upload_meta}",
            "HTTP_Upload_Length": str(file_size),
            "HTTP_Content_Length": "0",
            "HTTP_Tus_resumeable": "1.0.0",
        }

        post_data = {
            "series_name": "月光下的異世界之旅",
            "episode": f"{episode}",
            "filename": f"{filename}"
        }

        route = f"{reverse('api-dev:tus_post')}"

        # Create resource
        res = self.post_request(route, post_data, header=header)

        location = res.headers["Location"]

        # start upload(patch)
        upload_heads = {
            "HTTP_Content_Type": "applictation/offset+octet-stream",
            "HTTP_Content_Length": "",
            "HTTP_Upload_Offset": "",
            "HTTP_Tus_Resumable": "1.0.0"
        }
        self.upload_file_segs(url=location,
                              filename=filepath,
                              headers=upload_heads,
                              offset=0,
                              stop_at=0)

    def test_upload_offset(self):
        """
            Upload file and stop in the middle. Call HEAD method to get offset.
        """
        filename_b64, file_ext64 = self.file_b64_generator(1)
        filepath = self.mock_data[0]["videos"][0]["path"]
        filename = filepath.split("/")[-1]
        episode = self.mock_data[0]["videos"][0]["episode"]
        upload_meta = f"{filename_b64}, {file_ext64}"
        file_size = os.path.getsize(filepath)

        header = {
            "HTTP_Upload_Metadata": f"{upload_meta}",
            "HTTP_Upload_Length": str(file_size),
            "HTTP_Content_Length": "0",
            "HTTP_Tus_resumeable": "1.0.0",
        }

        post_data = {
            "series_name": "月光下的異世界之旅",
            "episode": f"{episode}",
            "filename": f"{filename}"
        }
        route = f"{reverse('api-dev:tus_post')}"

        # Create resource
        res = self.post_request(route, post_data, header=header)

        location = res.headers["Location"]

        # start upload(patch)
        upload_heads = {
            "HTTP_Content_Type": "applictation/offset+octet-stream",
            "HTTP_Content_Length": "",
            "HTTP_Upload_Offset": "",
            "HTTP_Tus_Resumable": "1.0.0"
        }

        stop = 100
        self.upload_file_segs(url=location,
                              filename=filepath,
                              headers=upload_heads,
                              offset=0,
                              stop_at=stop)
        res = self.head_request(location, header=header)

        self.assertEqual(res.status_code, 204, f"{res.content}")
        self.assertEqual(int(res.headers["Upload-Offset"]), 100, res.content)

    def test_delete_video_upload(self):
        pass

    def test_file_checknum(self):
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
