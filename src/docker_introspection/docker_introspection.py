#!/usr/bin/env

import docker
from flask import Flask, request
from flask.ext.restful import abort, Resource, Api
from argparse import ArgumentParser

DOCKER_CONFIG_ITEMS = [u'Env',
                       u'Hostname',
                       u'Entrypoint',
                       u'PortSpecs',
                       u'Memory',
                       u'OnBuild',
                       u'OpenStdin',
                       u'Cpuset',
                       u'User',
                       u'CpuShares',
                       u'AttachStdout',
                       u'NetworkDisabled',
                       u'WorkingDir',
                       u'Cmd',
                       u'StdinOnce',
                       u'AttachStdin',
                       u'MemorySwap',
                       u'Volumes',
                       u'Tty',
                       u'AttachStderr',
                       u'Domainname',
                       u'Image',
                       u'SecurityOpt',
                       u'ExposedPorts']
config_names = { name.lower(): name for name in DOCKER_CONFIG_ITEMS }

app = Flask(__name__)
api = Api(app)

class DockerContainer(Resource):
    def get(self, container_id, config_item=None):
        source_container_id = self._get_source_container_id()

        if container_id == '_myself':
            container_id = source_container_id

        if not (source_container_id == container_id or source_container_id[:12] == container_id):
            abort(401)

        container_info = app._docker_client.inspect_container(container_id)

        if not container_info:
            abort(404)

        if config_item:
            if not config_item.lower() in config_names: abort(404)
            config_item = config_names[config_item.lower()]
            if config_item in container_info['Config']:
                return container_info['Config'][config_item]
            else:
                abort(404)
        else:
            return container_info

    def _get_source_container_id(self):
        ip2id_map = {c_info['NetworkSettings']['IPAddress']: c_info['Id'] for c_info in map(app._docker_client.inspect_container, app._docker_client.containers())}
        return ip2id_map[request.remote_addr]

api.add_resource(DockerContainer, '/containers/<string:container_id>', '/containers/<string:container_id>/<string:config_item>')

def main():
    parser = ArgumentParser(description="Docker introspection server")
    parser.add_argument("-p", dest='port', default=5000, help="The port to listen on")
    parser.add_argument("-u", dest='url', default='unix://var/run/docker.sock', help="Docker API url")
    parser.add_argument("-b", dest='bind_address', default='172.17.42.1', help="Address to listen (bind) on")
    parser.add_argument("-d", dest='debug', default=False, help="Debug mode", action='store_true')
    opts = parser.parse_args()

    app._docker_client = docker.Client(opts.url)

    app.run(debug=opts.debug, port=opts.port, host=opts.bind_address)

if __name__ == '__main__': main()
