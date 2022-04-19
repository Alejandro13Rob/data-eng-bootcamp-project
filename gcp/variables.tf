
variable "env" {
  description = "Environment name"
}

variable "project_id" {
  description = "project id"
  default = "stone-bounty-346922"
}

variable "credentials_file" {
  description = "Credentials file"
  default = "credentials/key.json"
 }

variable "region" {
  description = "region"
}

variable "location" {
  description = "location"
}

variable "user_name" {
  description = "Default user name used as sufix"
  default = "ultrainla3"
}

variable "user_email" {
  description = "Default user email that is able to trigger CF"
  default = "ultrainla3@gmail.com"
}

variable "database_version" {
  description = "The MySQL, PostgreSQL or SQL Server (beta) version to use. "
  default     = "POSTGRES_12"
}


#GKE
variable "gke_num_nodes" {
  default     = 2
  description = "number of gke nodes"
}

variable "machine_type" {
  type    = string
  default = "n1-standard-1"
}
