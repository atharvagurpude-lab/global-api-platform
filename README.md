# Global Product API Platform

A secure, versioned and performance-optimized product API platform built on AWS.

## Project Overview

The Global Product API provides REST endpoints for managing product data using Amazon API Gateway, AWS Lambda and Amazon DynamoDB.

The platform includes:

- Amazon Cognito JWT authentication
- Group-based authorization
- API Gateway usage plans and API keys
- AWS WAF protection
- Amazon CloudFront edge caching
- AWS Certificate Manager TLS
- API versioning with v1 and v2
- CloudWatch logging and monitoring
- AWS X-Ray tracing
- GitHub Actions CI/CD

## Architecture

```text
Client
  |
  v
CloudFront
  |
  v
API Gateway
  |
  +------------------+
  |                  |
  v                  v
Cognito JWT        AWS WAF
Authentication     Protection
  |
  v
AWS Lambda
  |
  v
DynamoDB
  |
  v
Product Data

Observability:
API Gateway + Lambda + CloudFront
          |
          v
CloudWatch + X-Ray

CI/CD:
GitHub
  |
  v
GitHub Actions
  |
  v
AWS Lambda
```

## Technology Stack

| Component | Technology |
|---|---|
| API | Amazon API Gateway |
| Compute | AWS Lambda |
| Database | Amazon DynamoDB |
| Authentication | Amazon Cognito |
| Authorization | Cognito Groups |
| API Protection | AWS WAF |
| Rate Limiting | API Gateway Usage Plans / API Keys |
| CDN / Caching | Amazon CloudFront |
| TLS | AWS Certificate Manager |
| Monitoring | Amazon CloudWatch |
| Tracing | AWS X-Ray |
| API Specification | OpenAPI 3.0.3 |
| CI/CD | GitHub Actions |
| Source Control | GitHub |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/products` | List all products |
| POST | `/products` | Create a product |
| GET | `/products/{id}` | Get a product |
| PUT | `/products/{id}` | Update a product |
| DELETE | `/products/{id}` | Delete a product |

### Product Input

```json
{
  "name": "AWS Cloud Course",
  "price": 999,
  "category": "Training"
```
}

## Performance

Amazon CloudFront is used for edge caching of suitable API responses.

Measured testing demonstrated lower latency for cached CloudFront requests compared with direct origin requests.

Lambda provisioned concurrency was also configured to address cold-start behavior.

## Observability

The platform uses:

- API Gateway access logs
- Structured Lambda logs
- AWS X-Ray tracing
- CloudWatch dashboards
- Request and error metrics
- Latency percentile metrics
- CloudWatch alarms
- SNS notifications

## CI/CD

GitHub Actions provides automated CI/CD.

On every push to the `main` branch:

1. The repository is checked out.
2. Python 3.12 is configured.
3. Automated tests are executed.
4. The Lambda deployment package is created.
5. GitHub Actions authenticates to AWS using GitHub OIDC.
6. The Lambda function is automatically updated.

The pipeline was also tested with an intentional failing test. The workflow correctly failed at the test stage. The test was then removed and the pipeline returned to a successful state.

## Repository Structure

```text
global-api-platform/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── lambda/
│   └── lambda_function.py
├── tests/
│   └── test_lambda_syntax.py
├── dynamodb-policy.json
├── lambda-trust-policy.json
├── openapi.yaml
├── product-create-schema.json
├── product-update-schema.json
├── .gitignore
└── README.md
```

## Deployment

Deployment is automated through GitHub Actions after a successful push to the `main` branch.

GitHub Actions authenticates to AWS using OpenID Connect (OIDC), avoiding long-lived AWS access keys in the repository.

## Security Notes

Never commit:

- AWS access keys
- AWS secret keys
- Cognito passwords
- API key values
- Access tokens
- Private credentials

Use only personal test accounts and sample data.

## API Documentation

The OpenAPI specification is available in:

```text
openapi.yaml
```

It can be rendered using a Swagger/OpenAPI-compatible documentation viewer.

## Project Status

The project demonstrates:

- Secure API authentication and authorization
- API rate limiting
- WAF protection
- CloudFront edge caching
- TLS-secured API access
- API versioning and deprecation
- CloudWatch monitoring
- X-Ray tracing
- Automated GitHub Actions deployment
- Automated test validation



<!-- CI functional tests verified -->
