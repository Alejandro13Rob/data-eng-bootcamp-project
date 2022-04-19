terraform {
  required_providers {
    google = {
      version = "= 3.54.0"
    }
  }
}

provider "google" {
  credentials = file("../credentials/key.json")
  project = var.project_id
  region  = var.region
}