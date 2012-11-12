from utils import SERVICES
import tests
from resttest.jsontools import nested_search


cinder = SERVICES['volume']
k = SERVICES['keystone']
user = k.get_config()[1]
#    absolute-limits     Print a list of absolute limits for a user
##    create              Add a new volume.
##    credentials         Show user credentials returned from auth
##    delete              Remove a volume.
###    endpoints           Discover endpoints that get returned from the
#                        authenticate services
##    list                List all the volumes.
#    quota-class-show    List the quotas for a quota class.
#    quota-class-update  Update the quotas for a quota class.
##    quota-defaults      List the default quotas for a tenant.
##    quota-show          List the quotas for a tenant.
##    quota-update        Update the quotas for a tenant.
##    rate-limits         Print a list of rate limits for a user
##    show                Show details about a volume.
##    snapshot-create     Add a new snapshot.
##    snapshot-delete     Remove a snapshot.
##    snapshot-list       List all the snapshots.
##    snapshot-show       Show details about a snapshot.
##    type-create         Create a new volume type.
##    type-delete         Delete a specific flavor
##    type-list           Print a list of available 'volume types'.


class TestCinderAPI(tests.FunctionalTest):
    tags = ['cinder']

    def test_001_list_absolute_limits(self):
        cinder.GET('/limits', code=200)

    def test_002_list_volumes(self):
        cinder.GET('/volumes/detail', code=200)

    def test_003_list_default_quotas(self):
        cinder.GET('/os-quota-sets/%s/defaults' % user, code=200)

    def test_004_list_current_quotas(self):
        cinder.GET('/os-quota-sets/%s' % user, code=200)

    def test_005_list_rate_limits(self):
        cinder.GET('/limits', code=200)

    def test_006_list_types(self):
        cinder.GET('/types', code=200)
        
    def test_007_list_snapshots(self):
        cinder.GET('/snapshots/detail', code=200)
    
    def test_008_update_quotas(self):
        resp, body = cinder.GET('/os-quota-sets/%s' % user, code=200)
        current_volumes = body['quota_set']['volumes']
        target_volumes = current_volumes +1

        cinder.PUT("/os-quota-sets/%s" % user,
                  body={"quota_set":
                       {"tenant_id": "%s" % user,
                        "volumes": "%s" % target_volumes}},
                        code=200)

        resp, body = cinder.GET('/os-quota-sets/%s' % user, code=200)
        new_volumes = body['quota_set']['volumes']

        if new_volumes != target_volumes:
            raise AssertionError('Could not update quotas')

    def test_009_create_volume_type(self):
        cinder.POST('/types', body={"volume_type":
                                   {"name": "test-type"}}, code=200)

    def test_010_create_volume(self):
        resp, body = cinder.POST('/volumes', body={"volume":
                                                  {"size": "1",
                                                   "volume_type": "test-type",
                                                   "display_name": "test-volume"}},
                                                   code=200)
        volume_id = body["volume"]["id"]

        resp, body = cinder.GET_with_keys_eq('/volumes/%s' % volume_id,
                                            {"/volume/status": "available"},
                                            code=200, timeout=60, delay=5)

    def test_011_create_snapshot(self):
        volume_id = nested_search('/volumes/*/display_name=test-volume/id',
                        cinder.GET('/volumes/detail')[1])[0]

        resp, body = cinder.POST('/snapshots', body={"snapshot":
                                                     {"display_name": "test-snapshot",
                                                     "volume_id": volume_id}},
                                                     code=200)

        snapshot_id = body["snapshot"]["id"]

        resp, body = cinder.GET_with_keys_eq('/snapshots/%s' % snapshot_id,
                                            {"/snapshot/status": "available"},
                                            code=200, timeout=60, delay=5)


    def test_012_delete_snapshot(self):
        snapshot_id = nested_search('/snapshots/*/display_name=test-snapshot/id',
                        cinder.GET('/snapshots/detail')[1])[0]

        resp, body = cinder.DELETE('/snapshots/%s' % snapshot_id, code=202)

        resp, body = cinder.GET('/snapshots/%s' % snapshot_id, code=404, timeout=80, delay=5)

    def test_013_delete_volume(self):
        volume_id = nested_search('/volumes/*/display_name=test-volume/id',
                        cinder.GET('/volumes/detail')[1])[0]

        resp, body = cinder.DELETE('/volumes/%s' % volume_id, code=202)

        resp, body = cinder.GET('/volumes/%s' % volume_id, code=404, timeout=80, delay=5)

    def test_014_delete_volume_type(self):
        type_id = nested_search('/volume_types/*/name=test-type/id',
                        cinder.GET('/types')[1])[0]

        resp, body = cinder.DELETE('/types/%s' % type_id, code=202)

        resp, body = cinder.GET('/types/%s' % type_id, code=404, timeout=10, delay=5)
