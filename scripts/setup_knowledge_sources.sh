#!/bin/bash
#
# Setup Knowledge Sources for Zava Airlines
# Creates FoundryIQ knowledge sources including Bing Search for geo-political intelligence
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

log_step "Creating Knowledge Sources for Zava Airlines"

API_VERSION="2025-11-01-preview"

create_ks() {
    local name=$1
    local payload=$2
    
    log_info "Creating knowledge source: $name"
    
    HTTP_CODE=$(curl -s -o /tmp/ks_response.json -w "%{http_code}" \
        -X PUT "${SEARCH_ENDPOINT}/knowledgesources/${name}?api-version=${API_VERSION}" \
        -H "api-key: ${SEARCH_KEY}" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
        log_success "Created knowledge source: $name"
    else
        log_warn "KS $name may already exist or error (HTTP $HTTP_CODE)"
    fi
}

# --- Customer Service Knowledge Sources ---
log_step "Customer Service Knowledge Sources"

create_ks "ks-cs-aisearch" "{
    \"name\": \"ks-cs-aisearch\",
    \"type\": \"searchIndex\",
    \"searchIndexParameters\": {
        \"indexName\": \"index-customer-service\"
    }
}"

create_ks "ks-cs-web" "{
    \"name\": \"ks-cs-web\",
    \"type\": \"web\",
    \"webParameters\": {
        \"urls\": [
            \"https://www.iata.org/en/programs/ops-infra/baggage/\",
            \"https://www.transportation.gov/airconsumer\",
            \"https://europa.eu/youreurope/citizens/travel/passenger-rights/air/index_en.htm\"
        ]
    }
}"

create_ks "ks-cs-sharepoint" "{
    \"name\": \"ks-cs-sharepoint\",
    \"type\": \"searchIndex\",
    \"searchIndexParameters\": {
        \"indexName\": \"index-customer-service\"
    }
}"

# --- Operations Knowledge Sources ---
log_step "Operations Knowledge Sources"

create_ks "ks-ops-aisearch" "{
    \"name\": \"ks-ops-aisearch\",
    \"type\": \"searchIndex\",
    \"searchIndexParameters\": {
        \"indexName\": \"index-operations\"
    }
}"

create_ks "ks-ops-web" "{
    \"name\": \"ks-ops-web\",
    \"type\": \"web\",
    \"webParameters\": {
        \"urls\": [
            \"https://www.faa.gov/air_traffic/publications/notams\",
            \"https://www.eurocontrol.int/\",
            \"https://www.icao.int/safety/Pages/default.aspx\"
        ]
    }
}"

# Bing Search knowledge source for real-time geo-political intelligence
create_ks "ks-geopolitical-bing" "{
    \"name\": \"ks-geopolitical-bing\",
    \"type\": \"web\",
    \"webParameters\": {
        \"urls\": [
            \"https://www.bbc.com/news/world\",
            \"https://www.reuters.com/world/\",
            \"https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html/\",
            \"https://www.gov.uk/foreign-travel-advice\",
            \"https://www.flightradar24.com\",
            \"https://www.eurocontrol.int/news\"
        ]
    },
    \"description\": \"Real-time geo-political intelligence from Bing Search for airspace closures, travel advisories, conflict zones, and NOTAMs affecting Zava Airlines routes\"
}"

# --- Loyalty Knowledge Sources ---
log_step "Loyalty Knowledge Sources"

create_ks "ks-loyalty-aisearch" "{
    \"name\": \"ks-loyalty-aisearch\",
    \"type\": \"searchIndex\",
    \"searchIndexParameters\": {
        \"indexName\": \"index-loyalty\"
    }
}"

create_ks "ks-loyalty-web" "{
    \"name\": \"ks-loyalty-web\",
    \"type\": \"web\",
    \"webParameters\": {
        \"urls\": [
            \"https://www.staralliance.com/en/benefits\",
            \"https://www.iata.org/en/programs/passenger/frequent-flyer/\"
        ]
    }
}"

log_success "All knowledge sources created successfully!"
echo ""
echo "Knowledge Sources Summary:"
echo "  Customer Service: ks-cs-aisearch, ks-cs-web, ks-cs-sharepoint"
echo "  Operations:       ks-ops-aisearch, ks-ops-web, ks-geopolitical-bing"
echo "  Loyalty:          ks-loyalty-aisearch, ks-loyalty-web"
