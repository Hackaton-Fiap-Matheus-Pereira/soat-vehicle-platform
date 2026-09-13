variable "kubeconfig" { type = string, default = "~/.kube/config" }
variable "kube_context" { type = string, default = null }
variable "namespace" { type = string, default = "soat" }
variable "jwt_secret" { type = string, sensitive = true }
variable "mysql_root_password" { type = string, sensitive = true }
variable "auth_db_password" { type = string, sensitive = true }
variable "vehicle_db_password" { type = string, sensitive = true }
variable "bootstrap_admin_email" { type = string, default = "admin@example.com" }
variable "bootstrap_admin_password" { type = string, sensitive = true }

