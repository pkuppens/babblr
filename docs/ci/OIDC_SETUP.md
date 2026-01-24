# OIDC Setup Guide

This guide explains how to set up OpenID Connect (OIDC) for secure, keyless authentication from GitHub Actions to cloud providers.

## What is OIDC?

OIDC (OpenID Connect) allows GitHub Actions to authenticate to cloud providers without long-lived secrets.

**Benefits**:
- No static credentials stored
- Short-lived tokens (< 1 hour)
- Reduced secret sprawl
- Automatic credential rotation
- Better audit trail

**Use cases**:
- Deploy to AWS, Azure, GCP
- Access cloud resources
- Push Docker images to registries
- Manage infrastructure

## How OIDC Works

```
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│   GitHub     │   (1)    │    GitHub    │   (2)    │    Cloud     │
│   Actions    ├─────────>│   OIDC       ├─────────>│   Provider   │
│   Workflow   │  Request │   Provider   │  Present │   (AWS/     │
│              │   Token  │              │   Token  │   Azure/GCP) │
└──────────────┘          └──────────────┘          └──────────────┘
       │                                                     │
       │                                                     │
       │              (3) Return Credentials                 │
       │<────────────────────────────────────────────────────┘
       │
       │
       ▼
 Use credentials
 to access cloud
 resources
```

**Flow**:
1. Workflow requests OIDC token from GitHub
2. Workflow presents token to cloud provider
3. Cloud provider validates token and returns temporary credentials
4. Workflow uses credentials to access resources

## AWS Setup

### Prerequisites
- AWS account with admin access
- GitHub repository

### Step 1: Create IAM Identity Provider

In AWS Console:

1. Go to **IAM** → **Identity providers** → **Add provider**
2. Select **OpenID Connect**
3. Enter provider URL: `https://token.actions.githubusercontent.com`
4. Click **Get thumbprint**
5. Audience: `sts.amazonaws.com`
6. Click **Add provider**

### Step 2: Create IAM Role

Create role with trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:OWNER/REPO:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

**Replace**:
- `ACCOUNT_ID` with your AWS account ID
- `OWNER/REPO` with your GitHub repository

**Attach policies**: Add permissions for what workflow needs (e.g., S3 access)

### Step 3: Update Workflow

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

permissions:
  id-token: write  # Required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::ACCOUNT_ID:role/GitHubActionsRole
          aws-region: us-east-1

      - name: Deploy to S3
        run: |
          aws s3 sync ./dist s3://my-bucket
```

### Step 4: Test

Push to main branch and verify deployment succeeds.

## Azure Setup

### Prerequisites
- Azure subscription
- GitHub repository

### Step 1: Create Service Principal

In Azure CLI:

```bash
# Create service principal
az ad sp create-for-rbac \
  --name "GitHubActions" \
  --role contributor \
  --scopes /subscriptions/SUBSCRIPTION_ID \
  --sdk-auth

# Note the output
```

### Step 2: Configure Federated Credentials

In Azure Portal:

1. Go to **Azure Active Directory** → **App registrations**
2. Find your service principal
3. Go to **Certificates & secrets** → **Federated credentials**
4. Click **Add credential**
5. Select **GitHub Actions deploying Azure resources**
6. Enter repository details
7. Click **Add**

### Step 3: Update Workflow

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Deploy to Azure
        run: |
          az webapp deploy --name my-app --resource-group my-rg
```

### Step 4: Add Secrets

Add these secrets in GitHub repo settings:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

## GCP Setup

### Prerequisites
- GCP project
- GitHub repository

### Step 1: Create Workload Identity Pool

In GCP Console:

1. Go to **IAM & Admin** → **Workload Identity Federation**
2. Click **Create Pool**
3. Name: `github-pool`
4. Click **Continue**

### Step 2: Add Provider

1. Click **Add Provider**
2. Select **OIDC**
3. Name: `github-provider`
4. Issuer: `https://token.actions.githubusercontent.com`
5. Audience: Default
6. Attribute mapping:
   - `google.subject` = `assertion.sub`
   - `attribute.repository` = `assertion.repository`
7. Click **Save**

### Step 3: Grant Permissions

```bash
# Allow GitHub Actions to assume service account
gcloud iam service-accounts add-iam-policy-binding \
  SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/OWNER/REPO"
```

### Step 4: Update Workflow

```yaml
name: Deploy to GCP

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Authenticate to GCP
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
          service_account: 'SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com'

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy my-service --image gcr.io/PROJECT_ID/my-image
```

## Docker Registry (GHCR)

For GitHub Container Registry:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
```

## Security Considerations

### Principle of Least Privilege

Grant minimal permissions required:

**Bad**:
```json
{
  "Effect": "Allow",
  "Action": "*",  # Too broad
  "Resource": "*"
}
```

**Good**:
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:PutObject",
    "s3:GetObject"
  ],
  "Resource": "arn:aws:s3:::my-specific-bucket/*"
}
```

### Restrict to Specific Branches

Lock down trust policy to specific branches:

```json
{
  "StringEquals": {
    "token.actions.githubusercontent.com:sub": "repo:OWNER/REPO:ref:refs/heads/main"
  }
}
```

Or specific environments:

```json
{
  "StringLike": {
    "token.actions.githubusercontent.com:sub": "repo:OWNER/REPO:environment:production"
  }
}
```

### Audit Token Claims

Log OIDC token claims for audit:

```yaml
- name: Show OIDC claims
  run: |
    echo "Actor: ${{ github.actor }}"
    echo "Repository: ${{ github.repository }}"
    echo "Ref: ${{ github.ref }}"
    echo "SHA: ${{ github.sha }}"
```

## Troubleshooting

### Token Validation Failed

**Symptom**: `Error: Unable to get OIDC token`

**Solutions**:
1. Verify `id-token: write` permission set
2. Check if OIDC provider URL is correct
3. Ensure audience matches

### Assume Role Failed

**Symptom**: `Error: Unable to assume role`

**Solutions**:
1. Check trust policy conditions
2. Verify repository name matches
3. Check if branch/environment matches

### Permission Denied

**Symptom**: `Error: Access denied`

**Solutions**:
1. Check IAM role permissions
2. Verify resource ARN/path
3. Ensure least privilege principles

## Migration from Static Secrets

### Step 1: Set Up OIDC

Follow setup guide above for your cloud provider.

### Step 2: Update Workflows

Replace secret-based auth with OIDC:

**Before**:
```yaml
- name: Configure AWS credentials
  run: |
    aws configure set aws_access_key_id ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws configure set aws_secret_access_key ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

**After**:
```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCOUNT_ID:role/GitHubActionsRole
    aws-region: us-east-1
```

### Step 3: Remove Old Secrets

1. Delete static credentials from GitHub Secrets
2. Delete static credentials from cloud provider
3. Rotate any potentially compromised credentials

### Step 4: Verify

Test all deployments work with OIDC.

## Best Practices

1. **Use OIDC whenever possible** - Eliminate long-lived secrets
2. **Restrict by branch/environment** - Production from main only
3. **Audit regularly** - Review who/what accessed resources
4. **Rotate nothing** - OIDC tokens auto-expire
5. **Document setup** - Keep notes on IAM roles and permissions

## Resources

- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [AWS OIDC Setup](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [Azure OIDC Setup](https://learn.microsoft.com/en-us/azure/active-directory/workload-identities/workload-identity-federation-create-trust-github)
- [GCP OIDC Setup](https://cloud.google.com/iam/docs/workload-identity-federation-with-github)
