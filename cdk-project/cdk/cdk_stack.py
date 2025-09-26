from aws_cdk import (
    # Duration,
    Stack,
    CfnOutput,
    aws_iam as iam,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    aws_ecs_patterns as ecs_patterns
)
from constructs import Construct

#ref: https://docs.aws.amazon.com/cdk/v2/guide/ecs-example.html

class InfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, service: str, github_repo: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Creates ECR repo
        image_repo = ecr.Repository(self, "EcrRepo", repository_name=f"{service}-repo")

        # Creates VPC to host ECS
        vpc = ec2.Vpc(self, "EcsVpc", vpc_name=f"{service}-vpc", max_azs=3)

        # Create OIDC provider for Github Actions
        oidc = iam.OpenIdConnectProvider(
            self, "GithubActionsOIDC",
            url = "https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"]
        )

        # Create IAM role to connect Github Actions to AWS
        role = iam.Role(
            self, "GithubActionsRole",
            assumed_by=iam.WebIdentityPrincipal(
                oidc.open_id_connect_provider_arn,
                conditions={
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": ["sts.amazonaws.com"]
                    },
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": [f"repo:{github_repo}:*"]
                    }
                }
            ),
            description=f"Role for GitHub Actions to push to ECR from repo {github_repo}"
        )
        # Output IAM role arn
        CfnOutput(self, "GithubActionsRoleArn", value=role.role_arn)

        # Attach ECR permissions to the role
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:CompleteLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:InitiateLayerUpload",
                    "ecr:PutImage"
                ],
                resources=[ image_repo.repository_arn ]
            )
        )
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ecr:GetAuthorizationToken",
                ],
                resources=[ "*" ]
            )            
        )

        # Creates ECS cluster
        cluster = ecs.Cluster(self, "EcsCluster", vpc=vpc, cluster_name=f"{service}-cluster")

class AppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, service: str, tag: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Retrieve ECS cluster object
        cluster = ecs.Cluster.from_cluster_attributes(self, "EcsCluster",
            cluster_name=f"{service}-cluster",
            vpc=ec2.Vpc.from_lookup( self, "EcsVpc", vpc_name=f"{service}-vpc" )
        )

        # Create ECS with ALB
        fargate = ecs_patterns.ApplicationLoadBalancedFargateService(self, "Fargate",
            cluster=cluster,
            cpu=256,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(
                    repository=ecr.Repository.from_repository_name(
                        self,
                        "EcrRepo",
                        repository_name=f"{service}-repo"
                    ),
                    tag=tag
                ),
                container_port=3000
              ),
            memory_limit_mib=512,
            public_load_balancer=True
        )

        fargate.target_group.configure_health_check(
            path="/api/status",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
            healthy_http_codes="200-299"
        )
