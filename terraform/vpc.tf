variable "project_id" {}

variable "region" {
  description = "region"
}

# VPC
resource "google_compute_network" "main-vpc" {
  name                    = "${var.project_id}-vpc"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.project_id}-subnet"
  region        = var.region
  network       = google_compute_network.main-vpc.name
  ip_cidr_range = "10.10.0.0/24"
}

