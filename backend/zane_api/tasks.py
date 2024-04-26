import docker.errors
from celery import shared_task

from .docker_operations import (
    expose_docker_service_to_http,
    create_docker_volume,
    create_service_from_docker_registry,
    create_project_resources,
    cleanup_project_resources,
    cleanup_docker_service_resources,
    unexpose_docker_service_from_http,
)
from .models import (
    DockerDeployment,
    PortConfiguration,
    Project,
    ArchivedProject,
    ArchivedDockerService,
)


@shared_task
def deploy_docker_service(deployment_hash: str):
    deployment: DockerDeployment | None = (
        DockerDeployment.objects.filter(hash=deployment_hash)
        .select_related("service", "service__project")
        .prefetch_related(
            "service__volumes",
            "service__urls",
            "service__ports",
            "service__env_variables",
        )
        .first()
    )
    if deployment is None:
        raise DockerDeployment.DoesNotExist(
            "Cannot execute a deploy a non existent deployment."
        )

    if deployment.deployment_status == DockerDeployment.DeploymentStatus.QUEUED:
        deployment.deployment_status = DockerDeployment.DeploymentStatus.PREPARING
        deployment.save()
    # TODO (#67) : send system logs when the resources are created
    service = deployment.service
    for volume in service.volumes.all():
        create_docker_volume(volume, service=service)
    create_service_from_docker_registry(deployment)

    http_port: PortConfiguration = service.ports.filter(host__isnull=True).first()
    if http_port is not None:
        expose_docker_service_to_http(service)
    # TODO Create scheduled task for monitoring


@shared_task(
    autoretry_for=(docker.errors.APIError,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
)
def create_docker_resources_for_project(project_slug: str):
    create_project_resources(project=Project.objects.get(slug=project_slug))


@shared_task(
    autoretry_for=(docker.errors.APIError, TimeoutError),
    retry_kwargs={"max_retries": 3, "countdown": 5},
)
def delete_docker_resources_for_project(archived_project_id: int):
    archived_project = ArchivedProject.objects.get(pk=archived_project_id)

    archived_docker_services = (
        ArchivedDockerService.objects.filter(project=archived_project)
        .select_related("project")
        .prefetch_related("volumes", "urls")
    )

    for docker_service in archived_docker_services:
        cleanup_docker_service_resources(docker_service)
        unexpose_docker_service_from_http(docker_service)

    cleanup_project_resources(archived_project)


@shared_task(
    autoretry_for=(docker.errors.APIError, TimeoutError),
    retry_kwargs={"max_retries": 3, "countdown": 5},
)
def delete_resources_for_docker_service(archived_service_id: id):
    archived_service = (
        ArchivedDockerService.objects.filter(id=archived_service_id)
        .select_related("project")
        .prefetch_related("volumes", "urls")
    ).first()
    if archived_service is None:
        raise Exception(
            f"Cannot execute a deploy a non existent archived service with id={archived_service_id}."
        )
    cleanup_docker_service_resources(archived_service)
    unexpose_docker_service_from_http(archived_service)


@shared_task
def monitor_docker_service_deployments(deployment_hash: str):
    deployment: DockerDeployment | None = (
        DockerDeployment.objects.filter(hash=deployment_hash)
        .select_related("service", "service__project")
        .prefetch_related(
            "service__volumes",
            "service__urls",
            "service__ports",
            "service__env_variables",
        )
        .first()
    )
    if deployment is None:
        raise DockerDeployment.DoesNotExist("Cannot monitor a non existent deployment.")
