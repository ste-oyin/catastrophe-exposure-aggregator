from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticache as elasticache
from constructs import Construct


class CacheStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.security_group = ec2.SecurityGroup(
            self,
            "CacheSg",
            vpc=vpc,
            description="Security group for ElastiCache Redis",
            allow_all_outbound=False,
        )

        private_subnets = vpc.select_subnets(
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
        )

        subnet_group = elasticache.CfnSubnetGroup(
            self,
            "RedisSubnetGroup",
            description="Subnet group for Redis cache",
            subnet_ids=private_subnets.subnet_ids,
        )

        self.redis_cluster = elasticache.CfnReplicationGroup(
            self,
            "RedisReplicationGroup",
            replication_group_description="Redis cache for catastrophe-exposure-aggregator",
            engine="redis",
            cache_node_type="cache.t4g.micro",
            num_cache_clusters=1,
            automatic_failover_enabled=False,
            cache_subnet_group_name=subnet_group.ref,
            security_group_ids=[self.security_group.security_group_id],
            at_rest_encryption_enabled=True,
            transit_encryption_enabled=True,
            engine_version="7.1",
            port=6379,
        )

        self.redis_endpoint = self.redis_cluster.attr_primary_end_point_address
        self.redis_port = self.redis_cluster.attr_primary_end_point_port
