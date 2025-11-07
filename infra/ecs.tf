resource "aws_ecs_cluster" "this" {
  name = "${var.project}-cluster"
}

resource "aws_ecs_task_definition" "web" {
  family="${var.project}-web"
  requires_compatibilities=["FARGATE"]
  network_mode="awsvpc"
  cpu=256
  memory=512
  execution_role_arn=aws_iam_role.ecs_exec.arn
  task_role_arn=aws_iam_role.ecs_task.arn
  container_definitions = jsonencode([{
    name="web", image="${var.ecr_web_uri}:latest", essential=true,
    portMappings=[{containerPort=3000, hostPort=3000}],
    logConfiguration={logDriver="awslogs", options={
      awslogs-group=aws_cloudwatch_log_group.web.name, awslogs-region=var.region, awslogs-stream-prefix="ecs"
    }}
  }])
}

resource "aws_ecs_task_definition" "api" {
  family="${var.project}-api"
  requires_compatibilities=["FARGATE"]
  network_mode="awsvpc"
  cpu=256
  memory=512
  execution_role_arn=aws_iam_role.ecs_exec.arn
  task_role_arn=aws_iam_role.ecs_task.arn
  container_definitions = jsonencode([{
    name="api", image="${var.ecr_api_uri}:latest", essential=true,
    portMappings=[{containerPort=8000, hostPort=8000}],
    logConfiguration={logDriver="awslogs", options={
      awslogs-group=aws_cloudwatch_log_group.api.name, awslogs-region=var.region, awslogs-stream-prefix="ecs"
    }}
  }])
}

resource "aws_ecs_service" "web" {
  name            = "${var.project}-web-svc"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.web.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups   = [aws_security_group.app.id]
    assign_public_ip  = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.web.arn
    container_name   = "web"
    container_port   = 3000
  }
  
  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200
}

resource "aws_ecs_service" "api" {
  name            = "${var.project}-api-svc"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type      = "FARGATE"
  
  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups   = [aws_security_group.app.id]
    assign_public_ip  = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }
  
  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200
}
