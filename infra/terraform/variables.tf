variable "do_token" {
  description = "DigitalOcean API token."
  type        = string
  sensitive   = true
}

variable "project" {
  description = "Name prefix for created resources."
  type        = string
  default     = "lensrag"
}

variable "region" {
  description = "DigitalOcean region slug (e.g. blr1, nyc3)."
  type        = string
  default     = "blr1"
}

variable "db_size" {
  description = "Managed database node size."
  type        = string
  default     = "db-s-1vcpu-1gb"
}

variable "droplet_size" {
  description = "App droplet size."
  type        = string
  default     = "s-1vcpu-1gb"
}

variable "ssh_key_fingerprints" {
  description = "SSH key fingerprints authorised on the droplet."
  type        = list(string)
  default     = []
}
