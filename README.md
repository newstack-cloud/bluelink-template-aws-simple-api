# Bluelink AWS Simple API Template Repository

This repository contains the **AWS Simple API** template for the [Bluelink CLI](https://bluelink.dev). It provides an AWS-native starting point for serverless API projects using API Gateway, Lambda, DynamoDB, and VPC.

## Purpose

The AWS Simple API template demonstrates:
- AWS-specific resource types (`aws/apiGateway/api`, `aws/lambda/function`, `aws/dynamodb/table`)
- AWS Flex VPC (`aws/flex/vpc`) with automatic networking configuration
- Bluelink's link system for automatic IAM permissions and VPC integration
- Lambda function packaging workflow with Python and boto3
- Real DynamoDB integration with proper error handling
- Production-ready AWS architecture patterns

## Template Structure

```
├── README.md                          # This file (for maintainers)
├── README.md.tmpl                     # Template for generated project README
├── LICENSE                            # Apache 2.0 License
├── .gitignore                         # Python/IDE/Bluelink/Lambda build ignores
├── bluelink.deploy.jsonc.tmpl         # Deployment configuration template
├── project.blueprint.yaml.tmpl        # Blueprint in YAML format (template)
├── project.blueprint.jsonc.tmpl       # Blueprint in JSONC format (template)
├── requirements.txt                   # Python dependencies (boto3)
├── scripts/
│   └── package-lambda.sh              # Lambda packaging script
└── handlers/                          # Lambda handler code
    ├── __init__.py
    └── resources/
        ├── __init__.py
        └── update_resource.py         # PATCH /resources/{resourceId} handler
```

## Template Variables

The Bluelink CLI replaces these Go template variables during project initialization:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{.ProjectName}}` | User-provided project name | `my-api` |
| `{{.NormalisedProjectName}}` | Normalized version (lowercase, hyphens) | `my-api` |
| `{{.BlueprintFormat}}` | Selected format (yaml or jsonc) | `yaml` |

## File Naming Conventions

- **`.tmpl` extension**: Files with Go template syntax that need processing
  - `README.md.tmpl` → `README.md`
  - `project.blueprint.yaml.tmpl` → `project.blueprint.yaml`
  - `bluelink.deploy.jsonc.tmpl` → `bluelink.deploy.jsonc`

- **No `.tmpl` extension**: Files copied as-is
  - `handlers/**/*.py`
  - `requirements.txt`
  - `.gitignore`
  - `scripts/**/*.sh`

## Template Philosophy

### 1. **AWS-Native, Not Cloud-Agnostic**
- Uses AWS-specific resource types (`aws/apiGateway/api`, `aws/lambda/function`, `aws/dynamodb/table`)
- Demonstrates AWS Flex VPC for automatic networking
- Showcases Bluelink's link system for IAM and VPC configuration
- Separates this from cloud-agnostic templates (e.g., `scaffold`)

### 2. **Real AWS Integration**
- Uses boto3 for DynamoDB access (not mocked responses)
- Demonstrates proper Lambda handler structure
- Shows environment variable injection via Bluelink links
- Includes production-ready error handling patterns

### 3. **Deployment-Ready**
- Includes Lambda packaging script (`scripts/package-lambda.sh`)
- Shows how to create deployment artifacts
- Demonstrates VPC networking with Lambda
- Includes proper .gitignore for build artifacts

### 4. **Bluelink Link System**
- Demonstrates automatic IAM policy generation (Lambda → DynamoDB)
- Shows automatic VPC configuration (Lambda → VPC)
- Uses label-based resource discovery (API Gateway → Lambda)
- Minimizes manual configuration through intelligent links

### 5. **Format Flexibility**
- Provides both YAML and JSONC blueprint formats
- CLI selects one based on user preference
- Both are kept in sync with identical structure

## AWS Resources Defined

### VPC (`aws/flex/vpc`)
- Flexible VPC with standard preset
- Automatic subnet creation (public/private)
- Security group management
- NAT gateway configuration
- Uses linkSelector for label-based discovery

### API Gateway (`aws/apiGateway/api`)
- HTTP API (not REST API)
- CORS configuration
- Throttling settings
- Optional custom domain support
- Optional JWT authorization
- Uses linkSelector to discover Lambda functions

### Lambda Function (`aws/lambda/function`)
- Python 3.13 runtime
- VPC configuration via links
- DynamoDB access via links
- Environment variable injection
- X-Ray tracing enabled
- Route configuration for API Gateway

### DynamoDB Table (`aws/dynamodb/table`)
- PAY_PER_REQUEST billing mode
- Point-in-time recovery enabled
- KMS encryption
- DynamoDB Streams enabled
- Partition key configuration

## Maintaining This Template

### Adding New Features

1. **Update both blueprint formats**: Make identical changes to `.yaml.tmpl` and `.jsonc.tmpl`
2. **Update AWS resource types**: Use correct `aws/service/resource` format
3. **Maintain link configuration**: Ensure links are properly configured for IAM/VPC
4. **Update handler code**: If adding new endpoints, create example handlers
5. **Update packaging script**: If handler structure changes
6. **Update README.md.tmpl**: Document new features in generated project README
7. **Test with CLI**: Run `bluelink init --template aws-simple-api` to verify

### Keeping Format Parity

When updating blueprints, ensure:
- YAML and JSONC have identical structure
- Comments are adapted to format (# vs //)
- AWS resource types are consistent
- Link configurations match exactly
- Template variables are used consistently

### Maintaining Link Behavior

When modifying links:
- Lambda → DynamoDB: Generates read/write IAM policies
- Lambda → VPC: Configures subnets and security groups
- API → Lambda: Uses label selectors, not direct references

## Testing Changes

Before committing changes:

1. **Test template generation**:
   ```bash
   bluelink init --template aws-simple-api --project-name test-api
   cd test-api
   ```

2. **Verify template variables were replaced**:
   ```bash
   # Should see "test-api", not "{{.ProjectName}}"
   cat README.md
   grep -r "{{.ProjectName}}" . --include="*.yaml" --include="*.jsonc" --include="*.md"
   ```

3. **Test Lambda packaging**:
   ```bash
   ./scripts/package-lambda.sh
   # Should create dist/lambda-package.zip
   ```

4. **Validate blueprint syntax**:
   ```bash
   bluelink validate --blueprint-file project.blueprint.yaml
   ```

5. **Test both formats**:
   ```bash
   bluelink init --template aws-simple-api --blueprint-format yaml --project-name test-yaml
   bluelink init --template aws-simple-api --blueprint-format jsonc --project-name test-jsonc
   ```

6. **Verify AWS resource types**:
   ```bash
   # Check that all resources use aws/* types, not celerity/*
   grep -E "type: (aws|celerity)/" project.blueprint.yaml.tmpl
   ```

7. **Test deployment (optional but recommended)**:
   ```bash
   # Set AWS credentials
   export AWS_ACCESS_KEY_ID=...
   export AWS_SECRET_ACCESS_KEY=...

   # Package and deploy
   ./scripts/package-lambda.sh
   bluelink deploy --instance-name test-deployment

   # Clean up
   bluelink destroy --instance-name test-deployment
   ```

## Lambda Packaging

The template includes `scripts/package-lambda.sh` which:
1. Creates `dist/package/` directory
2. Installs requirements.txt into package directory
3. Copies handler code to package directory
4. Creates `dist/lambda-package.zip`

When updating:
- Test with empty requirements.txt
- Test with commented-out dependencies
- Verify handler imports work correctly
- Check ZIP structure matches Lambda expectations

## Bluelink Link System

This template demonstrates the linkSelector pattern for connecting resources:

### LinkSelector Pattern
Resources connect using `linkSelector` with label matching:

```yaml
# Resource A declares what it wants to connect to
updateResourceHandler:
  metadata:
    labels:
      app: {{.NormalisedProjectName}}
      network: {{.NormalisedProjectName}}
  linkSelector:
    byLabel:
      app: {{.NormalisedProjectName}}  # Finds resources with this label

