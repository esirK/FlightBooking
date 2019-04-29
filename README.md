# Flight Booking

[![Build Status](https://travis-ci.org/esirK/FlightBooking.svg?branch=develop)](https://travis-ci.org/esirK/FlightBooking)
[![Coverage Status](https://coveralls.io/repos/github/esirK/FlightBooking/badge.svg?branch=develop)](https://coveralls.io/github/esirK/FlightBooking?branch=develop)

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

`POST api/v1/users/register`

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
`POST api/v1/users/login`

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
`PUT api/v1/users/profile`

Updates a user profile e.g Update passport photo. (Authentication required)

`GET api/v1/flights`

Returns all flight available (No Authentication required)

`GET api/v1/flights/<pk>/`
Returns a single flight (No Authentication required)

`POST api/v1/flights/<pk>/reservation`

Allows a user to make a flight reservation. (Authentication required)

`GET api/v1/flights/<pk>/reservations`

Allows a user to view his/her reservation on this flight.
Admins can view all reservations for the specified flight.

`GET api/v1/all_reservations/`

Allows a user to view all their flights reservations.

`PUT api/v1/all_reservations/<pk>`

Allows a user to edit their flights reservation. e.g Cancle the reservation


`POST api/v1/flights/<pk>/book`

Allows a User to book a ticket for flight with the specified pk (Authentication required)

`GET api/v1/tickets` 

Allows a user to view his/her tickets. (Authentication required)
