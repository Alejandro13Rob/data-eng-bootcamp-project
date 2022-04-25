output "region" {
  value       = var.region
  description = "GCloud Region"
}

output "project_id" {
  value       = var.project_id
  description = "GCloud Project ID"
}

/*
output "subnet" {
  value = google_compute_subnetwork.subnet.id
}

output "main-vpc" {
  value = google_compute_network.main-vpc.id
}
*/

output "kubernetes_cluster_name" {
  value       = google_container_cluster.primary.name
  description = "GKE Cluster Name"
}

output "kubernetes_cluster_host" {
  value       = google_container_cluster.primary.endpoint
  description = "GKE Cluster Host"
}

output "instance_connection_name" {
  value = google_sql_database_instance.master.connection_name
}

output "instance_ip_address" {
  value = google_sql_database_instance.master.ip_address
}
