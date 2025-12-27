import json
from typing import Any, Dict
from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_sqs as sqs,
    aws_sagemaker as sagemaker,
    aws_events as events,
    aws_events_targets as targets,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_codepipeline as codepipeline,
    aws_codebuild as codebuild,
    aws_codepipeline_actions as codepipelineactions
)
from aws_cdk.aws_iam import Role
from constructs import Construct
from pathlib import Path

class MlopsPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "CloudInfraQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        # Create a Code Pipeline using AWS CDK


        # Create a S3 Bucket
        bucket = s3.Bucket(self, "MlopsModelBucket", versioned=True)
        
        sagemakerArtifactBucket = s3.Bucket(
            self,'sagemakerArtifactBucket',
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED)
        

         
        sagemakerExecutionRole = Role(
            self,
            "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),

            ]
            )
            
        # Explicitly add CloudWatch Logging permissions
        sagemakerExecutionRole.add_to_policy(iam.PolicyStatement(
            resources=["*"],
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
                ]
            )
        )

        ## Create Sagemaker Pipeline tRigger Lambda Fucntion
        lambda_sagemaker = _lambda.Function(self, "SagemakerPipelineTrigger",
                                            runtime=_lambda.Runtime.PYTHON_3_9,
                                            handler="sagemaker_trigger.handler",
                                            code=_lambda.Code.from_asset("../lambda_package.zip"),
                                            memory_size=256
                                            )
        
        # Optional: Grant S3 access if needed
        lambda_sagemaker.add_to_role_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=["arn:aws:s3:::mlopspipelinestack-mlopsmodelbucket88eed9f0-lzsbdgp0dgqy/*"]
        ))
        
        # Add permission to trigger sagemaker pipeline
        lambda_sagemaker.add_to_role_policy(iam.PolicyStatement(
            actions=[
                "sagemaker:StartPipelineExecution",
                "sagemaker:DescribePipeline",
                "sagemaker:ListPipelineExecutions"
            ],
            resources=["*"]
        ))
        
      
        ## Create Deployment Lambda Function
        lambda_fn = _lambda.Function(self, "InferenceFucntion",
                                   runtime=_lambda.Runtime.PYTHON_3_9,
                                   handler="app.handler",
                                   #code=_lambda.Code.from_asset(str(Path(__file__).resolve().parent.parent.parent/ "lambda_inference")),
                                   code=_lambda.Code.from_asset("../lambda_package.zip"),
                                   memory_size=256)
         # Optional: Grant S3 access if needed
        lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=["arn:aws:s3:::mlopspipelinestack-mlopsmodelbucket88eed9f0-lzsbdgp0dgqy/*"]
        ))
        
        lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["s3:ListBucket"],
            resources=["arn:aws:s3:::mlopspipelinestack-mlopsmodelbucket88eed9f0-lzsbdgp0dgqy"]
        ))

        lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions = [
                "sagemaker:CreateModel",
                "sagemaker:CreateEndpoint",
                "sagemaker:CreateEndpointConfig",
                "sagemaker:DeleteEndpoint",
                "sagemaker:DescribeModel",
                "sagemaker:ListModelPackages",
            ],
            resources=['*']
        ))

        lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["iam:PassRole"],
            resources=["arn:aws:iam::252312373833:role/MlopsPipelineStack-SageMakerExecutionRole7843F3B8-84gSLJ2pWKPJ"]
        ))

        lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=["arn:aws:s3:::mlopspipelinestack-mlopsmodelbucket88eed9f0-lzsbdgp0dgqy/*"]
        ))


        # Create an Event rule to trigger Lambda on Sagemaker Model State Change
        lambda_trigger_rule = events.Rule(
            self, 'sagemaker-saket-mlops-model-approve-or-reject',
            event_pattern={
                "source": ["aws.sagemaker"],
                "detail_type": ["SageMaker Model Package State Change"],
                "detail": {
                    "ModelPackageGroupName": ["saket-mlops-model-group"],  # Trigger when model state changes
                    "ModelApprovalStatus": ["Approved"]
                }
            }
        )

        lambda_trigger_rule.add_target(targets.LambdaFunction(handler=lambda_fn))

        # Create an Event Rule to publish SNS Topic when Sagemaker Endpoint is Alive and In Service.

        sns_publish_topic = sns.Topic(
            self, "SagemakerEndpointTopic",
            topic_name="sagemaker-endpoint-notification",
            display_name="sagemaker-endpoint-notification"
        )

        sns_publish_topic.add_subscription(subscriptions.EmailSubscription("saketthavananilindan@gmail.com"))

       # sns_publish_topic.add_to_resource_policy(
        #    iam.PolicyStatement(
        #        principals=[iam.ServicePrincipal("events.amazonaws.com")],
         #       actions=["sns:Publish"],
          #      sid="AllowEventBridgeToPublish"
           # )
        #)
        
        
        sns_trigger_rule = events.Rule(
            self, 'sagemaker-endpoint-inservice-notification',
            event_pattern={
                "source": ["aws.sagemaker"],
                "detail_type": ["Sagemaker Endpoint State Change"],
                "detail": {
                    "EndpointStatus": ["IN_SERVICE"],
                    "EndpointName": ["mlops-endpoint"]
                }
            }
        )

        sns_trigger_rule.add_target(targets.SnsTopic(topic=sns_publish_topic))


        # Feature Store Groups & Roles
        feature_store_role = iam.Role(
            self,
            "FeatureStoreRole",
            assumed_by=iam.ServicePrincipal('sagemaker.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSagemakerFullAccess"
                )
            ]
        )

        sagemaker.CfnFeatureGroup(
            self,
            "DriverFeatureGroup",
            description="Feature group for storing driver entity features",
            event_time_feature_name="event_time",
            feature_group_name="driver_features_fg",
            record_identifier_feature_name="driver_id",
            feature_definitions=[
                sagemaker.CfnFeatureGroup.FeatureDefinitionProperty(
                    feature_name="driver_id",
                    feature_type="String",
                ),
                sagemaker.CfnFeatureGroup.FeatureDefinitionProperty(
                    feature_name='driver_age',
                    feature_type="Integral"
                ),
                sagemaker.CfnFeatureGroup.FeatureDefinitionProperty(
                    feature_name="driver_gender",
                    feature_type="String"
                ),
                sagemaker.CfnFeatureGroup.FeatureDefinitionProperty(
                    feature_name="driver_safety_score",
                    feature_type="Fractional"
                ),
                sagemaker.CfnFeatureGroup.FeatureDefinitionProperty(
                    feature_name="driver_style",
                    feature_type="String"
                ),
                sagemaker.CfnFeatureGroup.FeatureDefinitionProperty(
                    feature_name="event_time",
                    feature_type="String"
                ),
                
            ],
            online_store_config={
                "EnableOnlineStore": True
            },
            offline_store_config={
                "S3StorageConfig":{
                    # CDK will provision a default bucket if one is not specified
                    "S3Uri": "s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/feature_store/driver"
                    }
            },
            role_arn=feature_store_role.role_arn
        )