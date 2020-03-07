# aws-lambda-flask
aws-lambda-flask

* AWS API Gateway -> Resources -> Create Method -> Use Lambda Proxy integration -> check
* AWS API Gateway -> Settings -> Binary Media Types -> multipart/form-data
* Browser -> XMLHttpRequest -> xhr.setRequestHeader('Accept', 'multipart/form-data');
* AWS IAM -> Roles -> LAMBDA_ROLE -> Permissions -> Attach policies -> AWSLambdaVPCAccessExecutionRole
* AWS EC2 -> Security Groups -> iAmProdDB, iAmLambdaAndNeedDBAccess
* AWS Lambda -> VPC -> Default VPC or VPC of RDS
* AWS Lambda -> Security Group -> iAmLambdaAndNeedDBAccess
* AWS VPC -> Endpoints -> Create Endpoint -> AWS Services -> com.amazonaws.ap-northeast-2.s3 -> Default VPC
* AWS S3 -> Permissions -> Block all public access -> Uncheck
* AWS S3 -> Permissions -> Bucket Policy
```
{
    "Version": "2012-10-17",
    "Id": "Policy1582338959560",
    "Statement": [
        {
            "Sid": "Stmt1582338958005",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::BUCKET_NAME/*"
        },
        {
            "Sid": "Stmt1582338958006",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::AWS_USER_ID:role/service-role/LAMBDA_ROLE"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::BUCKET_NAME/*"
        }
    ]
}
```
