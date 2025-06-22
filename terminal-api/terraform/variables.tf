variable "api_key" {
  description = "API key for terminal access"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "AWS region"
  default     = "us-east-1"
}
