#!/usr/bin/python3

import os

import graphene
from graphene import relay
from aysclient.client import Client
import json
from pocportal.utils import json2obj
from pocportal.graphqlbase import BaseQuery
from pocportal.apps.ays.config import AYS_INSTANCE
# from schema import schema


# cl = j.clients.atyourservice.get(AYS_INSTANCE).api
cl = Client(AYS_INSTANCE)


# def service_view(s):
#     """
#     generate a dict that represent a service from a service object
#     """


# def run_view(run):
#     """
#     generate a dict that represent a run
#     """
#     obj = {
#         'key': run.key,
#         'state': str(run.state),
#         'steps': [],
#         'epoch': run.model.dbobj.lastModDate,
#     }
#     for step in run.steps:
#         aystep = {
#             'number': step.dbobj.number,
#             'jobs': [],
#             'state': step.state
#         }
#         for job in step.jobs:
#             logs = []
#             for log in job.model.dbobj.logs:
#                 log_dict = {}
#                 log_record = log.to_dict()
#                 log_dict['epoch'] = log_record['epoch'] if 'epoch' in log_record else None
#                 log_dict['log'] = log_record['log'] if 'log' in log_record else None
#                 log_dict['level'] = log_record['level'] if 'level' in log_record else None
#                 log_dict['category'] = log_record['category'] if 'category' in log_record else None
#                 log_dict['tags'] = log_record['tags'] if 'tags' in log_record else None
#                 logs.append(log_dict)

#             aystep['jobs'].append({
#                 'key': job.model.key,
#                 'action_name': job.model.dbobj.actionName,
#                 'actor_name': job.model.dbobj.actorName,
#                 'service_key': job.model.dbobj.serviceKey,
#                 'service_name': job.model.dbobj.serviceName,
#                 'state': str(job.model.dbobj.state),
#                 'logs': logs
#             })
#         obj['steps'].append(aystep)

#     return obj


class StepType(graphene.ObjectType):
    number = graphene.Int()
    #jobs = graphene.List()
    state = graphene.String()


class RunType(graphene.ObjectType):
    key = graphene.String()
    state = graphene.String()
    steps = graphene.List(StepType)
    epoch = graphene.String()


class ActionType(graphene.ObjectType):
    name = graphene.String()
    code = graphene.String()
    state = graphene.Boolean()
    # recurring = graphene.Dict() # period info


class EventType(graphene.ObjectType):
    actions = graphene.List(graphene.String)
    command = graphene.String()
    channel = graphene.String()
    tags = graphene.List(graphene.String)


class ServiceType(graphene.ObjectType):

    repository = graphene.Field(lambda: RepositoryType)

    def resolve_repository(self, info):
        return json2obj(json.dumps(cl.ays.getRepository(self.repository).json()))

    def resolve_parent(self, info):
        if self.parent is not None:
            return json2obj(json.dumps(cl.ays.getServiceByName(repository=self.repository, role=self.parent.role, name=self.parent.name).json()))

    def resolve_children(self, info):
        children = [cl.ays.getServiceByName(
            repository=self.repository, role=x.role, name=x.name).json() for x in self.children]
        return json2obj(json.dumps(children))

    def resolve_producers(self, info):
        producers = [cl.ays.getServiceByName(
            repository=self.repository, role=x.role, name=x.name).json() for x in self.producers]
        return json2obj(json.dumps(producers))

    def resolve_consumers(self, info):
        consumers = [cl.ays.getServiceByName(
            repository=self.repository, role=x.role, name=x.name).json() for x in self.consumers]
        return json2obj(json.dumps(consumers))

    key = graphene.String()
    name = graphene.String()

    role = graphene.String()
    # # data = graphene.Dict()
    state = graphene.String()
    path = graphene.String()
    actions = graphene.List(graphene.String)
    parent = graphene.Field(lambda: ServiceType)
    producers = graphene.List(lambda: ServiceType)
    consumers = graphene.List(lambda: ServiceType)
    children = graphene.List(lambda: ServiceType)
    events = graphene.List(EventType)


class BlueprintType(graphene.ObjectType):
    name = graphene.String()
    path = graphene.String()
    content = graphene.String()
    hash = graphene.String()
    archived = graphene.Boolean()


class RepositoryType(graphene.ObjectType):
    name = graphene.String()
    gitUrl = graphene.String()
    path = graphene.String()

    blueprints = graphene.List(BlueprintType)
    services = graphene.List(ServiceType)

    actors = graphene.List(lambda: ActorType)
    templates = graphene.List(lambda: TemplateType)

    def resolve_blueprints(self, info):
        blueprints = cl.ays.listBlueprints(self.name).json()

        return json2obj(json.dumps(blueprints))

    def resolve_services(self, info):
        services = cl.ays.listServices(self.name).json()
        fullservices = [cl.ays.getServiceByName(repository=self.name, role=s[
                                                'role'], name=s['name']).json() for s in services]

        return json2obj(json.dumps(fullservices))

    def resolve_actors(self, info):
        actors = cl.ays.listActors(self.name).json()
        fullactors = [cl.ays.getActorByName(repository=self.name, actor=a[
                                            'name']).json() for a in actors]

        return json2obj(json.dumps(fullactors))

    def resolve_templates(self, info):
        templates = cl.ays.listTemplates(repository=self.name).json()
        return json2obj(json.dumps(templates))
        # fulltemplates = [cl.ays.getTemplate(repository=self.name, name=t['name']).json() for t in templates]

        # return json2obj(json.dumps(fulltemplates))


class ActorType(graphene.ObjectType):
    name = graphene.String()
    schema = graphene.String()
    actions = graphene.Field(ActionType)


class JobType(graphene.ObjectType):
    key = graphene.String()
    actionName = graphene.String()
    serviceKey = graphene.String()
    serviceName = graphene.String()
    state = graphene.String()
    # logs = graphene.List(graphene.String)
    result = graphene.String()

    # actor = ?


class TemplateType(graphene.ObjectType):

    name = graphene.String()
    action = graphene.String()
    schema = graphene.String()
    config = graphene.String()  # is it dict?
    path = graphene.String()
    role = graphene.String()


class Query(BaseQuery):
    hello = graphene.String()
    repositories = graphene.List(RepositoryType)
    repository = graphene.Field(RepositoryType, name=graphene.String())
    node = relay.Node.Field()

    def resolve_repositories(self, info):
        repos = cl.ays.listRepositories().json()
        return json2obj(json.dumps(repos))

    def resolve_repository(self, info, name):
        repo = cl.ays.getRepository(repository=name).json()
        return json2obj(json.dumps(repo))
