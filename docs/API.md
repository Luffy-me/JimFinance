# JimFinance API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints except `/auth/register` and `/auth/login` require a ****** in the `Authorization` header:

```
Authorization: ******
```

## Error Responses

All error responses follow this format:

```json
{
    "error": "error_type",
    "detail": "Detailed error message",
    "status_code": 400
}
```

### Common Status Codes
- `200 OK` - Successful request
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "username": "john_doe",
    "full_name": "John Doe",
    "password": "secure_password_123"
}
```

**Response (200):**
```json
{
    "access_token": "******",
    "refresh_token": "******",
    "token_type": "bearer"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password_123"
}
```

**Response (200):**
```json
{
    "access_token": "******",
    "refresh_token": "******",
    "token_type": "bearer"
}
```

#### Logout
```http
POST /auth/logout
Authorization: ******
```

**Response (200):**
```json
{
    "message": "Successfully logged out"
}
```

### Users

#### Get Current User
```http
GET /users/me
Authorization: ******
```

**Response (200):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "full_name": "John Doe",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-15T10:30:00+00:00"
}
```

#### Update User
```http
PUT /users/me
Authorization: ******
Content-Type: application/json

{
    "full_name": "John Updated",
    "avatar_url": "https://example.com/avatar.jpg"
}
```

**Response (200):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "full_name": "John Updated",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-15T10:30:00+00:00"
}
```

### Accounts

#### Create Account
```http
POST /accounts
Authorization: ******
Content-Type: application/json

{
    "name": "Main Checking",
    "account_type": "checking",
    "currency": "USD"
}
```

**Response (201):**
```json
{
    "id": 1,
    "user_id": 1,
    "name": "Main Checking",
    "account_type": "checking",
    "currency": "USD",
    "balance": "0.00",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00+00:00"
}
```

#### List Accounts
```http
GET /accounts
Authorization: ******
```

**Response (200):**
```json
[
    {
        "id": 1,
        "user_id": 1,
        "name": "Main Checking",
        "account_type": "checking",
        "currency": "USD",
        "balance": "5000.00",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00+00:00"
    }
]
```

#### Get Account
```http
GET /accounts/{account_id}
Authorization: ******
```

#### Update Account
```http
PUT /accounts/{account_id}
Authorization: ******
Content-Type: application/json

{
    "name": "Updated Account Name",
    "balance": "5500.00"
}
```

#### Delete Account
```http
DELETE /accounts/{account_id}
Authorization: ******
```

**Response (200):**
```json
{
    "message": "Account deleted successfully"
}
```

### Transactions

#### Create Transaction
```http
POST /transactions
Authorization: ******
Content-Type: application/json

{
    "account_id": 1,
    "amount": "25.50",
    "currency": "USD",
    "merchant": "Starbucks",
    "description": "Coffee",
    "transaction_type": "expense",
    "category_id": 1,
    "transaction_date": "2024-01-15T10:30:00+00:00"
}
```

**Response (201):**
```json
{
    "id": 1,
    "user_id": 1,
    "account_id": 1,
    "amount": "25.50",
    "currency": "USD",
    "merchant": "Starbucks",
    "description": "Coffee",
    "transaction_type": "expense",
    "category_id": 1,
    "confidence_score": 1.0,
    "is_recurring": false,
    "is_anomaly": false,
    "created_at": "2024-01-15T10:30:00+00:00"
}
```

#### List Transactions
```http
GET /transactions?skip=0&limit=50
Authorization: ******
```

**Query Parameters:**
- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 50)

**Response (200):**
```json
[
    {
        "id": 1,
        "user_id": 1,
        "account_id": 1,
        "amount": "25.50",
        "currency": "USD",
        "merchant": "Starbucks",
        "description": "Coffee",
        "transaction_type": "expense",
        "category_id": 1,
        "confidence_score": 1.0,
        "is_recurring": false,
        "is_anomaly": false,
        "created_at": "2024-01-15T10:30:00+00:00"
    }
]
```

#### Get Transaction
```http
GET /transactions/{transaction_id}
Authorization: ******
```

#### Update Transaction
```http
PUT /transactions/{transaction_id}
Authorization: ******
Content-Type: application/json

