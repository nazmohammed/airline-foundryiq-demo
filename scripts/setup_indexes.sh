#!/bin/bash
#
# Setup Search Indexes for Zava Airlines
# Creates Azure AI Search indexes for customer service, operations, and loyalty data
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

log_step "Creating Search Indexes for Zava Airlines"

API_VERSION="2024-11-01-preview"

create_index() {
    local name=$1
    local payload=$2
    
    log_info "Creating index: $name"
    
    HTTP_CODE=$(curl -s -o /tmp/index_response.json -w "%{http_code}" \
        -X PUT "${SEARCH_ENDPOINT}/indexes/${name}?api-version=${API_VERSION}" \
        -H "api-key: ${SEARCH_KEY}" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
        log_success "Created index: $name"
    else
        log_warn "Index $name may already exist or error (HTTP $HTTP_CODE)"
    fi
}

# 1. Customer Service Index
log_info "Creating index-customer-service..."
create_index "index-customer-service" '{
    "name": "index-customer-service",
    "fields": [
        {"name": "id", "type": "Edm.String", "key": true, "filterable": true},
        {"name": "title", "type": "Edm.String", "searchable": true, "filterable": true},
        {"name": "content", "type": "Edm.String", "searchable": true},
        {"name": "category", "type": "Edm.String", "filterable": true, "facetable": true},
        {"name": "policy_type", "type": "Edm.String", "filterable": true},
        {"name": "last_updated", "type": "Edm.DateTimeOffset", "filterable": true, "sortable": true},
        {"name": "content_vector", "type": "Collection(Edm.Single)", "searchable": true, "dimensions": 3072, "vectorSearchProfile": "default-profile"}
    ],
    "vectorSearch": {
        "algorithms": [{"name": "default-algo", "kind": "hnsw"}],
        "profiles": [{"name": "default-profile", "algorithmConfigurationName": "default-algo"}]
    }
}'

# 2. Operations Index
log_info "Creating index-operations..."
create_index "index-operations" '{
    "name": "index-operations",
    "fields": [
        {"name": "id", "type": "Edm.String", "key": true, "filterable": true},
        {"name": "title", "type": "Edm.String", "searchable": true, "filterable": true},
        {"name": "content", "type": "Edm.String", "searchable": true},
        {"name": "category", "type": "Edm.String", "filterable": true, "facetable": true},
        {"name": "region", "type": "Edm.String", "filterable": true, "facetable": true},
        {"name": "severity", "type": "Edm.String", "filterable": true},
        {"name": "effective_date", "type": "Edm.DateTimeOffset", "filterable": true, "sortable": true},
        {"name": "content_vector", "type": "Collection(Edm.Single)", "searchable": true, "dimensions": 3072, "vectorSearchProfile": "default-profile"}
    ],
    "vectorSearch": {
        "algorithms": [{"name": "default-algo", "kind": "hnsw"}],
        "profiles": [{"name": "default-profile", "algorithmConfigurationName": "default-algo"}]
    }
}'

# 3. Loyalty Index
log_info "Creating index-loyalty..."
create_index "index-loyalty" '{
    "name": "index-loyalty",
    "fields": [
        {"name": "id", "type": "Edm.String", "key": true, "filterable": true},
        {"name": "title", "type": "Edm.String", "searchable": true, "filterable": true},
        {"name": "content", "type": "Edm.String", "searchable": true},
        {"name": "category", "type": "Edm.String", "filterable": true, "facetable": true},
        {"name": "tier", "type": "Edm.String", "filterable": true, "facetable": true},
        {"name": "miles_value", "type": "Edm.Int32", "filterable": true, "sortable": true},
        {"name": "content_vector", "type": "Collection(Edm.Single)", "searchable": true, "dimensions": 3072, "vectorSearchProfile": "default-profile"}
    ],
    "vectorSearch": {
        "algorithms": [{"name": "default-algo", "kind": "hnsw"}],
        "profiles": [{"name": "default-profile", "algorithmConfigurationName": "default-algo"}]
    }
}'

log_success "All indexes created successfully!"
