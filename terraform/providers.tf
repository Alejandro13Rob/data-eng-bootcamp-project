provider "google" {
  credentials = file("../credentials/key.json")
  project = var.project_id
  region  = var.region
}