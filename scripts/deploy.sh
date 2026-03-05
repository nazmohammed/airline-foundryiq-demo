#!/bin/bash
#
# Zava Airlines - FoundryIQ + Agent Framework Demo - Full Deployment Script
#
# This script deploys all Azure resources and configures FoundryIQ:
# 1. Azure infrastructure via azd (OpenAI, Search, Storage, Container Apps)
# 2. User-Assigned Managed Identity with permissions
# 3. Search indexes with sample Zava Airlines data
# 4. Knowledge Sources (searchIndex, web, Bing Search for geo-political intel)
# 5. Knowledge Bases (kb-customer-service, kb-operations, kb-loyalty)
#
# Usage:
#   ./scripts/deploy.sh                    # Full deployment
#   ./scripts/deploy.sh --skip-infra       # Skip azd infrastructure
#   ./scripts/deploy.sh --help             # Show help
#
# Prerequisites:
#   - Azure CLI logged in (az login)
#   - azd CLI installed
#   - jq installed

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

SKIP_INFRA=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --skip-infra) SKIP_INFRA=true ;;
        --help)
            echo "Usage: ./scripts/deploy.sh [options]"
            echo "Options:"
            echo "  --skip-infra  Skip azd infrastructure deployment"
            echo "  --help        Show this help"
            exit 0
            ;;
    esac
done

# Run sub-scripts
run_subscript() {
    local script_name=$1
    local script_path="$SCRIPT_DIR/$script_name"
    
    if [ -f "$script_path" ]; then
        log_info "Running $script_name..."
        chmod +x "$script_path"
        bash "$script_path"
    else
        log_error "Script not found: $script_path"
        exit 1
    fi
}

# Main deployment flow
main() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  Zava Airlines - FoundryIQ + Agent Framework Deployment      ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Step 1: Infrastructure
    if [ "$SKIP_INFRA" = false ]; then
        log_step "Step 1: Deploying Azure Infrastructure"
        azd up
    else
        log_warn "Skipping infrastructure deployment (--skip-infra)"
    fi

    # Load env from azd
    log_info "Loading environment from azd..."
    export SEARCH_ENDPOINT=$(azd env get-value AZURE_SEARCH_ENDPOINT 2>/dev/null || echo "")
    export OPENAI_ENDPOINT=$(azd env get-value AZURE_OPENAI_ENDPOINT 2>/dev/null || echo "")
    export RESOURCE_GROUP=$(azd env get-value AZURE_RESOURCE_GROUP 2>/dev/null || echo "")
    export SUBSCRIPTION_ID=$(az account show --query id -o tsv)

    # Get search admin key for setup scripts
    SEARCH_SERVICE_NAME=$(echo "$SEARCH_ENDPOINT" | sed 's|https://||' | sed 's|\.search.*||')
    export SEARCH_KEY=$(az search admin-key show \
        --service-name "$SEARCH_SERVICE_NAME" \
        -g "$RESOURCE_GROUP" \
        --query primaryKey -o tsv 2>/dev/null || echo "")

    # Step 2: RBAC
    log_step "Step 2: Setting Up RBAC"
    run_subscript "setup_rbac.sh"

    # Step 3: Search Indexes
    log_step "Step 3: Creating Search Indexes"
    run_subscript "setup_indexes.sh"

    # Step 4: Upload Sample Data
    log_step "Step 4: Uploading Sample Airline Data"
    run_subscript "upload_sample_data.sh"

    # Step 5: Knowledge Sources
    log_step "Step 5: Creating Knowledge Sources (including Bing Search)"
    run_subscript "setup_knowledge_sources.sh"

    # Step 6: Knowledge Bases
    log_step "Step 6: Creating Knowledge Bases"
    run_subscript "setup_knowledge_bases.sh"

    # Print summary
    log_step "Deployment Complete!"
    
    echo ""
    echo -e "${GREEN}Resources Created:${NC}"
    echo "  • Resource Group: $RESOURCE_GROUP"
    echo "  • AI Search: $SEARCH_SERVICE_NAME"
    echo "  • AI Services: $(azd env get-value AZURE_OPENAI_ENDPOINT 2>/dev/null || echo 'N/A')"
    echo ""
    echo -e "${GREEN}FoundryIQ Resources:${NC}"
    echo "  • Indexes: index-customer-service, index-operations, index-loyalty"
    echo "  • Knowledge Sources:"
    echo "    - Customer Service: ks-cs-aisearch, ks-cs-web, ks-cs-sharepoint"
    echo "    - Operations: ks-ops-aisearch, ks-ops-web, ks-geopolitical-bing (Bing Search)"
    echo "    - Loyalty: ks-loyalty-aisearch, ks-loyalty-web"
    echo "  • Knowledge Bases: kb1-customer-service, kb2-operations, kb3-loyalty"
    echo ""
    echo -e "${YELLOW}Manual Steps Required:${NC}"
    echo "  1. Search RBAC: Portal → Search service → Keys → 'Both' (API keys + RBAC)"
    echo "  2. Create Foundry Project in AI Foundry portal and note the project endpoint"
    echo ""
    echo "See docs/deployment.md for detailed instructions."
    echo ""
    
    log_success "Deployment completed successfully! ✈️"
}

main "$@"
