variable "google_api_key" {
  description = "Google Vision API key for OCR"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub personal access token for Amplify to access the repo"
  type        = string
  sensitive   = true
}

variable "github_repo" {
  description = "GitHub repository URL"
  type        = string
  default     = "https://github.com/liuyang19900520/WordsMaker"
}

variable "github_branch" {
  description = "Branch to deploy"
  type        = string
  default     = "master"
}
