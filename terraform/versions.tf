terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.54.0"
    }
  }

  required_version = ">= 0.14"
}