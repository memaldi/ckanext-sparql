import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from routes.mapper import SubMapper


class SparqlPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

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
