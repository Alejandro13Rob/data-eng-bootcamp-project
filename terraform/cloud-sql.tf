variable "instance_name" {
  description = "Name for the sql instance database"
}
resource "random_id" "db_name_suffix" {
  byte_length = 4
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


resource "google_sql_database_instance" "master" {
  name              = "${var.instance_name}-instance-${random_id.db_name_suffix.hex}"
  region            = var.region
  database_version  = var.database_version

  settings {
    tier      = var.instance_tier
    availability_type = "REGIONAL"
    disk_size = var.disk_space
    ip_configuration {
      authorized_networks {
        value           = "0.0.0.0/0"
        name            = "test-cluster"
      }
    }
    location_preference {
      zone = "us-west1-a"
    }
  }

  deletion_protection = "false"
}

resource "google_sql_user" "main" {
  depends_on = [
    google_sql_database_instance.master
  ]
  name     = "main"
  instance = google_sql_database_instance.master.name
  host     = "*"
  password = var.db_password
}

resource "google_sql_database" "main" {
  depends_on = [
    google_sql_user.main
  ]
  name     = "main"
  instance = google_sql_database_instance.master.name
}
