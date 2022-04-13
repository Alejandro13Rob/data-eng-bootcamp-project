module "gke" {
  source = "./modules/gke"

  project_id    = var.project_id
  cluster_name  = "airflow-gke-data-engineering-bootcamp"
  zone          = var.zone
  vpc_id        = module.vpc.vpc
  subnet_id     = module.vpc.private_subnets[0]
  gke_num_nodes = var.gke_num_nodes
  machine_type  = var.machine_type
}

module "vpc" {
  source = "./modules/vpc"

  project_id = var.project_id
}