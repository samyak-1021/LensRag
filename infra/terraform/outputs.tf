output "app_ip" {
  description = "Public IPv4 of the app droplet."
  value       = digitalocean_droplet.app.ipv4_address
}

output "database_uri" {
  description = "Connection URI for the managed Postgres cluster."
  value       = digitalocean_database_cluster.postgres.uri
  sensitive   = true
}
