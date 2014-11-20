#!/usr/bin/env

import docker
from flask import Flask, request
from flask.ext.restful import abort, Resource, Api
from argparse import ArgumentParser

app = Flask(__name__)
api = Api(app)

class DockerContainer(Resource):
    def get(self, container_id, config_item=None):
        if app._do_auth:
            source_container_id = self._get_source_container_id()

            if container_id == '_myself':
                container_id = source_container_id

            if not (source_container_id == container_id or source_container_id[:12] == container_id):
                abort(401)

        container_info = app._docker_client.inspect_container(container_id)

        if not container_info:
            abort(404)

        if config_item:
            for k in container_info['Config']:
                if k.lower() == config_item:
                    return container_info['Config'][k]
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
    parser.add_argument("--no-auth", dest='do_auth', default=True, help="Disable source IP checks", action='store_false')
    opts = parser.parse_args()

    app._docker_client = docker.Client(opts.url)
    app._do_auth = opts.do_auth

    app.run(debug=opts.debug, port=opts.port, host=opts.bind_address)

if __name__ == '__main__': main()
