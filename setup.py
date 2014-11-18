#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='docker-introspection',
      version='0.1.0',
      description='An HTTP read only API for container introspection',
      author='Avishai Ish-Shalom',
      install_requires=['docker-py', 'Flask-RESTful'],
      entry_points={'console_scripts': [ 'docker-introspection = docker_introspection:main' ] },
      packages=['docker_introspection'],
      package_dir={'docker_introspection': 'src/docker_introspection' },
)
