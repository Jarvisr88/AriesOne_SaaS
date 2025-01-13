# Authentication Transformation Rules

## User Management Transformation

### Legacy to Modern Mapping
1. User Table:
   ```
   Legacy (UserProfile)                Modern (User)
   ------------------------           ----------------------
   UserID -> id
   UserName -> username
   Email -> email
   Password -> hashed_password
   FullName -> full_name
   IsActive -> is_active
   LastLoginDate -> last_login
   ```

2. Role Table:
   ```
   Legacy (UserRole)                  Modern (Role)
   ------------------------           ----------------------
   RoleID -> id
   RoleName -> name
   Description -> description
   IsSystem -> is_system_role
   ```

### Data Transformation Rules
1. Password Hashing:
   - Legacy plain-text passwords must be hashed using bcrypt
   - Hash format: `$2b$12$[22 characters]`

2. User-Role Relationships:
   - Convert legacy role assignments to many-to-many relationship
   - Create entries in `core_user_roles` junction table

3. Permissions:
   - Map legacy permissions to resource-action format
   - Example: `EditUser` becomes `users:update`

### Validation Rules
1. Username:
   - Minimum length: 3 characters
   - Maximum length: 50 characters
   - Pattern: `^[a-zA-Z0-9_-]+$`

2. Email:
   - Must be valid email format
   - Maximum length: 100 characters
   - Unique constraint

3. Password:
   - Minimum length: 8 characters
   - Must contain: uppercase, lowercase, number
   - Special characters recommended

## Token Management Transformation

### Token Storage
1. Convert session-based auth to JWT:
   ```
   Legacy (UserSession)               Modern (Token)
   ------------------------           ----------------------
   SessionID                         token
   UserID -> user_id
   ExpiryDate -> expires_at
   IsValid -> is_revoked
   ```

2. Token Format:
   ```json
   {
     "sub": "username",
     "exp": "timestamp",
     "roles": ["role1", "role2"],
     "permissions": ["perm1", "perm2"]
   }
   ```

### Security Rules
1. Token Expiration:
   - Access tokens: 30 minutes
   - Refresh tokens: 7 days
   - Revoke all tokens on password change

2. Rate Limiting:
   - Login attempts: 5 per minute
   - API calls: 100 per minute per user

3. Session Management:
   - Track device information
   - Allow multiple active sessions
   - Provide session revocation