{
    "merchant": "Starbucks Coffee",
    "category_id": 2,
    "description": "Morning coffee and pastry",
    "tags": ["coffee", "breakfast"]
}
```

#### Delete Transaction
```http
DELETE /transactions/{transaction_id}
Authorization: ******
```

### Categories

#### Create Category
```http
POST /categories
Authorization: ******
Content-Type: application/json

{
    "name": "Groceries",
    "description": "Grocery store purchases",
    "category_type": "food",
    "color": "#FF5733",
    "icon": "shopping-bag"
}
```

**Response (201):**
```json
{
    "id": 1,
    "user_id": 1,
    "name": "Groceries",
    "description": "Grocery store purchases",
    "category_type": "food",
    "color": "#FF5733",
    "icon": "shopping-bag",
    "is_default": false
}
```

#### List Categories
```http
GET /categories
Authorization: ******
```

#### Get Category
```http
GET /categories/{category_id}
Authorization: ******
```

#### Delete Category
```http
DELETE /categories/{category_id}
Authorization: ******
```

### Subscriptions

#### Create Subscription
```http
POST /subscriptions
Authorization: ******
Content-Type: application/json

{
    "account_id": 1,
    "name": "Netflix",
    "merchant": "Netflix Inc.",
    "amount": "15.99",
    "currency": "USD",
    "billing_cycle": "monthly",
    "billing_date": 15,
    "start_date": "2024-01-15T00:00:00+00:00"
}
```

**Response (201):**
```json
{
    "id": 1,
    "user_id": 1,
    "account_id": 1,
    "name": "Netflix",
    "merchant": "Netflix Inc.",
    "amount": "15.99",
    "currency": "USD",
    "billing_cycle": "monthly",
    "billing_date": 15,
    "is_active": true,
    "start_date": "2024-01-15T00:00:00+00:00",
    "end_date": null
}
```

#### List Subscriptions
```http
GET /subscriptions
Authorization: ******
```

#### Get Subscription
```http
GET /subscriptions/{subscription_id}
Authorization: ******
```

#### Update Subscription
```http
PUT /subscriptions/{subscription_id}
Authorization: ******
Content-Type: application/json

{
    "name": "Netflix Premium",
    "amount": "22.99",
    "is_active": true
}
```

#### Delete Subscription
```http
DELETE /subscriptions/{subscription_id}
Authorization: ******
```

### Dashboard

#### Get Dashboard
```http
GET /dashboard
Authorization: ******
```

**Response (200):**
```json
{
    "stats": {
        "total_balance": "5000.00",
        "monthly_income": "3000.00",
        "monthly_expenses": "500.00",
        "savings_rate": 0.833,
        "burn_rate": "16.67",
        "financial_runway_days": 300
    },
    "accounts": [
        {
            "id": 1,
            "user_id": 1,
            "name": "Main Checking",
            "account_type": "checking",
            "currency": "USD",
            "balance": "5000.00",
            "is_active": true,
            "created_at": "2024-01-15T10:30:00+00:00"
        }
    ],
    "recent_transactions": [
        {
            "id": 1,
            "user_id": 1,
            "account_id": 1,
            "amount": "25.50",
            "currency": "USD",
            "merchant": "Starbucks",
            "description": "Coffee",
            "transaction_type": "expense",
            "category_id": 1,
            "confidence_score": 1.0,
            "is_recurring": false,
            "is_anomaly": false,
            "created_at": "2024-01-15T10:30:00+00:00"
        }
    ],
    "subscriptions": [],
    "financial_goals": []
}
```

### Health Check

#### Health Status
```http
GET /health
```

**Response (200):**
```json
{
    "status": "healthy",
    "database": "connected"
}
```

## Rate Limiting

(Coming in Phase 2)

## Pagination

List endpoints support pagination via query parameters:

- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 50, max: 100)

**Example:**
```http
GET /transactions?skip=0&limit=25
```

## Sorting & Filtering

(Coming in Phase 2)

## Webhooks

(Coming in Phase 3)

## SDK Integration

(Coming in Phase 5)
