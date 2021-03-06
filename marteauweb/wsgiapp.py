import logging

from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid.decorator import reify
from pyramid.request import Request as BaseRequest
from pyramid.security import authenticated_userid
from pyramid.exceptions import Forbidden

from marteau import queue


class Request(BaseRequest):
    """
    Custom request class
    """
    @reify
    def user(self):
        """
        Get the logged in user
        """
        return authenticated_userid(self)


def main(global_config, **settings):
    # defaults
    if 'mako.directories' not in settings:
        settings['mako.directories'] = 'marteauweb:templates'

    session_factory = session_factory_from_settings(settings)

    # configure the waitress logger
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    # creating the config and the queue
    config = Configurator(settings=settings, session_factory=session_factory)
    config.registry['queue'] = queue.Queue()

    # Use our custom Request class
    config.set_request_factory(Request)

    # Both of our chosen policies configure a "forbidden view" to handle
    # unauthenticated access.  We have to resolve this conflict by explicitly
    # picking which one we want to use.
    config.add_forbidden_view("pyramid_persona.views.forbidden")

    # routing
    config.add_route('index', '/')
    config.add_route('profile', '/profile')
    config.add_route('purge', '/purge')
    config.add_route('reset', '/reset')
    config.add_route('test', '/test')
    config.add_route('cancel', '/test/{jobid}/cancel')
    config.add_route('delete', '/test/{jobid}/delete')
    config.add_route('replay', '/test/{jobid}/replay')
    config.add_route('job', '/test/{jobid}')
    config.add_route('nodes', '/nodes')
    config.add_route('node_enable', '/nodes/{name}/enable')
    config.add_route('node_test', '/nodes/{name}/test')
    config.add_route('node', '/nodes/{name}')
    config.add_route('report_index', '/report/{jobid}')
    config.add_route('report_file', '/report/{jobid}/{filename:.*}')
    config.add_route('docs_file', '/docs/{file:.*}')
    config.add_route('docs_index', '/docs')
    config.add_route('addjob', '/addjob')
    config.add_route('fixture_options', '/fixture_options/{fixture:.*}')
    config.add_route('project_options', '/project_options/{project:.*}')
    config.add_route('hosts', '/hosts')
    config.add_route('verify_host', '/hosts/{host:.*}/verify')
    config.add_route('host', '/hosts/{host:.*}')
    config.add_static_view('media', 'marteauweb:media/')
    config.add_route('karaoke', '/media/marteau.kar')
    config.add_route('socket_io', 'socket.io/*remaining')

    config.scan("marteauweb.views")
    config.scan("marteauweb.socketio_service")
    return config.make_wsgi_app()
