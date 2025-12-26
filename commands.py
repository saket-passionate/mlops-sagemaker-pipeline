########## Commnds to create Lambda package ##########3

## cd /lambda_inference
## pip install -r requirements.txt -t .
## zip -r ../lambda_package.zip .
## Reference this lambda_package in cdk code





###### Command to approve the sagmaker model package group

#aws sagemaker update-model-package \
 #   --model-package-arn arn:aws:sagemaker:ca-central-1:252312373833:model-package/saket-mlops-model-group/6 \
  #  --model-approval-status Approved

"""
docker run --rm \
  -v $(pwd)/input:/opt/ml/processing/input/ \
  -v $(pwd)/preprocess.py:/opt/ml/processing/code/preprocess.py \
  -v $(pwd)/output:/opt/ml/processing/train/ \
  sagemaker-processing:latest \
  python /opt/ml/processing/code/preprocess.py


  docker tag processing_image:latest 252312373833.dkr.ecr.ca-central-1.amazonaws.com/sagemaker-processing:latest

  docker push 252312373833.dkr.ecr.ca-central-1.amazonaws.com/sagemaker-processing:latest


"""




