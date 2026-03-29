data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  ecr_repo   = "${local.account_id}.dkr.ecr.ap-northeast-1.amazonaws.com/words-maker"
}

# ── Secrets Manager ──────────────────────────────────────────────────────────

data "aws_secretsmanager_secret_version" "google_api_key" {
  secret_id = "words-maker/google-api-key"
}

data "aws_secretsmanager_secret_version" "github_token" {
  secret_id = "words-maker/github-token"
}

# ── DynamoDB ────────────────────────────────────────────────────────────────

resource "aws_dynamodb_table" "words" {
  name         = "words_maker"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "word"

  attribute {
    name = "word"
    type = "S"
  }
}

# ── ECR Repository ───────────────────────────────────────────────────────────

resource "aws_ecr_repository" "lambda" {
  name                 = "words-maker"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_lifecycle_policy" "lambda" {
  repository = aws_ecr_repository.lambda.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep only last 3 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 3
      }
      action = { type = "expire" }
    }]
  })
}

# ── IAM Role for Lambda ──────────────────────────────────────────────────────

resource "aws_iam_role" "lambda" {
  name = "words-maker-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_dynamodb" {
  name = "words-maker-dynamodb"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Scan",
        "dynamodb:Query",
        "dynamodb:DescribeTable",
        "dynamodb:CreateTable",
      ]
      Resource = aws_dynamodb_table.words.arn
    }]
  })
}

# ── Lambda Function (container image) ───────────────────────────────────────

resource "aws_lambda_function" "pipeline" {
  function_name = "words-maker-pipeline"
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${local.ecr_repo}:latest"

  timeout     = 300
  memory_size = 1024

  environment {
    variables = {
      GOOGLE_API_KEY            = data.aws_secretsmanager_secret_version.google_api_key.secret_string
      DYNAMODB_TABLE_NAME       = aws_dynamodb_table.words.name
      EUDIC_DEFAULT_CATEGORY_ID = "0"
      PDF_START_PAGE            = "1"
      PDF_END_PAGE              = "15"
    }
  }

  depends_on = [aws_ecr_repository.lambda]
}

# ── API Gateway HTTP API ─────────────────────────────────────────────────────

resource "aws_apigatewayv2_api" "pipeline" {
  name          = "words-maker-pipeline"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "OPTIONS"]
    allow_headers = ["content-type"]
  }
}

resource "aws_apigatewayv2_integration" "pipeline" {
  api_id                 = aws_apigatewayv2_api.pipeline.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.pipeline.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "pipeline" {
  api_id    = aws_apigatewayv2_api.pipeline.id
  route_key = "POST /"
  target    = "integrations/${aws_apigatewayv2_integration.pipeline.id}"
}

resource "aws_apigatewayv2_stage" "pipeline" {
  api_id      = aws_apigatewayv2_api.pipeline.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pipeline.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.pipeline.execution_arn}/*/*"
}

# ── Amplify ──────────────────────────────────────────────────────────────────

resource "aws_amplify_app" "frontend" {
  name         = "words-maker"
  repository   = var.github_repo
  access_token = data.aws_secretsmanager_secret_version.github_token.secret_string
  platform     = "WEB_COMPUTE"

  build_spec = <<-YAML
    version: 1
    applications:
      - appRoot: frontend
        frontend:
          phases:
            preBuild:
              commands:
                - npm ci
            build:
              commands:
                - npm run build
          artifacts:
            baseDirectory: .next
            files:
              - '**/*'
          cache:
            paths:
              - node_modules/**/*
  YAML

  environment_variables = {
    LAMBDA_FUNCTION_URL          = aws_apigatewayv2_stage.pipeline.invoke_url
    AMPLIFY_MONOREPO_APP_ROOT    = "frontend"
  }
}

resource "aws_amplify_branch" "master" {
  app_id      = aws_amplify_app.frontend.id
  branch_name = var.github_branch

  framework = "Next.js - SSR"
  stage     = "PRODUCTION"
}
