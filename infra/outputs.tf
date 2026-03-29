output "lambda_function_url" {
  description = "API Gateway endpoint (set as LAMBDA_FUNCTION_URL in Amplify)"
  value       = aws_apigatewayv2_stage.pipeline.invoke_url
}

output "amplify_app_url" {
  description = "Amplify default domain"
  value       = "https://${var.github_branch}.${aws_amplify_app.frontend.id}.amplifyapp.com"
}

output "dynamodb_table" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.words.name
}

output "github_actions_role_arn" {
  description = "IAM Role ARN for GitHub Actions (set as GHA_ROLE_ARN secret in GitHub)"
  value       = aws_iam_role.github_actions.arn
}
