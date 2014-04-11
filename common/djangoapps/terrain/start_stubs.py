"""
Initialize and teardown stub and video HTTP services for use in acceptance tests.
"""
import requests
from lettuce import before, after, world
from django.conf import settings
from terrain.stubs.youtube import StubYouTubeService
from terrain.stubs.xqueue import StubXQueueService
from terrain.stubs.lti import StubLtiService
from terrain.stubs.video_source import VideoSourceHttpService


SERVICES = {
    "youtube": {"port": settings.YOUTUBE_PORT, "class": StubYouTubeService},
    "xqueue": {"port": settings.XQUEUE_PORT, "class": StubXQueueService},
    "lti": {"port": settings.LTI_PORT, "class": StubLtiService},
}

YOUTUBE_API_RESPONSE = requests.get('http://www.youtube.com/iframe_api')


@before.all
def start_video_server():
    """
    Serve the HTML5 Video Sources from a local port
    """
    video_source_dir = '{}/data/video'.format(settings.TEST_ROOT)
    video_server = VideoSourceHttpService(port_num=settings.VIDEO_SOURCE_PORT)
    video_server.config.update({'root_dir': video_source_dir})
    setattr(world, 'video_source', video_server)


@after.all
def stop_video_server(_):
    """
    Stop the HTML5 Video Source server after all tests have executed
    """
    video_server = getattr(world, 'video_source', None)
    video_server.shutdown()


@before.each_scenario
def start_stubs(_):
    """
    Start each stub service running on a local port.
    Since these services can be reconfigured on the fly,
    stop and restart them on a scenario basis.
    """
    for name, service in SERVICES.iteritems():
        fake_server = service['class'](port_num=service['port'])
        if name == 'youtube':
            fake_server.config['youtube_api_response'] = YOUTUBE_API_RESPONSE
        setattr(world, name, fake_server)


@after.each_scenario
def stop_stubs(_):
    """
    Shut down each stub service.
    """
    for name in SERVICES.keys():
        stub_server = getattr(world, name, None)
        if stub_server is not None:
            stub_server.shutdown()
