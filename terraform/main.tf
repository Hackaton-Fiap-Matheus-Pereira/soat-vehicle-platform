terraform {
  required_version = ">= 1.6.0"
  required_providers {
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.32" }
  }
}

provider "kubernetes" {
  config_path    = var.kubeconfig
  config_context = var.kube_context
}

resource "kubernetes_namespace_v1" "soat" {
  metadata { name = var.namespace }
}

resource "kubernetes_secret_v1" "soat" {
  metadata {
    name      = "soat-secrets"
    namespace = kubernetes_namespace_v1.soat.metadata[0].name
  }
  data = {
    JWT_SECRET              = var.jwt_secret
    MYSQL_ROOT_PASSWORD     = var.mysql_root_password
    AUTH_DB_PASSWORD        = var.auth_db_password
    VEHICLE_DB_PASSWORD     = var.vehicle_db_password
    BOOTSTRAP_ADMIN_PASSWORD = var.bootstrap_admin_password
    AUTH_DATABASE_URL       = "mysql+aiomysql://auth_user:${var.auth_db_password}@auth-db:3306/auth_db"
    VEHICLE_DATABASE_URL    = "mysql+aiomysql://vehicle_user:${var.vehicle_db_password}@vehicle-db:3306/vehicle_db"
  }
  type = "Opaque"
}

resource "kubernetes_config_map_v1" "soat" {
  metadata {
    name      = "soat-config"
    namespace = kubernetes_namespace_v1.soat.metadata[0].name
  }
  data = { BOOTSTRAP_ADMIN_EMAIL = var.bootstrap_admin_email }
}

