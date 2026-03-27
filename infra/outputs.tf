output "lambda_function_url" {
  description = "Lambda Function URL (set as LAMBDA_FUNCTION_URL in Amplify)"
  value       = aws_lambda_function_url.pipeline.function_url
}

output "amplify_app_url" {
  description = "Amplify default domain"
  value       = "https://${var.github_branch}.${aws_amplify_app.frontend.id}.amplifyapp.com"
}

output "dynamodb_table" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.words.name
}
