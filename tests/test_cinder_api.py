from utils import SERVICES
import tests
from resttest.jsontools import nested_search


cinder = SERVICES['volume']

#    absolute-limits     Print a list of absolute limits for a user
#    create              Add a new volume.
#    credentials         Show user credentials returned from auth
#    delete              Remove a volume.
#    endpoints           Discover endpoints that get returned from the
#                        authenticate services
#    list                List all the volumes.
#    quota-class-show    List the quotas for a quota class.
#    quota-class-update  Update the quotas for a quota class.
#    quota-defaults      List the default quotas for a tenant.
#    quota-show          List the quotas for a tenant.
#    quota-update        Update the quotas for a tenant.
#    rate-limits         Print a list of rate limits for a user
#    show                Show details about a volume.
#    snapshot-create     Add a new snapshot.
#    snapshot-delete     Remove a snapshot.
#    snapshot-list       List all the snapshots.
#    snapshot-show       Show details about a snapshot.
#    type-create         Create a new volume type.
#    type-delete         Delete a specific flavor
#    type-list           Print a list of available 'volume types'.


class TestCinderAPI(tests.FunctionalTest):
    tags = ['cinder']

    def test_001_get_absolute_limits(self):
        cinder.GET('/limits?format=json', code=200)

    def test_002_list_volumes(self):
        cinder.GET('/volumes/detail', code=200)

#    def test_003_list_containers(self):
#        response, body = swift.GET('?format=json', code=200)
#        #check to see container count is greater than zero
#        if int(response['x-account-container-count']) < 1:
#            raise AssertionError("No containers found")
#
#    def test_004_create_custom_container_meta(self):
#        headers = {"X-Container-Meta-blah": "blahblah"}
#        swift.POST('/%s?format=json' % (CONTAINER), headers=headers, code=204)
#
## create objects
#
#    def test_005_create_normal_object(self):
#        # open fake file object
#        obj = StringIO.StringIO()
#        # write some Content
#        obj.write(NORMAL_OBJ)
#        headers = ({'Content-Length': '%d' % obj.len,
#                'Content-Type': 'application/octet-stream'})
#        swift.PUT_raw('/%s/%s' % (CONTAINER, NORMAL_OBJ),
#                headers=headers, body=obj.getvalue(),  code=201)
#
#    def test_006_create_manifest_object(self):
#        # create 3 objects
#        for obj in [MULTIPART_OBJ_1, MULTIPART_OBJ_2, MULTIPART_OBJ_3]:
#            p = StringIO.StringIO()
#            p.write(obj)
#            headers = ({'Content-Length': '%d' % p.len,
#                'Content-Type': 'application/octet-stream'})
#            swift.PUT_raw('/%s/%s/%s' % (CONTAINER, PREFIX, obj),
#                headers=headers, body=p.getvalue(),  code=201)
#
#        # create the manifest file
#        headers = ({'X-Object-Manifest': '%s/%s' % (CONTAINER, PREFIX),
#                'Content-Length': '0'})
#        swift.PUT_raw('/%s/%s' % (CONTAINER, PREFIX),
#                headers=headers, code=201)
#
## update object Meta
#    def test_008_create_custom_object_meta(self):
#        headers = ({'X-Object-Meta-blah': 'blahblah'})
#        swift.POST('/%s/%s?format=json' % (CONTAINER, NORMAL_OBJ),
#                headers=headers, code=202)
#
## get objects
#    def test_009_get_normal_object(self):
#        response, body = swift.GET_raw('/%s/%s?format=json'
#                % (CONTAINER, NORMAL_OBJ), code=200)
#        if body != NORMAL_OBJ:
#            raise AssertionError('file does not contain expected contents')
#
#    def test_010_get_manifest_object(self):
#        response, body = swift.GET_raw('/%s/%s'
#                % (CONTAINER, PREFIX), code=200)
#        if body != "".join([MULTIPART_OBJ_1, MULTIPART_OBJ_2,
#            MULTIPART_OBJ_3]):
#            raise AssertionError('file does not contain expected contents')
#
#    def test_012_delete_normal_object(self):
#        swift.DELETE('/%s/%s?format=json' % (CONTAINER, NORMAL_OBJ),
#                     code=204)
#
#    def test_013_delete_manifest_object(self):
#        # delete manifest file first
#        swift.DELETE('/%s/%s?format=json' % (CONTAINER, PREFIX),
#                     code=204)
#        # delete all parts individually
#        for m in [MULTIPART_OBJ_1, MULTIPART_OBJ_2, MULTIPART_OBJ_3]:
#            swift.DELETE('/%s/%s/%s' % (CONTAINER, PREFIX,
#                    m), code=204)
#
#    def test_100_delete_container(self):
#        # need to get a list of objects in the container and delete them
#        response, body = swift.GET(('/%s?format=json') % (CONTAINER), code=200)
#        # pull the objects out of the returned json
#        objects = nested_search('*/name', body)
#        # delete the objects one by one
#        for obj in objects:
#            swift.DELETE('%s/%s' % (CONTAINER, obj), code=204)
#
#        # now we can delete the container
#        swift.DELETE('/%s?format=json' % (CONTAINER), code=204)
