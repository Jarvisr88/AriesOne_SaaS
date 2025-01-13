export class ValidationError extends Error {
  constructor(
    message: string,
    public readonly errors: string[] = []
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class ResourceNotFoundError extends Error {
  constructor(resourceId: string) {
    super(`Resource not found: ${resourceId}`);
    this.name = 'ResourceNotFoundError';
  }
}

export class InvalidOperationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'InvalidOperationError';
  }
}

export class DataTypeError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'DataTypeError';
  }
}

export class AuthenticationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class AuthorizationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthorizationError';
  }
}

export class RateLimitError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RateLimitError';
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class CacheError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'CacheError';
  }
}

export class ConfigurationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConfigurationError';
  }
}
