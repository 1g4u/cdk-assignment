#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.cdk_stack import InfraStack
from cdk.cdk_stack import AppStack

app = cdk.App()

svcName = "ts-svc"
githubRepo = "company/coderepo"

account = "123456789012"
region = "us-east-1"

imageTag = "to-be-updated"

prod = cdk.Environment(account=account, region=region)

infra_stack = InfraStack(app, "InfraStack", service=svcName, github_repo=githubRepo, env=prod)

app_stack = AppStack(app, "AppStack", service=svcName, tag=imageTag, env=prod)

app_stack.add_dependency(infra_stack)

app.synth()
