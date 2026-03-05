targetScope = 'subscription'

@description('Name of the environment (used as prefix for all resources)')
param environmentName string

@description('Primary location for all resources')
param location string

@description('Azure OpenAI model deployment name')
param openAIModelName string = 'gpt-4.1'

@description('Azure OpenAI embedding model')
param embeddingModelName string = 'text-embedding-3-large'

var abbrs = {
  resourceGroup: 'rg-'
  search: 'srch-'
  openai: 'oai-'
  storage: 'st'
  containerApp: 'ca-'
  containerEnv: 'cae-'
  managedIdentity: 'uami-'
  cognitiveServices: 'foundry-'
}

var resourceGroupName = '${abbrs.resourceGroup}${environmentName}'

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
}

module search 'modules/search.bicep' = {
  name: 'search'
  scope: rg
  params: {
    name: '${abbrs.search}${environmentName}'
    location: location
  }
}

module openai 'modules/openai.bicep' = {
  name: 'openai'
  scope: rg
  params: {
    name: '${abbrs.cognitiveServices}${environmentName}'
    location: location
    modelName: openAIModelName
    embeddingModelName: embeddingModelName
  }
}

module storage 'modules/storage.bicep' = {
  name: 'storage'
  scope: rg
  params: {
    name: '${abbrs.storage}${replace(environmentName, '-', '')}'
    location: location
  }
}

module identity 'modules/identity.bicep' = {
  name: 'identity'
  scope: rg
  params: {
    name: '${abbrs.managedIdentity}${environmentName}'
    location: location
  }
}

module containerApp 'modules/container-app.bicep' = {
  name: 'container-app'
  scope: rg
  params: {
    name: '${abbrs.containerApp}${environmentName}'
    envName: '${abbrs.containerEnv}${environmentName}'
    location: location
    identityId: identity.outputs.identityId
    searchEndpoint: search.outputs.endpoint
    openaiEndpoint: openai.outputs.endpoint
    projectEndpoint: openai.outputs.projectEndpoint
  }
}

output AZURE_SEARCH_ENDPOINT string = search.outputs.endpoint
output AZURE_OPENAI_ENDPOINT string = openai.outputs.endpoint
output AZURE_AI_PROJECT_ENDPOINT string = openai.outputs.projectEndpoint
output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_CONTAINER_APP_URL string = containerApp.outputs.url
