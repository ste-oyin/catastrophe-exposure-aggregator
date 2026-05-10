from aws_cdk import Duration, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_rds as rds
from constructs import Construct


class BackendStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        db_cluster: rds.IDatabaseCluster,
        db_security_group_id: str,
        cache_security_group_id: str,
        redis_endpoint: str,
        redis_port: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.ecr_repo = ecr.Repository(
            self,
            "BackendRepo",
            repository_name="catastrophe-exposure-aggregator-backend",
            image_tag_mutability=ecr.TagMutability.MUTABLE,
        )

        backend_sg = ec2.SecurityGroup(
            self,
            "BackendSg",
            vpc=vpc,
            description="Security group for ECS Fargate backend tasks",
            allow_all_outbound=True,
        )

        alb_sg = ec2.SecurityGroup(
            self,
            "AlbSg",
            vpc=vpc,
            description="Security group for the Application Load Balancer",
            allow_all_outbound=True,
        )
        alb_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP",
        )
        alb_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS",
        )

        backend_sg.add_ingress_rule(
            peer=alb_sg,
            connection=ec2.Port.tcp(8000),
            description="Allow traffic from ALB to Fargate on port 8000",
        )

        ec2.CfnSecurityGroupIngress(
            self,
            "BackendToDbIngress",
            ip_protocol="tcp",
            from_port=5432,
            to_port=5432,
            group_id=db_security_group_id,
            source_security_group_id=backend_sg.security_group_id,
            description="Allow PostgreSQL from backend tasks",
        )

        ec2.CfnSecurityGroupIngress(
            self,
            "BackendToCacheIngress",
            ip_protocol="tcp",
            from_port=6379,
            to_port=6379,
            group_id=cache_security_group_id,
            source_security_group_id=backend_sg.security_group_id,
            description="Allow Redis from backend tasks",
        )

        cluster = ecs.Cluster(
            self,
            "EcsCluster",
            vpc=vpc,
            container_insights_v2=ecs.ContainerInsights.ENABLED,
        )

        task_definition = ecs.FargateTaskDefinition(
            self,
            "BackendTaskDef",
            memory_limit_mib=1024,
            cpu=512,
        )

        task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"],
                resources=[db_cluster.secret.secret_arn],
            )
        )

        container = task_definition.add_container(
            "BackendContainer",
            image=ecs.ContainerImage.from_ecr_repository(self.ecr_repo, tag="latest"),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="backend",
                log_retention=logs.RetentionDays.TWO_WEEKS,
            ),
            environment={
                "REDIS_HOST": redis_endpoint,
                "REDIS_PORT": redis_port,
                "DB_SECRET_ARN": db_cluster.secret.secret_arn,
            },
            secrets={
                "DB_SECRET": ecs.Secret.from_secrets_manager(db_cluster.secret),
            },
            health_check=ecs.HealthCheck(
                command=[
                    "CMD-SHELL",
                    "python -c 'import urllib.request; urllib.request.urlopen(\"http://localhost:8000/health\")'",
                ],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                retries=3,
                start_period=Duration.seconds(60),
            ),
        )
        container.add_port_mappings(
            ecs.PortMapping(container_port=8000, protocol=ecs.Protocol.TCP),
        )

        self.fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "BackendService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=2,
            listener_port=80,
            public_load_balancer=True,
            assign_public_ip=False,
            task_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            ),
            security_groups=[backend_sg],
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
            enable_execute_command=True,
        )

        self.fargate_service.load_balancer.add_security_group(alb_sg)

        self.fargate_service.target_group.configure_health_check(
            path="/health",
            healthy_http_codes="200",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
        )

        scaling = self.fargate_service.service.auto_scale_task_count(
            min_capacity=1,
            max_capacity=6,
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )

        self.alb_dns = self.fargate_service.load_balancer.load_balancer_dns_name
