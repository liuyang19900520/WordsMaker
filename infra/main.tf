data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  ecr_repo   = "${local.account_id}.dkr.ecr.ap-northeast-1.amazonaws.com/words-maker"
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
      GOOGLE_API_KEY            = var.google_api_key
      DYNAMODB_TABLE_NAME       = aws_dynamodb_table.words.name
      EUDIC_DEFAULT_CATEGORY_ID = "0"
      PDF_START_PAGE            = "1"
      PDF_END_PAGE              = "15"
    }
  }

  depends_on = [aws_ecr_repository.lambda]
}

resource "aws_lambda_function_url" "pipeline" {
  function_name      = aws_lambda_function.pipeline.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["POST"]
    allow_headers = ["content-type"]
  }
}

# ── Amplify ──────────────────────────────────────────────────────────────────

resource "aws_amplify_app" "frontend" {
  name         = "words-maker"
  repository   = var.github_repo
  access_token = var.github_token
  platform     = "WEB_COMPUTE"

  build_spec = <<-YAML
    version: 1
    applications:
      - frontend:
          phases:
            preBuild:
              commands:
                - cd frontend && npm ci
            build:
              commands:
                - npm run build
          artifacts:
            baseDirectory: frontend/.next
            files:
              - '**/*'
          cache:
            paths:
              - frontend/node_modules/**/*
        appRoot: frontend
  YAML

  environment_variables = {
    LAMBDA_FUNCTION_URL = aws_lambda_function_url.pipeline.function_url
  }
}

resource "aws_amplify_branch" "master" {
  app_id      = aws_amplify_app.frontend.id
  branch_name = var.github_branch

  framework = "Next.js - SSR"
  stage     = "PRODUCTION"
}
