# Route53 resources (optional, only if domain is provided)
data "aws_route53_zone" "primary" {
  count        = var.domain != "" ? 1 : 0
  name         = replace(var.domain, "/^.*\\.([^.]+\\.[^.]+)$/", "$1")
  private_zone = false
}

resource "aws_route53_record" "app" {
  count   = var.domain != "" ? 1 : 0
  zone_id = data.aws_route53_zone.primary[0].zone_id
  name    = var.domain
  type    = "A"
  alias {
    name                   = aws_lb.alb.dns_name
    zone_id                = aws_lb.alb.zone_id
    evaluate_target_health = true
  }
}