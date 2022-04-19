#!/usr/bin/env bash

# Once the cluster is created, set the kubectl context:
gcloud container clusters get-credentials $(terraform output -raw kubernetes_cluster_name) --region $(terraform output -raw region)

echo "Cluster info"
kubectl cluster-info

# Create the NFS namespace and server
echo "Installing NFS Server"
cd ..
kubectl create namespace nfs
kubectl -n nfs apply -f nfs-server.yaml
# Export the server
export NFS_SERVER=$(kubectl -n nfs get service/nfs-server -o jsonpath="{.spec.clusterIP}")
# Create a namespace for storage deployment
kubectl create namespace storage
# Add chart for the NFS-provisioner
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
# Install NFS-external-provisioner
helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
    --namespace storage \
    --set nfs.server=$NFS_SERVER \
    --set nfs.path=/

echo "Installing airflow"
# Fetch the official Helm of Apache Airflow, then update the repo to make you got the latest version of it
kubectl create namespace airflow
helm repo add apache-airflow https://airflow.apache.org
helm repo update
helm search repo airflow
# Deploy Airflow with Helm install
helm install airflow apache-airflow/airflow --namespace airflow --debug

# Create secrets for the service account, for connections and for your private key
kubectl create secret generic service-account --from-file=credentials/key.json -n airflow
kubectl create secret generic airflow-connections --from-env-file=.env -n airflow
kubectl create secret generic airflow-ssh-git-secret --from-file=gitSshKey=/Users/your-user/.ssh/id_rsa -n airflow

echo "Create ConfigMap for variables"
kubectl create configmap airflow-variables --from-env-file=.variables -n airflow
kubectl get configmap airflow-variables -o yaml -n airflow

# Finally, upgrade your Airflow instance
echo "Update airflow with repo"
helm upgrade --install airflow apache-airflow/airflow -n airflow -f values.yaml --debug

