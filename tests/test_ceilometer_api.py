from utils import SERVICES
import tests
from resttest.jsontools import nested_search


ceilometer = SERVICES['metering']
k = SERVICES['keystone']
admin = SERVICES['keystone-admin']
user = k.get_config()[1]
project = k.get_config()[3]
api_ver = 'v1'


class TestCeilometerAPI(tests.FunctionalTest):
    tags = ['ceilometer']

    def test_001_list_meters(self):
        ceilometer.GET('/%s/meters' % api_ver, code=200)

    def test_002_list_resources(self):
        ceilometer.GET('/%s/resources' % api_ver, code=200)

    def test_003_list_users(self):
        ceilometer.GET('/%s/users' % api_ver, code=200)

    def test_004_list_projects(self):
        ceilometer.GET('/%s/projects' % api_ver, code=200)

    def test_005_list_meters_for_user(self):
        response, data = admin.GET("/users")
        userid = nested_search("/users/*/name=%s/id" % user, data)[0]
        ceilometer.GET('/%s/users/%s/meters'
                       % (api_ver, userid), code=200)

    def test_006_list_meters_for_project(self):
        response, data = admin.GET("/tenants")
        projectid = nested_search("/tenants/*/name=%s/id" % project, data)[0]
        ceilometer.GET('/%s/projects/%s/meters'
                       % (api_ver, projectid), code=200)

    def test_007_list_resources_for_user(self):
        response, data = admin.GET("/users")
        userid = nested_search("/users/*/name=%s/id" % user, data)[0]
        ceilometer.GET('/%s/users/%s/resources'
                       % (api_ver, userid), code=200)

    def test_008_list_resources_for_project(self):
        response, data = admin.GET("/tenants")
        projectid = nested_search("/tenants/*/name=%s/id" % project, data)[0]
        ceilometer.GET('/%s/projects/%s/resources'
                       % (api_ver, projectid), code=200)