# Resource B with matching label - automatically linked
resourceStore:
  metadata:
    labels:
      app: {{.NormalisedProjectName}}  # Matched by Lambda's linkSelector

# Resource C discovers Resource A via its labels
appVpc:
  linkSelector:
    byLabel:
      network: {{.NormalisedProjectName}}  # Finds Lambda with network label
```

### How It Works
1. **Labels on resources** act as identifiers
2. **LinkSelector on resources** queries for matching labels
3. **Bidirectional matching** - either resource can initiate the link
4. **Provider-defined behavior** - AWS provider determines what happens (IAM policies, VPC config, etc.)

### Annotations for Link Behavior
```yaml
updateResourceHandler:
  metadata:
    annotations:
      aws.lambda.function.http: true
      aws.lambda.function.http.method: "PATCH"
      aws.lambda.function.http.path: "/resources/{resourceId}"
```

Annotations guide HOW the link is established (e.g., which HTTP method/path for API Gateway integration).

## Contributing

When contributing to this template:

1. Open an issue describing the proposed change
2. Ensure changes are AWS-specific (not cloud-agnostic)
3. Update all relevant files (both blueprint formats, README, handler code, scripts)
4. Maintain Bluelink link system patterns
5. Test thoroughly with Bluelink CLI and actual AWS deployment
6. Submit a PR with clear description of changes
7. Use conventional commit messages

### AWS-Specific Guidelines

- Leverage Bluelink links for automatic IAM/VPC configuration
- Include realistic AWS examples (not mocked)
- Document AWS-specific features (X-Ray, CloudWatch, etc.)
- Show production-ready patterns (encryption, backups, etc.)

## Support

- **Template Issues**: [Bluelink GitHub Issues](https://github.com/newstack-cloud/bluelink/issues)
- **AWS Provider Issues**: [Bluelink AWS Provider](https://github.com/newstack-cloud/bluelink-provider-aws/issues)
- **Documentation**: [Bluelink Docs](https://bluelink.dev)
- **AWS Documentation**: [AWS Docs](https://docs.aws.amazon.com/)

## License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.
