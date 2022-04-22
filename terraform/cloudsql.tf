variable "instance_name" {
  description = "Name for the sql instance database"
  default     = "data-bootcamp-capstone-project"
}

variable "instance_tier" {
  description = "Tier for the sql instance database"
  default = "db-f1-micro"
}

variable "disk_space" {
  description = "Disk space for the sql instance database"
  default = 10
}

variable "database_version" {
  description = "The PostgreSQL version to use"
  default     = "POSTGRES_12"
}

variable "db_name" { }
variable "db_username" { }
variable "db_password" { }


resource "google_sql_database_instance" "sql_instance" {
  name              = var.instance_name
  database_version  = var.database_version
  region            = var.region

  settings {
    tier      = var.instance_tier
    disk_size = var.disk_space

    location_preference {
      zone = var.region
    }

    ip_configuration {
      authorized_networks {
        value           = "0.0.0.0/0"
        name            = "test-cluster"
      }
    }
  }

  deletion_protection = "false"
}

resource "google_sql_database" "database" {
  name     = var.db_name
  instance = google_sql_database_instance.sql_instance.name
}

resource "google_sql_user" "users" {
  name     = var.db_username
  instance = google_sql_database_instance.sql_instance.name
  host     = "*"
  password = var.db_password
}