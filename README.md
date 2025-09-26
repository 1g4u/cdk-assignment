# cdk-assignment

## Instructions

Write a CDK application that:

- Includes an ECR repository for storing application images
- Hosts the sample application (from `src`) in AWS
- Defines a VPC for the new resources to reside within

There is no need to deploy the application to AWS. It is enough for `npm run cdk synth` to complete without errors.

Also include:

- A Dockerfile that can be used to build an image for this application
- A GitHub Actions workflow that builds the Docker image and uploads it to the ECR repo

Be prepared to discuss your design choices, particularly around networking, security, and availability during the interview.

----
----
# Assignment Updates

## Changed folders/files
 - .github => GitHub Actions workflow
 - docker => Dockerfile for building image
 - cdk-python => CDK project, which contains two stacks:
    * InfraStack to deploy ECR, VPC, OIDC Provider, IAM Role, ECS Cluster
    * AppStack to deploy/update the Typescript App to ECS

## Steps

1. Update the values of githubRepo, account, region variables in cdk/app.py

2. Deploy InfraStack via cdk
```bash
cd cdk

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

cdk bootstrap
cdk deploy InfraStack
```

2. Config settings for the Github repository -> Settings -> Secrets and variables -> Actions -> New Repository Secret
    - *AWS_ACCOUNT_ID*
    - *AWS_REGION*
    - *AWS_OIDC_ROLE*

3. Push code change, which triggers GitHub Actions to build docker image and push to ECR

4. Update the value of imageTag in cdk/app.py to deploy newer version of the app
```bash
cdk deploy AppStack
```

