#!/usr/bin/env python
# -*- coding: utf-8 -*-

from link.riak.driver import RiakDriver
from riak import RiakError

from subprocess import call
from time import sleep
import json
import os


def create_bucket_type(bucket_name):
    ret = call(
        [
            'sudo',
            'riak-admin',
            'bucket-type',
            'create',
            bucket_name,
            json.dumps({'props': {'datatype': 'map'}})
        ]
    )

    if ret == 0:
        return call(
            [
                'sudo',
                'riak-admin',
                'bucket-type',
                'activate',
                bucket_name
            ]
        )


def create_schema(bucket_name, schema_name, index_name, schema_path):
    riakmiddleware = RiakDriver.get_middleware_by_uri(
        'riak://localhost:8087/default?protocol=pbc'
    )
    riakclient = riakmiddleware.conn

    with open(schema_path) as f:
        riakclient.create_search_schema(schema_name, f.read())

    riakclient.create_search_index(index_name, schema_name)

    # make sure the index is created
    timeout = 30

    while timeout:
        try:
            riakclient.get_search_index(index_name)

        except RiakError:
            timeout -= 1
            sleep(1)

        else:
            break

    return call(
        [
            'sudo',
            'riak-admin',
            'bucket-type',
            'update',
            bucket_name,
            json.dumps({'props': {'search_index': index_name}})
        ]
    )


def main():
    iterations = [
        {
            'bucket-name': 'nodes',
            'schema-name': 'nodes',
            'index-name': 'nodes',
            'schema-path': os.path.join(
                '..', 'etc', 'link', 'graph', 'schemas', 'node.xml'
            )
        },
        {
            'bucket-name': 'relationships',
            'schema-name': 'relationships',
            'index-name': 'relationships',
            'schema-path': os.path.join(
                '..', 'etc', 'link', 'graph', 'schemas', 'relationship.xml'
            )
        }
    ]

    for iteration in iterations:
        ret = create_bucket_type(iteration['bucket-name'])
        assert ret == 0

        ret = create_schema(
            iteration['bucket-name'],
            iteration['schema-name'],
            iteration['index-name'],
            iteration['schema-path']
        )

        assert ret == 0


if __name__ == '__main__':
    main()
