from django.conf import settings
from django.apps import apps as django_apps

from django_tenants.utils import has_multi_type_tenants, get_tenant_types, app_in_list


class TenantSyncRouter(object):
    """
    A router to control which applications will be synced,
    depending if we are syncing the shared apps or the tenant apps.
    """

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # the imports below need to be done here else django <1.5 goes crazy
        # https://code.djangoproject.com/ticket/20704
        from django.db import connections
        from django_tenants.utils import get_public_schema_name, get_tenant_database_alias

        if db != get_tenant_database_alias():
            return False

        connection = connections[db]
        public_schema_name = get_public_schema_name()
        if has_multi_type_tenants():
            tenant_types = get_tenant_types()
            if connection.schema_name == public_schema_name:
                installed_apps = tenant_types[public_schema_name]['APPS']
            else:
                installed_apps = tenant_types[connection.tenant.tenant_type]['APPS']
        else:
            if connection.schema_name == public_schema_name:
                installed_apps = settings.SHARED_APPS
            else:
                installed_apps = settings.TENANT_APPS
        if not app_in_list(app_label, installed_apps):
            return False
        return None
