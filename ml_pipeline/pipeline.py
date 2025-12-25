import boto3
import sagemaker
from sagemaker.pipeline import PipelineModel
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.inputs import TrainingInput
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.parameters import ParameterInteger, ParameterString
from sagemaker.workflow.steps import ProcessingStep, TrainingStep, CreateModelStep
from sagemaker.workflow.properties import PropertyFile
from sagemaker.model import Model
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.processing import FrameworkProcessor, Processor


# S3 URIs for preprocessing and evaluation scripts
S3_PREPROCESSING_URI = (
    "s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/"
    "Demo/processing/input/code/preprocess.py"
)
S3_EVALUATION_URI = (
    "s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/"
    "Demo/evaluation/input/code/evaluation.py"
)


def get_session(region: str = "ca-central-1", bucket: str = "") -> sagemaker.session.Session:
    """
    Creates and returns a SageMaker session for the specified AWS region.
    Optionally specifies a default S3 bucket.
    """
    boto_session = boto3.Session(region_name=region)
    sagemaker_client = boto_session.client("sagemaker")

    return sagemaker.session.Session(
        boto_session=boto_session,
        sagemaker_client=sagemaker_client,
        default_bucket=bucket,
    )


def get_pipeline(
    region: str,
    role: str = None,
    bucket: str = None,
    pipeline_name: str = "MlopsPipeline",
    base_job_prefix: str = "SageMakerPipeline",
) -> Pipeline:
    """
    Creates and returns a SageMaker Pipeline with the following steps:
    - Data preprocessing using SKLearnProcessor
    - Model training using SKLearn estimator
    - Model evaluation using SKLearnProcessor
    """

    sagemaker_session = get_session(region, bucket=bucket)

    # Pipeline parameters for instance counts and types
    processing_instance_count = ParameterInteger(name="ProcessingInstanceCount", default_value=1)
    processing_instance_type = ParameterString(name="ProcessingInstanceType", default_value="ml.g5.xlarge")
    training_instance_type = ParameterString(name="TrainingInstanceType", default_value="ml.m4.xlarge")
    model_approval_status = ParameterString(name="ModelApprovalStatus", default_value="Approved")


    sklearn_processor = SKLearnProcessor(
        role=role,
        framework_version="1.2-1",
        sagemaker_session=sagemaker_session,
        instance_count=1,
        instance_type="ml.t3.medium",
        base_job_name=f"{base_job_prefix}/sklearn_preprocessor",
)
    
    custom_processor = Processor(
        image_uri="252312373833.dkr.ecr.ca-central-1.amazonaws.com/sm-processing-telematics:latest",
        sagemaker_session=sagemaker_session,
        role=role,
        base_job_name=f"{base_job_prefix}/custom-preprocess",
        instance_type="ml.g5.xlarge",
        instance_count=2

    )

    # Data preprocessing step
    # NOW use ProcessingStep with step_args (no source_dir here)
    processing_step = ProcessingStep(
        processor=custom_processor,
        name="PreprocessData",
        code='preprocess.py',
        inputs=[
            ProcessingInput(
                source="s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/processing/input/data",
                destination="/opt/ml/processing/input",
            ),
        ],
        outputs=[
            ProcessingOutput(
                output_name="train",
                source="/opt/ml/processing/train",
                destination="s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/processing/output/",
            ),
        ]
        
    )
   
    model_path = (
        "s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/"
        "Demo/training/model/"
    )

    # SKLearn estimator for training
    sklearn_estimator = SKLearn(
        entry_point="train.py",  # Local path to your training script
        framework_version="1.2-1",
        instance_type=training_instance_type,
        instance_count=1,
        role=role,
        sagemaker_session=sagemaker_session,
        base_job_name=f"{base_job_prefix}/train",
        output_path=model_path,
    )

    # Training step in pipeline
    training_step = TrainingStep(
        name="TrainModel",
        estimator=sklearn_estimator,
        inputs={
            "train": TrainingInput(
                s3_data=processing_step.properties.ProcessingOutputConfig.Outputs["train"].S3Output.S3Uri,
                content_type="text/csv",
            )
        },
    )

    # Define evaluation report property file
    evaluation_report = PropertyFile(
        name="EvaluationReport",
        output_name="evaluation",
        path="evaluation.json",
    )

    # SKLearn processor for evaluation
    eval_processor = SKLearnProcessor(
        framework_version="1.2-1",
        instance_count=1,
        instance_type=processing_instance_type,
        role=role,
        sagemaker_session=sagemaker_session,
        base_job_name=f"{base_job_prefix}/evaluation",
    )

    # Evaluation step in pipeline
    evaluation_step = ProcessingStep(
        name="EvaluateModel",
        processor=eval_processor,
        inputs=[
            ProcessingInput(
                source=training_step.properties.ModelArtifacts.S3ModelArtifacts,
                destination="/opt/ml/processing/model",
            ),
            ProcessingInput(
                source="s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/processing/output/train.csv",
                destination="/opt/ml/processing/train",
            ),
        ],
        outputs=[
            ProcessingOutput(
                output_name="evaluation",
                source="/opt/ml/processing/evaluation",
                destination="s3://mlopspipelinestack-sagemakerartifactbucket4252fcb9-fvqyn7tgtetp/Demo/evaluation/output/",
            ),
        ],
        code=S3_EVALUATION_URI,
        property_files=[evaluation_report],
    )


    # Register Model Using Model Registry

    
    from sagemaker.sklearn.model import SKLearnModel
    inference_model = SKLearnModel(
        model_data=training_step.properties.ModelArtifacts.S3ModelArtifacts,
        role=role,
        entry_point="inference.py",
        framework_version="1.2-1",
        py_version="py3",
        sagemaker_session = sagemaker_session
        )

    model = PipelineModel(
        name='PipelineModel',
        role=role,
        models=[inference_model]
    )

    model_package_group_name = "saket-mlops-model-group"
  
    
    register_model_step = RegisterModel(
        name="RegisterModel",
        estimator=sklearn_estimator,
        content_types=["text/csv"],
        response_types=["test/csv"],
        inference_instances=["ml.t2.medium", "ml.m5.xlarge"],
        transform_instances=["ml.m5.xlarge"],
        model_package_group_name=model_package_group_name,
        model=model

    )
    
    # Define the pipeline with steps
    pipeline = Pipeline(
        name=pipeline_name,
        parameters=[
            processing_instance_count,
            processing_instance_type,
            training_instance_type,
            model_approval_status,
        ],
        steps=[
            processing_step,
            training_step,
            evaluation_step,
            register_model_step
        ],
        sagemaker_session=sagemaker_session,
    )

    return pipeline
