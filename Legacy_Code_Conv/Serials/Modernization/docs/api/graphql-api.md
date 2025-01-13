# Serials Module GraphQL API Documentation

## Overview
The Serials Module provides a GraphQL API for flexible querying and real-time updates. This document outlines available queries, mutations, and subscriptions.

## Authentication
Include the JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoint
```
https://api.ariesone.com/graphql
```

## Schema

### Types

#### Serial
```graphql
type Serial {
  id: ID!
  serialNumber: String!
  maxUsageCount: Int!
  expirationDate: DateTime
  client: Client!
  metadata: JSON
  isDemo: Boolean!
  isActive: Boolean!
  usages: [SerialUsage!]!
  createdAt: DateTime!
  createdBy: String
  updatedAt: DateTime!
  updatedBy: String
}
```

#### Client
```graphql
type Client {
  id: ID!
  name: String!
  clientNumber: String!
  description: String
  metadata: JSON
  isActive: Boolean!
  serials: [Serial!]!
  contactEmail: String
  contactPhone: String
  notes: String
  createdAt: DateTime!
  createdBy: String
  updatedAt: DateTime!
  updatedBy: String
}
```

#### SerialUsage
```graphql
type SerialUsage {
  id: ID!
  serial: Serial!
  deviceId: String!
  ipAddress: String!
  deviceInfo: JSON!
  status: String!
  createdAt: DateTime!
  expiresAt: DateTime
  notes: String
}
```

### Queries

#### Get Serial
```graphql
query GetSerial($id: ID!) {
  serial(id: $id) {
    id
    serialNumber
    maxUsageCount
    expirationDate
    isActive
    isDemo
    client {
      id
      name
    }
    usages {
      deviceId
      status
      createdAt
    }
  }
}
```

#### List Serials
```graphql
query ListSerials(
  $offset: Int = 0
  $limit: Int = 10
  $isActive: Boolean
  $isDemo: Boolean
  $clientId: ID
) {
  serials(
    offset: $offset
    limit: $limit
    isActive: $isActive
    isDemo: $isDemo
    clientId: $clientId
  ) {
    id
    serialNumber
    maxUsageCount
    expirationDate
    isActive
    client {
      id
      name
    }
  }
}
```

#### Get Client
```graphql
query GetClient($id: ID!) {
  client(id: $id) {
    id
    name
    clientNumber
    isActive
    serials {
      id
      serialNumber
      isActive
    }
  }
}
```

### Mutations

#### Create Serial
```graphql
mutation CreateSerial($input: CreateSerialInput!) {
  createSerial(input: $input) {
    id
    serialNumber
    maxUsageCount
    expirationDate
    isActive
  }
}
```

#### Update Serial
```graphql
mutation UpdateSerial($id: ID!, $input: UpdateSerialInput!) {
  updateSerial(id: $id, input: $input) {
    id
    serialNumber
    maxUsageCount
    expirationDate
    isActive
  }
}
```

#### Validate Serial
```graphql
mutation ValidateSerial($input: ValidateSerialInput!) {
  validateSerial(input: $input)
}
```

### Subscriptions

#### Serial Validation
```graphql
subscription OnSerialValidated($id: ID!) {
  serialValidated(id: $id) {
    deviceId
    status
    createdAt
  }
}
```

#### Serial Revocation
```graphql
subscription OnSerialRevoked($id: ID!) {
  serialRevoked(id: $id) {
    id
    serialNumber
    isActive
  }
}
```

## Error Handling

### Error Types
```graphql
type Error {
  message: String!
  code: String!
  path: [String!]
}
```

Common error codes:
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Invalid input
- `RATE_LIMITED`: Too many requests

### Example Error Response
```json
{
  "errors": [
    {
      "message": "Serial number not found",
      "code": "NOT_FOUND",
      "path": ["validateSerial"]
    }
  ]
}
```

## Best Practices

### Query Optimization
1. Request only needed fields
2. Use fragments for repeated selections
3. Implement pagination for large datasets

Example with fragments:
```graphql
fragment SerialFields on Serial {
  id
  serialNumber
  maxUsageCount
  isActive
}

query GetSerials {
  serials {
    ...SerialFields
    client {
      id
      name
    }
  }
}
```

### Caching
1. Use Apollo Client caching
2. Implement field-level caching
3. Consider cache policies for real-time data

Example cache policy:
```typescript
const cache = new InMemoryCache({
  typePolicies: {
    Serial: {
      fields: {
        usages: {
          merge: false
        }
      }
    }
  }
});
```

### Real-time Updates
1. Use subscriptions for critical updates
2. Implement retry logic for connection loss
3. Handle subscription cleanup

Example subscription setup:
```typescript
const wsLink = new WebSocketLink({
  uri: 'wss://api.ariesone.com/graphql',
  options: {
    reconnect: true,
    connectionParams: {
      authToken: getToken()
    }
  }
});
```

## Performance Considerations
1. Batch related queries
2. Use dataloader for N+1 queries
3. Implement query complexity limits
4. Monitor response times and errors
