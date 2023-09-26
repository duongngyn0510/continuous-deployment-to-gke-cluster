variable "project_id" {
  description = "The project ID to host the cluster in"
  default     = "mle-course-398013"
}

variable "region" {
  description = "The region the cluster in"
  default     = "us-central1-f"
}

variable "k8s" {
  description = "GKE for text_image_retrieval"
  default     = "text-image-retrieval"
}
