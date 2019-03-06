# Flight Booking

[![Build Status](https://travis-ci.org/esirK/FlightBooking.svg?branch=ft-allow-users-signup)](https://travis-ci.org/esirK/FlightBooking)
[![Coverage Status](https://coveralls.io/repos/github/esirK/FlightBooking/badge.svg?branch=ft-allow-users-signup)](https://coveralls.io/github/esirK/FlightBooking?branch=ft-allow-users-signup)

FlightBooking is a web app that automates the process of booking for a flight.
The flight booking system provides an API that allows users to 

* Sign up
* log in
* upload passport photographs
* book tickets
* receive tickets as an email
* check the status of their flight
* make flight reservations
* purchase tickets
* A user receives a reminder email a day before their flight is due.

## API Spec
The preferred response format should be JSON.
The JSON object to be returned by the API will be structured as follows:
### Example
##### A User 
```source-json
{
  "user": {
    "email": "john@doe.jake",
    "username": "johndoe",
  }
}
```
### Errors and Status Codes
If a request fails any validations, errors should be expected in the following format:
```source-json
{
  "errors":{
    "email": [
      "User with this email already exists"
    ]
  }
}
```
### Other status codes:
401 for Unauthorized requests, when a request requires authentication but it isn't provided

403 for Forbidden requests, when a request may be valid but the user doesn't have permissions to perform the action

404 for Not found requests, when a resource can't be found to fulfill the request

## Endpoints
### Registration

`POST api/register`

User registration.
Requires a request with the following format. (No Authentication required)
```source-json
{
  "user": {
    "email": "john@doe.jake",
    "username": "johndoe",
    "password": "********"
  }
}
```
`POST api/login`

User login.

Returns a JWT authentication token. (No Authentication required)
```source-json
{
  "user": {
    "email": "john@doe.jake",
    "password": "********"
  }
}
```
`PUT api/profile`

Updates a user profile e.g Update passport photo. (Authentication required)

`GET api/flights`

Returns all flights available (No Authentication required)

`GET api/tickets` 

Allows a user to view his/her tickets. (Authentication required)

`POST api/tickets` 

Allows a user to book a ticket. (Authentication required)

`POST api/flights/reservation`

Allows a user to make a flight reservation. (Authentication required)

`POST api/tickets/purchase` 

Allows a user to book a ticket. (Authentication required)