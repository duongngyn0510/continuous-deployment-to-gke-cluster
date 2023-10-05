variable "project_id" {
  description = "The project ID to host the cluster in"
  default     = "language-translate-401102"
}

variable "region" {
  description = "The region the cluster in"
  default     = "us-central1-f"
}

variable "k8s" {
  description = "GKE for simple mlops"
  default     = "mlops-gke"
}
