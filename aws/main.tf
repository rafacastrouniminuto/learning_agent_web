# Terraform Configuration for Learning Agent Web on AWS
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend para guardar el estado en S3
  backend "s3" {
    bucket = "learning-agent-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "Learning Agent Web"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "Living Lab UNIMINUTO"
    }
  }
}

# Variables
variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "learning-agent"
}

# VPC y Networking
module "vpc" {
  source = "./modules/vpc"
  
  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = "10.0.0.0/16"
}

# RDS MySQL
module "database" {
  source = "./modules/rds"
  
  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  db_instance_class     = "db.t3.micro"
  db_allocated_storage  = 20
  db_name               = "learningagent"
  db_username           = "admin"
}

# ElastiCache Redis
module "cache" {
  source = "./modules/elasticache"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  node_type          = "cache.t3.micro"
}

# S3 Buckets
module "storage" {
  source = "./modules/s3"
  
  project_name = var.project_name
  environment  = var.environment
}

# ECS Fargate
module "ecs" {
  source = "./modules/ecs"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids
  
  container_image    = "${module.ecr.repository_url}:latest"
  container_port     = 8000
  cpu                = 512   # 0.5 vCPU
  memory             = 1024  # 1 GB
  desired_count      = 2
  
  db_host            = module.database.db_endpoint
  db_name            = module.database.db_name
  redis_host         = module.cache.redis_endpoint
}

# ECR Repository
module "ecr" {
  source = "./modules/ecr"
  
  project_name = var.project_name
  environment  = var.environment
}

# Application Load Balancer
module "alb" {
  source = "./modules/alb"
  
  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  target_group_arn  = module.ecs.target_group_arn
}

# CloudFront CDN
module "cloudfront" {
  source = "./modules/cloudfront"
  
  project_name = var.project_name
  environment  = var.environment
  alb_domain   = module.alb.alb_dns_name
}

# Secrets Manager
module "secrets" {
  source = "./modules/secrets"
  
  project_name = var.project_name
  environment  = var.environment
  
  db_password = module.database.db_password
}

# Outputs
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain"
  value       = module.cloudfront.cloudfront_domain
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = module.ecr.repository_url
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.database.db_endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.cache.redis_endpoint
  sensitive   = true
}