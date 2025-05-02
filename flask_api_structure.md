# Flask API Structure

## Base URL
`/api/v1/`

## Authentication Endpoints
### POST /login
**Request:**
```json
{
  "employee_number": "string",
  "password": "string"
}
```
**Response:**
```json
{
  "token": "JWT token",
  "user_id": "integer",
  "department": "string"
}
```

### POST /logout
**Headers:** `Authorization: Bearer <token>`
**Response:** `200 OK`

## Tools Endpoints
### GET /tools
**Response:** `200 OK` with array of tools

### POST /tools
**Headers:** `Authorization: Bearer <token>`
**Request:**
```json
{
  "tool_number": "string",
  "serial_number": "string",
  "description": "string",
  "condition": "string",
  "location": "string"
}
```
**Response:** `201 Created` with new tool object

### GET /tools/<id>
**Response:** `200 OK` with tool details

### PUT /tools/<id>
**Headers:** `Authorization: Bearer <token>`
**Request:** Partial tool object
**Response:** `200 OK` with updated tool

### DELETE /tools/<id>
**Headers:** `Authorization: Bearer <token>`
**Response:** `204 No Content`

## Users Endpoints
### GET /users
**Response:** `200 OK` with array of users

### POST /users
**Headers:** `Authorization: Bearer <token>`
**Request:**
```json
{
  "name": "string",
  "employee_number": "string",
  "department": "string",
  "password": "string"
}
```
**Response:** `201 Created` with new user

## Checkouts Endpoints
### POST /checkouts
**Headers:** `Authorization: Bearer <token>`
**Request:**
```json
{
  "tool_id": "integer",
  "user_id": "integer"
}
```
**Response:** `201 Created` with checkout record

### PUT /checkouts/<id>/return
**Headers:** `Authorization: Bearer <token>`
**Response:** `200 OK` with updated checkout record

## Audit Endpoints
### GET /audit
**Headers:** `Authorization: Bearer <token>`
**Response:** `200 OK` with array of audit logs

This API structure follows RESTful principles with JWT-based authentication. Would you like me to:
1. Proceed with documenting the SPA frontend design
2. Add detailed error response examples
3. Or make any adjustments to this API structure?