variable "raw_layer_bucket" {}
variable "staging_layer_bucket" {}
variable "dataproc_scripts_bucket" {}
variable "movies_reviews_script" {}
variable "logs_reviews_script" {}
variable "dataproc_temp_bucket" {}

// Create Raw Layer bucket
resource "google_storage_bucket" "raw_layer_bucket" {
  name          = var.raw_layer_bucket
  location      = var.region
  force_destroy = true
  project       = var.project_id
}

// Upload files to bucket
resource "google_storage_bucket_object" "user_purchase_csv" {
  name   = "user_purchase.csv"
  source = "../data/user_purchase.csv"
  bucket = google_storage_bucket.raw_layer_bucket.name
}

resource "google_storage_bucket_object" "movie_reviews_csv" {
  name   = "movie_reviews.csv"
  source = "../data/movie_reviews.csv"
  bucket = google_storage_bucket.raw_layer_bucket.name
}

resource "google_storage_bucket_object" "log_reviews_csv" {
  name   = "log_reviews.csv"
  source = "../data/log_reviews.csv"
  bucket = google_storage_bucket.raw_layer_bucket.name
}

// Create Staging Layer bucket
resource "google_storage_bucket" "staging_layer_bucket" {
  name          = var.staging_layer_bucket
  location      = var.region
  force_destroy = true
  project       = var.project_id
}

// Processing scripts for the data
resource "google_storage_bucket" "processing_scripts_bucket" {
  name          = var.dataproc_scripts_bucket
  location      = var.region
  force_destroy = true
  project       = var.project_id
}

resource "google_storage_bucket_object" "movie_processing_script" {
  name   = var.movies_reviews_script
  source = "../spark/movie_reviews.py"
  bucket = google_storage_bucket.processing_scripts_bucket.name
}

resource "google_storage_bucket_object" "logs_processing_script" {
  name   = var.logs_reviews_script
  source = "../spark/log_reviews.py"
  bucket = google_storage_bucket.processing_scripts_bucket.name
}

// Dataproc Temp Bucket for Dataproc Cluster
resource "google_storage_bucket" "dataproc_temp_bucket" {
  name          = var.dataproc_temp_bucket
  location      = var.region
  force_destroy = true
  project       = var.project_id
}
