from kongrequester import KongRequester
from resttest.jsontools import nested_get
from resttest.resttest import Retryable
from utils import SERVICES
import tests
import os

glance = SERVICES['glance']

def md5sum_file(path):
    from hashlib import md5
    md5sum = md5()
    with open(path, 'rb') as file:
        for chunk in iter(lambda: file.read(8192), ''):
            md5sum.update(chunk)
    return md5sum.hexdigest()

def glance_headers(name, file, format, kernel=None, ramdisk=None):
    h = {'x-image-meta-is-public': 'true',
            'x-image-meta-name': name,
            'x-image-meta-disk-format': format,
            'x-image-meta-container-format': format,
            'x-image-meta-size': '%s' % os.path.getsize(file),
            'Content-Length': '%s' % os.path.getsize(file),
            'Content-Type': 'application/octet-stream'}
    if kernel:
        h['x-image-meta-property-Kernel_id'] = str(kernel)
    if ramdisk:
        h['x-image-meta-property-Ramdisk_id'] = str(ramdisk)
    return h

class TestGlanceSwift(tests.FunctionalTest):
    tags = ['glance-swift']

    def test_010_upload_file_to_glance(self):
        streamable = "etc/config.ini"
        headers = glance_headers("glance-swift-test", streamable, "ami")
        md5 = md5sum_file(streamable)
        with open(streamable, "rb") as image_file:
            r, d = glance.POST_raw_with_keys_eq(
                "/images",
                 {"/image/name": "glance-swift-test",
                  "/image/checksum": md5},
                  headers=headers,
                  body=image_file, code=201)

        image_id=nested_get("image/id", d)

        swifty_requester = KongRequester('object-store',
                                         section='glance-swift')

        r, d = swifty_requester.HEAD('/%s/%s?format=json' % (
                self.config["glance-swift"]["container"], image_id),
                                     code=200)

        assert(r['etag'] == md5)
