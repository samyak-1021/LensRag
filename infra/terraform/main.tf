# Illustrative infrastructure-as-code: a managed Postgres + a Docker host to run
# the stack. This is a TEMPLATE (DigitalOcean is not free) — the zero-cost paths
# are `docker compose up` locally or the Render blueprint. See ./README.md.

terraform {
  required_version = ">= 1.5"
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

# Managed Postgres 16 — stores document metadata + embeddings.
resource "digitalocean_database_cluster" "postgres" {
  name       = "${var.project}-db"
  engine     = "pg"
  version    = "16"
  size       = var.db_size
  region     = var.region
  node_count = 1
}

# A small Docker droplet that runs the API + dashboard via docker compose.
resource "digitalocean_droplet" "app" {
  name     = "${var.project}-app"
  image    = "docker-20-04"
  region   = var.region
  size     = var.droplet_size
  tags     = [var.project]
  ssh_keys = var.ssh_key_fingerprints
}
