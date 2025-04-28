#!/bin/bash
set -e

# Variables de configuración

PROJECT_ID="rundawn-newsletter"  # Reemplaza con tu ID de proyecto de GCP
SERVICE_NAME="tutor-agents-service"
REGION="europe-west1"  # Reemplaza con tu región preferida
SERVICE_ACCOUNT_NAME="${SERVICE_NAME}-sa"  # Nombre de la cuenta de servicio

# Verificar si el proyecto existe y establecerlo como el proyecto actual

echo "Verificando proyecto y configurando como proyecto actual..."
gcloud config set project ${PROJECT_ID}

# Habilitar las APIs necesarias (sólo primera vez)

echo "Habilitando APIs necesarias..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com iam.googleapis.com
# Crear un repositorio Docker en Artifact Registry (sólo primera vez)

echo "Creando repositorio Docker en Artifact Registry..."
gcloud artifacts repositories create docker-repo \
--repository-format=docker \
--location=${REGION} \
--description="Repositorio Docker para ${SERVICE_NAME}" \
|| echo "El repositorio ya existe, continuando..."

# Crear cuenta de servicio para Cloud Run (sólo primera vez)

echo "Creando cuenta de servicio para Cloud Run...",
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
--display-name="${SERVICE_NAME} Service Account" \
|| echo "La cuenta de servicio ya existe, continuando..."

# Asignar rol de acceso a Cloud Storage

echo "Configurando permisos para Cloud Storage..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
--role="roles/storage.objectAdmin"

# Asignar permisos para acceder a Secret Manager

echo "Configurando permisos para Secret Manager..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
--role="roles/secretmanager.secretAccessor"


# Construir la imagen de Docker

echo "Construyendo imagen de Docker..."
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/docker-repo/${SERVICE_NAME}"
gcloud builds submit --tag ${IMAGE_NAME}

# Desplegar en Cloud Run

echo "Desplegando en Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
--image=${IMAGE_NAME} \
--platform=managed \
--region=${REGION} \
--service-account="${SERVICE_ACCOUNT_NAME}" \
--allow-unauthenticated \
--memory=2Gi \
--cpu=1 \
--timeout=600s \
--set-env-vars="ENVIRONMENT=production" \
--set-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,OPIK_API_KEY=OPIK_API_KEY:latest

echo "¡Despliegue completado!"
echo "Tu servicio estará disponible en: $(gcloud run services describe ${SERVICE_NAME} --platform=managed --region=${REGION} --format='value(status.url)')"