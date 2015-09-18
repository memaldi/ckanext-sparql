from ckan.controllers.package import PackageController
from ckan.plugins import toolkit as tk
from ckan.common import request
import ckan.model as model
import ckan.logic as logic
import logging

log = logging.getLogger(__name__)

c = tk.c
render = tk.render
get_action = logic.get_action


class SPARQLController(PackageController):
    def sparql_endpoint(self, id):

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj}

        c.pkg_dict = get_action('package_show')(
            context, {'id': id, 'include_tracking': True}
        )

        log.debug(request.body)
        log.debug(request.params)

        return render('sparql/sparql_endpoint.html')
