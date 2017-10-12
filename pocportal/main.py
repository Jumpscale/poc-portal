import os
import warnings
from importlib import import_module
import json
from collections import namedtuple


import graphene
from graphene import relay
from graphql.execution.executors.asyncio import AsyncioExecutor
from sanic_graphql import GraphQLView
from sanic import Sanic

from pocportal.graphqlbase import BaseQuery

app = Sanic(__name__)
app.debug = True


@app.listener('before_server_start')
def init_graphql(app, loop):
    print(os.getcwd())
    for root, dirs, files in os.walk('pocportal/apps'):
        for file in files:
            print(file)
            if file != 'graphql.py':
                continue
            package = root.replace('/', '.')
            import_module('%s.graphql' % package)

    basequerychildren = tuple(BaseQuery.__subclasses__())
    MainQuery = type('MainQuery', tuple(basequerychildren), {})
    schema = graphene.Schema(query=MainQuery)

    executor = AsyncioExecutor(loop)

    app.add_route(GraphQLView.as_view(
        schema=schema, graphiql=True, executor=executor), '/graphql')


def run_simple():
    app.run(host="0.0.0.0")

if __name__ == '__main__':
    run_simple()
