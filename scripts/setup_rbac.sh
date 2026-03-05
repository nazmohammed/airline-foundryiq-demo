#!/bin/bash
#
# Setup RBAC for Zava Airlines FoundryIQ + Agent Framework
# Assigns required roles for RBAC-only authentication
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

log_step "Setting up RBAC for Zava Airlines"

# Required role IDs
COGNITIVE_SERVICES_USER="a97b65f3-24c7-4388-baec-2e87135dc908"
COGNITIVE_SERVICES_CONTRIBUTOR="25fbc0a9-bd7c-42a3-aa1a-3b75d497ee68"
SEARCH_INDEX_DATA_CONTRIBUTOR="8ebe5a00-799e-43f5-93ac-243d3dce84a7"
SEARCH_INDEX_DATA_READER="1407120a-92aa-4202-b7e9-c0e197c71c8f"
SEARCH_SERVICE_CONTRIBUTOR="7ca78c08-252a-4471-8644-bb5ff32d4ba0"
STORAGE_BLOB_DATA_READER="2a2b9908-6ea1-4ae2-8e65-a410df84e7d1"

echo "Resource Group: ${RESOURCE_GROUP}"
echo "Subscription: ${SUBSCRIPTION_ID}"

az account set --subscription "${SUBSCRIPTION_ID}"

# Get current user
CURRENT_USER_ID=$(az ad signed-in-user show --query id -o tsv 2>/dev/null || echo "")
[ -n "${CURRENT_USER_ID}" ] && echo "Current User: ${CURRENT_USER_ID}"

# Get resource IDs
FOUNDRY_HUB_ID=$(az cognitiveservices account list -g "${RESOURCE_GROUP}" \
    --query "[?kind=='AIServices'].id | [0]" -o tsv 2>/dev/null)
SEARCH_ID=$(az search service list -g "${RESOURCE_GROUP}" \
    --query "[0].id" -o tsv 2>/dev/null)
STORAGE_ID=$(az storage account list -g "${RESOURCE_GROUP}" \
    --query "[0].id" -o tsv 2>/dev/null)

# Assign roles to current user
if [ -n "${CURRENT_USER_ID}" ]; then
    log_info "Assigning roles to current user..."
    
    [ -n "${FOUNDRY_HUB_ID}" ] && az role assignment create \
        --role "${COGNITIVE_SERVICES_USER}" --scope "${FOUNDRY_HUB_ID}" \
        --assignee "${CURRENT_USER_ID}" 2>/dev/null || true
    
    [ -n "${FOUNDRY_HUB_ID}" ] && az role assignment create \
        --role "${COGNITIVE_SERVICES_CONTRIBUTOR}" --scope "${FOUNDRY_HUB_ID}" \
        --assignee "${CURRENT_USER_ID}" 2>/dev/null || true
    
    [ -n "${SEARCH_ID}" ] && az role assignment create \
        --role "${SEARCH_INDEX_DATA_CONTRIBUTOR}" --scope "${SEARCH_ID}" \
        --assignee "${CURRENT_USER_ID}" 2>/dev/null || true
    
    [ -n "${SEARCH_ID}" ] && az role assignment create \
        --role "${SEARCH_SERVICE_CONTRIBUTOR}" --scope "${SEARCH_ID}" \
        --assignee "${CURRENT_USER_ID}" 2>/dev/null || true
    
    [ -n "${STORAGE_ID}" ] && az role assignment create \
        --role "${STORAGE_BLOB_DATA_READER}" --scope "${STORAGE_ID}" \
        --assignee "${CURRENT_USER_ID}" 2>/dev/null || true
    
    log_success "Roles assigned to current user"
fi

# Assign roles to UAMI if it exists
UAMI_PRINCIPAL_ID=$(az identity list -g "${RESOURCE_GROUP}" \
    --query "[0].principalId" -o tsv 2>/dev/null)

if [ -n "${UAMI_PRINCIPAL_ID}" ]; then
    log_info "Assigning roles to managed identity..."
    
    [ -n "${FOUNDRY_HUB_ID}" ] && az role assignment create \
        --role "${COGNITIVE_SERVICES_USER}" --scope "${FOUNDRY_HUB_ID}" \
        --assignee-object-id "${UAMI_PRINCIPAL_ID}" \
        --assignee-principal-type ServicePrincipal 2>/dev/null || true
    
    [ -n "${SEARCH_ID}" ] && az role assignment create \
        --role "${SEARCH_INDEX_DATA_READER}" --scope "${SEARCH_ID}" \
        --assignee-object-id "${UAMI_PRINCIPAL_ID}" \
        --assignee-principal-type ServicePrincipal 2>/dev/null || true
    
    [ -n "${STORAGE_ID}" ] && az role assignment create \
        --role "${STORAGE_BLOB_DATA_READER}" --scope "${STORAGE_ID}" \
        --assignee-object-id "${UAMI_PRINCIPAL_ID}" \
        --assignee-principal-type ServicePrincipal 2>/dev/null || true
    
    log_success "Roles assigned to managed identity"
fi

log_success "RBAC setup complete!"
