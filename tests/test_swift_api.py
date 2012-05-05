from resttest.jsontools import nested_search
from resttest.httptools import wrap_headers
from kongrequester import KongRequester
from utils import SERVICES
import tests
import os


SMALL_OBJ = "include/swift_objects/swift_small"
#SMALL_OBJ = "swift_small"
MED_OBJ = "include/swift_objects/swift_medium"
LRG_OBJ = "include/swift_objects/swift_large"
CONTAINER = "kongtestcontainer"


swift = SERVICES['object-store']


class TestSwiftAPI2(tests.FunctionalTest):
    tags = ['swift']

    def test_001_create_container(self):
        swift.PUT("/" + CONTAINER + "?format=json", code=201)

    def test_002_list_container_meta(self):
        swift.HEAD("/" + CONTAINER + "?format=json", code=204)

    def test_003_list_containers(self):
        response, body = swift.GET('?format=json', code=200)
        #check to see container count is greater than zero
        if int(response['x-account-container-count']) < 1:
            raise AssertionError("No containers found")

    def test_004_create_custom_container_meta(self):
        headers = {"X-Container-Meta-blah": "blahblah"}
        swift.POST('/' + CONTAINER + '?format=json', headers=headers, code=204)

# create objects
#    @tests.skip_test("Currently not working")
    def test_005_create_normal_object(self):
        headers = ({'Content-Length': '%d' % os.path.getsize(SMALL_OBJ), \
                'Content-Type': 'application/octet-stream'})
        object = open(SMALL_OBJ, "rb")
        swift.PUT_raw('/' + CONTAINER + '/' + SMALL_OBJ, \
                headers=headers, body=object,  code=201)

    def test_006_create_manifest_object(self):
        pass

#    @tests.skip_test("Currently not working")
#    def test_006_create_medium_object(self):
#
#        headers = ({'Content-Length': '%d' % os.path.getsize(MED_OBJ), \
#                'Content-Type': 'application/octet-stream'})
#        object = open(MED_OBJ, "rb")
#        swift.PUT_raw('/' + CONTAINER + '/' + MED_OBJ, \
#                headers=headers, body=object,  code=201)
#
##    @tests.skip_test("Currently not working")
#    def test_007_create_large_object(self):
#        headers = ({'Content-Length': '%d' % os.path.getsize(LRG_OBJ), \
#                'Content-Type': 'application/octet-stream'})
#        object = open(LRG_OBJ, "rb")
#        swift.PUT_raw('/' + CONTAINER + '/' + LRG_OBJ, \
#                headers=headers, body=object,  code=201)

# update object Meta
#    @tests.skip_test("Currently not working")
    def test_008_create_custom_object_meta(self):
        headers = ({'X-Object-Meta-blah': 'blahblah'})
        swift.POST('/' + CONTAINER + '/' + SMALL_OBJ + '?format=json',\
                headers=headers, code=202)

# get objects
#    @tests.skip_test("Currently not working")
    def test_009_get_normal_object(self):
        swift.GET_raw('/' + CONTAINER + '/' + SMALL_OBJ, code=200)
#       swift.GET_raw('/' + CONTAINER + '/' + SMALL_OBJ + '?format=json',
#                     code=200)

    def test_010_get_manifest_object(self):
        pass

#    @tests.skip_test("Currently not working")
#    def test_010_get_medium_object(self):
#        swift.GET_raw('/' + CONTAINER + '/' + MED_OBJ + '?format=json',
#                      code=200)
#
#    @tests.skip_test("Currently not working")
#    def test_011_get_large_object(self):
#        swift.GET_raw('/' + CONTAINER + '/' + LRG_OBJ + '?format=json',
#                       code=200)

# delete objects
#    @tests.skip_test("Currently not working")
    def test_012_delete_normal_object(self):
        swift.DELETE('/' + CONTAINER + '/' + SMALL_OBJ + '?format=json',
                     code=204)

    def test_013_delete_manifest_object(self):
        pass

#    @tests.skip_test("Currently not working")
#    def test_013_delete_medium_object(self):
#        swift.DELETE('/' + CONTAINER + '/' + MED_OBJ + '?format=json',
#                      code=204)
#
#    @tests.skip_test("Currently not working")
#    def test_014_delete_large_object(self):
#        swift.DELETE('/' + CONTAINER + '/' + LRG_OBJ + '?format=json',
#                      code=204)

    def test_100_delete_container(self):
        swift.DELETE('/' + CONTAINER + '?format=json', code=204)
