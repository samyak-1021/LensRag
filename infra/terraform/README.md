# Terraform (illustrative IaC)

A small, valid Terraform config that provisions a managed **Postgres 16** cluster
and a **Docker droplet** to run the stack — included to show the deployment shape
as code.

> **Note:** DigitalOcean is not free, so this is a template, not the demo path.
> For zero-cost running use `docker compose up` locally, or the `render.yaml`
> blueprint at the repo root.

## Usage

```bash
export DIGITALOCEAN_TOKEN=... # or pass -var="do_token=..."
terraform init
terraform plan
terraform apply
```

`terraform output database_uri` gives the Postgres connection string (prefix it
with `postgresql+asyncpg://` for `LENSRAG_DATABASE_URL`).
