terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

variable "cloudflare_token" {
  type        = string
  description = "Token de API de Cloudflare con permisos para R2"
  sensitive   = true
}

variable "cloudflare_account_id" {
  type        = string
  description = "ID de la cuenta de Cloudflare"
}

provider "cloudflare" {
  api_token = var.cloudflare_token
}

resource "cloudflare_r2_bucket" "bucket_raw" {
  account_id = var.cloudflare_account_id
  name       = "raw"
  location   = "WEUR" 
}