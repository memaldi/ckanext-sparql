from ckan.controllers.package import PackageController
from ckan.plugins import toolkit as tk
from ckan.common import request
import ckan.model as model
import ckan.logic as logic
import logging
import requests
import ConfigParser
import os
import json

log = logging.getLogger(__name__)

config = ConfigParser.ConfigParser()
config.read(os.environ['CKAN_CONFIG'])

PLUGIN_SECTION = 'plugin:sparql'
WELIVE_API = config.get(PLUGIN_SECTION, 'welive_api')

RDF_FORMAT = ['rdf', 'application/rdf+xml', 'text/plain',
              'application/x-turtle', 'text/rdf+n3']

c = tk.c
render = tk.render
get_action = logic.get_action
check_access = logic.check_access


class SPARQLController(PackageController):
    def sparql_endpoint(self, id):
        query = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj}
        try:
            c.pkg_dict = get_action('package_show')(
                context, {'id': id, 'include_tracking': True}
            )
        except logic.NotFound:
            check_access('package_show', context, {'id': id})
            resource = get_action('resource_show')(
                context, {'id': id}
            )
            c.pkg_dict = get_action('package_show')(
                context, {'id': resource['package_id'],
                          'include_tracking': True}
            )

        if request.method == 'POST':
            query = request.POST.getone('sparql-query')
            api_url = WELIVE_API + 'sparql-query-maker/query'
            package_id = None
            for resource in c.pkg_dict.get('resources', []):
                if resource.get('format', '').lower() in RDF_FORMAT:
                    package_id = resource['id']
                    break
            log.debug(package_id)
            if package_id is not None:
                payload = {'query': query, 'graphName': package_id}
                r = requests.get(api_url, params=payload)
                response = r.json()
                result = json.loads(response['response'])
                c.result = result
        c.query = query

        return render('sparql/sparql_endpoint.html')
