from resttest.jsontools import nested_search
from resttest.httptools import wrap_headers
from utils import SERVICES
import tests
import os


SMALL_OBJ = "include/swift_objects/swift_small"
MED_OBJ = "include/swift_objects/swift_medium"
LRG_OBJ = "include/swift_objects/swift_large"
CONTAINER = "kongtestcontainer"


swift = SERVICES['swift']


class TestSwiftAPI2(tests.FunctionalTest):
    tags = ['swift']

    def test_001_create_container(self):
        r, d = swift.PUT("/" + CONTAINER + "?format=json", code=201)


    def test_002_list_container_meta(self):
        r, d = swift.HEAD( "/" + CONTAINER + "?format=json", code=204)


    def test_003_list_containers(self):
        r, d = swift.GET('?format=json', code=200)
        #check to see container count is greater than zero
        if int(r['x-account-container-count']) < 1:
            raise AssertionError("No containers found")


    def test_004_create_custom_container_meta(self):
        """need to use wrap_headers somehow to add in a custom metadata k,v"""
        # CUSTOM-META = {"X-Container-Meta-blah": "blahblah"}
        # r, d = swift.POST('/')


    @tests.skip_test("Currently not working")
    def test_003_create_small_object(self):
        # build headers to pass to wrap_headers
        ADDITIONAL_HEADERS = ({'Content-Length': '%d' %os.path.getsize(SMALL_OBJ), \
                'Content-Type': 'application/octet-stream'})
        # somehow use wrap_headers to pass additional headers to request
        # r, d = swift.PUT(CONTAINER + '/' + SMALL_OBJ) + ADDITIONAL_HEADERS

    @tests.skip_test("Currently not working")
    def test_005_update_object_meta(self):
        # build headers to pass to wrap_headers
        ADDITIONAL_HEADERS=({'X-Object-Meta-blah': 'blahblah'})
        swift.POST('/CONTAINER/SMALL_OBJ' + '?format=json', code=202)

    @tests.skip_test("Currently not working")
    def test_004_create_medium_object(self):
        # build headers to pass to wrap_headers
        ADDITIONAL_HEADERS = ({'Content-Length': '%d' %os.path.getsize(MED_OBJ), \
                'Content-Type': 'application/octet-stream'})
        # somehow use wrap_headers to pass additional headers to request
        # r, d = swift.PUT(CONTAINER + '/' + MED_OBJ) + ADDITIONAL_HEADERS


    @tests.skip_test("Currently not working")
    def test_005_create_large_object(self):
        # build headers to pass to wrap_headers
        ADDITIONAL_HEADERS = ({'Content-Length': '%d' %os.path.getsize(MED_OBJ), \
                'Content-Type': 'application/octet-stream'})
        # somehow use wrap_headers to pass additional headers to request
        #r, d = swift.PUT(CONTAINER + '/' + LRG_OBJ) + ADDITIONAL_HEADERS


    @tests.skip_test("Currently not working")
    def test_006_get_small_object(self):
        swift.GET('/CONTAINER/SMALL_OBJ' + '?format=json', code=200)

    @tests.skip_test("Currently not working")
    def test_007_get_medium_object(self):
        swift.GET('/CONTAINER/MED_OBJ' + '?format=json', code=200)

    @tests.skip_test("Currently not working")
    def test_008_get_large_object(self):
        swift.GET('/CONTAINER/LRG_OBJ' + '?format=json', code=200)

    @tests.skip_test("Currently not working")
    def test_009_delete_small_object(self):
        swift.DELETE('/CONTAINER/SMALL_OBJ' + '?format=json', code=204)

    @tests.skip_test("Currently not working")
    def test_010_delete_medium_object(self):
        swift.DELETE('/CONTAINER/MED_OBJ' + '?format=json', code=204)

    @tests.skip_test("Currently not working")
    def test_010_delete_large_object(self):
        swift.DELETE('/CONTAINER/LRG_OBJ' + '?format=json', code=204)


    def test_100_delete_container(self):
        swift.DELETE('/CONTAINER' + '?format=json', code=204)



