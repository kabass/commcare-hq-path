from django.utils.decorators import method_decorator

from corehq import privileges
from corehq.apps.accounting.decorators import requires_privilege_with_fallback
from corehq.apps.reports.dispatcher import ProjectReportDispatcher
from corehq.apps.users.decorators import require_permission
from corehq.apps.users.models import HqPermissions

require_can_edit_fixtures = lambda *args, **kwargs: (
    require_permission(HqPermissions.edit_data)(
        requires_privilege_with_fallback(privileges.LOOKUP_TABLES)(*args, **kwargs)
    )
)


class FixtureInterfaceDispatcher(ProjectReportDispatcher):
    prefix = 'fixture_interface'
    map_name = 'FIXTURE_INTERFACES'

    @method_decorator(require_can_edit_fixtures)
    def dispatch(self, request, *args, **kwargs):
        return super(FixtureInterfaceDispatcher, self).dispatch(request, *args, **kwargs)
