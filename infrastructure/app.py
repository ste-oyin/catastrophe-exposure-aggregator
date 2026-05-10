#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.backend_stack import BackendStack
from stacks.cache_stack import CacheStack
from stacks.database_stack import DatabaseStack
from stacks.frontend_stack import FrontendStack
from stacks.networking_stack import NetworkingStack

app = cdk.App()

env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
)

networking = NetworkingStack(app, "CatExposure-Networking", env=env)

database = DatabaseStack(
    app,
    "CatExposure-Database",
    vpc=networking.vpc,
    env=env,
)

cache = CacheStack(
    app,
    "CatExposure-Cache",
    vpc=networking.vpc,
    env=env,
)

backend = BackendStack(
    app,
    "CatExposure-Backend",
    vpc=networking.vpc,
    db_cluster=database.db_cluster,
    db_security_group_id=database.security_group.security_group_id,
    cache_security_group_id=cache.security_group.security_group_id,
    redis_endpoint=cache.redis_endpoint,
    redis_port=cache.redis_port,
    env=env,
)

frontend = FrontendStack(
    app,
    "CatExposure-Frontend",
    api_domain=backend.alb_dns,
    env=env,
)

cdk.Tags.of(app).add("Project", "CatastropheExposureAggregator")
cdk.Tags.of(app).add("ManagedBy", "CDK")

app.synth()
