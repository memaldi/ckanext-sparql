import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ConfigParser
import requests
import logging
import os

from routes.mapper import SubMapper

log = logging.getLogger(__name__)

RDF_FORMAT = ['rdf', 'application/rdf+xml', 'text/plain',
              'application/x-turtle', 'text/rdf+n3']

config = ConfigParser.ConfigParser()
config.read(os.environ['CKAN_CONFIG'])

PLUGIN_SECTION = 'plugin:sparql'
WELIVE_API = config.get(PLUGIN_SECTION, 'welive_api')


class SparqlPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IResourceController)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'sparql')

    # IRouter

    def before_map(self, map):
        with SubMapper(
                map,
                controller='ckanext.sparql.controller:SPARQLController') as m:
            m.connect('sparql_endpoint', '/dataset/sparql/{id}',
                      action='sparql_endpoint', ckan_icon='cogs')

        return map

    # IPackageController

    def before_view(self, pkg_dict):
        for resource in pkg_dict.get('resources', []):
            if resource.get('format', '').lower() in RDF_FORMAT:
                pkg_dict['sparql'] = True
                break
        return pkg_dict

    # IResourceController

    def before_create(self, context, resource):
        return resource

    def after_create(self, context, resource):
        if resource.get('format', '').lower() in RDF_FORMAT:
            if 'url' in resource:
                url = resource['url']
                rdf_text = requests.get(url).content
                api_url = WELIVE_API + 'sparql-query-maker/create'
                files = {'data': rdf_text}
                payload = {'graphName': resource['id']}
                r = requests.post(api_url, files=files, data=payload)
                log.debug(r.text)
        return resource

    def before_update(self, context, current, resource):
        return resource

    def after_update(self, context, resource):
        return resource

    def before_delete(self, context, resource, resources):
        return resource

    def after_delete(self, context, resource):
        return resource

    def before_show(self, resource_dict):
        return resource_dict
