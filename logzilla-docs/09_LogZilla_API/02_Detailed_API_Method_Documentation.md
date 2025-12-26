<!-- @@@title:Detailed API Method Documentation@@@ -->

# Detailed API Method Documentation

## 1. Purpose and Audience

This document provides a comprehensive guide to using the LogZilla API, focusing
on conceptual explanations, common workflows, and best practices. It is intended
for developers and administrators who need to integrate with LogZilla
programmatically or automate tasks.

While this guide offers detailed explanations and examples, for the most
granular, up-to-the-minute specifications of every API endpoint—including all
request parameters, response schemas, and authentication methods—please refer to
our auto-generated API documentation:

*   **Swagger UI:** [`/api/docs/`](/api/docs/)

This document aims to complement the auto-generated specifications by providing
the narrative and context needed to use the API effectively.

## 2. Core API Concepts & Conventions

Requests to the API are made using standard HTTP methods. For endpoints that
accept or return data in the request/response body, JSON is the standard format,
and you should typically set the `Content-Type: application/json` header for
`POST`, `PUT`, and `PATCH` requests. Authentication, including how to obtain and
use authorization tokens, is detailed in "[Using The LogZilla
API](01_Using_The_LogZilla_API.md)".

This section outlines key concepts, data structures, and conventions used
throughout the LogZilla API beyond basic authentication. Understanding these
will help you interact with the API more effectively.

### 2.1. Error Handling

The LogZilla API uses standard HTTP status codes to indicate the success or
failure of an API request.

*   **2xx (Successful):**
    *   `200 OK`: The request was successful.
    *   `201 Created`: The request was successful, and a resource was created.
    *   `202 Accepted`: The request has been accepted for processing, but the
        processing has not been completed (common for asynchronous operations).
        The response body usually contains information on how to check the
        status.
    *   `204 No Content`: The request was successful, but there is no content to
        return (e.g., for a successful DELETE request).
*   **4xx (Client Errors):**
    *   `400 Bad Request`: The request could not be understood by the server due
        to malformed syntax or invalid parameters. The response body often
        contains more specific error details.
    *   `401 Unauthorized`: Authentication is required and has failed or has not
        yet been provided. Ensure your auth token is valid and included in the
        request.
    *   `403 Forbidden`: Authentication was successful, but the authenticated
        user does not have permission to perform the requested action.
    *   `404 Not Found`: The requested resource could not be found.
    *   `405 Method Not Allowed`: The HTTP method used (e.g., GET, POST) is not
        supported for the requested resource.
    *   `429 Too Many Requests`: The user has sent too many requests in a given
        amount of time (rate limiting).
*   **5xx (Server Errors):**
    *   `500 Internal Server Error`: An unexpected condition was encountered on
        the server.
    *   `503 Service Unavailable`: The server is currently unable to handle the
        request due to temporary overloading or maintenance.

When an error occurs (especially `4xx` or `5xx`), the response body will often
be a JSON object. While a common key for a simple error message is `detail`
(e.g., `{"detail": "Error message"}`), more specific structures can be returned:

*   **Validation Errors (e.g., `400 Bad Request`, `422 Unprocessable Entity`):**
    May include a `detail` key for general validation issues, or a dictionary
    where keys are the names of the invalid fields and values are a list of
    error messages pertaining to that field. For example: `{"field_name": ["This
    field is required.", "Another error for this field."]}`.
*   **Query Parameter Errors (`400 Bad Request`):** For errors related to
    invalid query parameters, the response might be a JSON object where the key
    is the name of the problematic parameter and the value is the error message:
    `{"parameter_name": "Invalid value supplied."}`.
*   **Server Errors (`500 Internal Server Error`):** In case of unhandled server
    errors, the response may include an `error` key with the error message, and
    potentially a `traceback` key with debugging information (though relying on
    the traceback format for programmatic error handling is not recommended).
    Example: `{"error": "An unexpected error occurred.", "traceback":
    "...traceback string..."}`.
*   **Specific Endpoint Errors:** Some endpoints might return a custom JSON
    structure for certain errors. For example, a timeout during an asynchronous
    operation (like report generation, HTTP status `408 Request Timeout`) might
    return: `{"detail": "Problem with generate report", "status":
    "TASK_TIMEOUT_STATUS"}`. Always check the specific endpoint documentation if
    available, or inspect the response body for details.


### 2.2. Pagination

For API endpoints that return a list of items (e.g., `/api/users`,
`/api/events`), the results are typically paginated to manage response size and
performance.

LogZilla's API uses two distinct pagination mechanisms depending on the type of
endpoint:

#### 1. Query Results Pagination

Used for endpoints like `/api/query/` and `/api/query/{qid}/` (e.g., event search).

- **How to use:**  
  Pass `page`, `page_size`, and optionally `offset` as parameters in your query
  request body or URL.
- **Response structure:**  
  Pagination information is included inside the `results.events` object (for
  search queries), for example:
  ```json
  {
    "results": {
      "events": {
        "objects": [ ... ],
        "page_number": 1,
        "page_size": 100,
        "offset": 0,
        "item_count": 1234,
        "page_count": 13
      },
      ...
    }
  }
  ```

#### 2. Standard List Pagination

Used for most other list endpoints, such as `/api/users/`, `/api/dashboards/`, etc.

- **How to use:**  
  Pass `page` and `page_size` as query parameters in the URL (e.g.,
  `/api/users/?page=2&page_size=50`).
- **Response structure:**  
  Pagination information is included at the top level of the response:
  ```json
  {
    "objects": [ ... ],
    "item_count": 57,
    "page_count": 3,
    "page_number": 2
  }
  ```

### 2.3. Common Data Structures and Formats

#### 2.3.1. Event Field Names

Events in LogZilla are characterized by several standard fields. When querying
or receiving event data through the API, you will encounter these fields. Some
can be prefixed with `-` in sort parameters to reverse the order (e.g.,
`'sort':['first_occurrence','-counter']`).

| Name               | Description |
| ------------------ | --- |
| `first_occurrence` | Timestamp of the first occurrence as seconds from epoch (including microseconds). |
| `last_occurrence`  | Timestamp of the last occurrence as seconds from epoch (including microseconds).  |
| `counter`          | Number of occurrences of the same message in the current deduplication window. |
| `message`          | The event message content. |
| `host`             | The originating host of the event. |
| `program`          | The process or program name associated with the event. |
| `cisco_mnemonic`   | The Cisco mnemonic code, if the event is from a Cisco device and the mnemonic is known. |
| `severity`         | Numeric severity according to the syslog protocol (0-7). |
| `facility`         | Numeric facility according to the syslog protocol (0-23). |
| `status`           | Status as a number (0 - unknown, 1 - actionable, 2 - non-actionable). |
| `type`             | Categorization type of the event (e.g., `SYSLOG`, `INTERNAL`, `UNKNOWN` |
| `User Tags`        | User-defined fields. If a user tag's name conflicts with certain system-reserved event field names, it will be prefixed with `ut_`. See the note below this table for details on this behavior and the specific list of reserved names. |

The base field names that will cause a `ut_` prefix if a user tag shares the
same name are: `host`, `program`, `cisco_mnemonic`, `severity`, `facility`,
`status`, and `type`.

#### 2.3.2. Schedule Configuration

API endpoints for features like scheduled reports (e.g., when dealing with
`ReportSchedule` objects) use a flexible JSON structure to define schedules.
This is typically handled via two main fields: `schedule_type` and `schedule`.

*   **`schedule_type`**: A string indicating the kind of schedule. Common values
    include:
    *   `"c"`: For cron-based schedules.
    *   `"a"`: For ad-hoc (run once now) schedules.
    *   `"t"`: For schedules based on a specific timestamp.

*   **`schedule`**: A JSON object whose structure depends on the
    `schedule_type`.
    *   **For Cron Schedules (`schedule_type: "c"`)**:
        When `schedule_type` is `"c"`, the `schedule` field will be a JSON
        object containing a single key `"cron"`. The value of this `"cron"` key
        is another JSON object that specifies the cron parameters. These
        parameters correspond to standard cron fields used by Celery (which
        LogZilla utilizes for task scheduling):

        *   `minute`: String representing the minute of the hour (0-59).
        *   `hour`: String representing the hour of the day (0-23).
        *   `day_of_week`: String representing the day of the week (0-6 for
            Sunday-Saturday, or use names like `sun`, `mon`).
        *   `day_of_month`: String representing the day of the month (1-31).
        *   `month_of_year`: String representing the month of the year (1-12).

        Each parameter can accept standard cron expressions (e.g., `"*"` for
        any, `"*/5"` for every 5th, `"0-5"` for a range, `"1,3,5"` for specific
        values).

        **Example `schedule` field content when `schedule_type` is `"c"`:**
        ```json
        {
          "cron": {
            "minute": "0",
            "hour": "*/2",
            "day_of_week": "*",
            "day_of_month": "*",
            "month_of_year": "*"
          }
        }
        ```
        This example configures a task to run at minute 0 of every 2nd hour.

    *   **(Note: The exact structure for `"adhoc"` or `"timestamp"` schedule
        types would be `{"adhoc": true}` or `{"timestamp": "<ISO 8601 string or
        epoch>"}` respectively, but the primary focus here is detailing the cron
        structure.)**

This cron setting structure is primarily used by the `/api/reports-schedules/`
endpoint when creating or updating report schedules.

## 3. Workflow-Oriented Documentation

This section groups API endpoints by major resources or common developer
workflows. Each subsection provides an overview, lists key endpoints with direct
links to their detailed specifications in the auto-generated documentation, and
offers practical examples.

(TODO: Review the `urls.py` file and the API's capabilities to identify all
major resources and workflows to be documented here. Examples include: Managing
Users, Managing Groups, Managing Dashboards, Querying Events, Managing Triggers,
System Settings, etc.)

### 3.1. Managing Users

The User Management API allows you to create, retrieve, update, and delete user
accounts, as well as manage their properties and permissions.

**Key Endpoints:**

*   **List Users:** `GET /api/users` - Retrieves a list of all users. ([Swagger
    details](/api/docs/#/users/users_list)) (TODO: Verify link)
*   **Create User:** `POST /api/users` - Creates a new user. ([Swagger
    details](/api/docs/#/users/users_create)) (TODO: Verify link)
*   **Retrieve User:** `GET /api/users/{id}` - Retrieves a specific user by
    their ID. ([Swagger details](/api/docs/#/users/users_read)) (TODO: Verify
    link)
*   **Update User:** `PUT /api/users/{id}` - Updates all fields for a specific
    user. ([Swagger details](/api/docs/#/users/users_update)) (TODO: Verify
    link)
*   **Partial Update User:** `PATCH /api/users/{id}` - Partially updates fields
    for a specific user. ([Swagger
    details](/api/docs/#/users/users_partial_update)) (TODO: Verify link)
*   **Delete User:** `DELETE /api/users/{id}` - Deletes a specific user.
    ([Swagger details](/api/docs/#/users/users_delete)) (TODO: Verify link)
*   (TODO: Add other relevant user-related endpoints like managing user groups,
    permissions, etc., if they are separate, e.g., `/api/users/{id}/groups/`)

**Example Workflow: Creating a New User and Assigning to a Group**

1.  **Create the User:**
    Send a `POST` request to `/api/users/` with the user's details in the
    request body.
    ```json
    // POST /api/users
    {
      "username": "newuser",
      "email": "newuser@example.com",
      "first_name": "New",
      "last_name": "User",
      "password": "Str0ngPassword!", // TODO: Note password complexity requirements
      "is_active": true
      // TODO: Add other relevant fields like permission_codenames or group assignments if supported directly on creation
    }
    ```
    Note the `id` of the newly created user from the response.

2.  **Find or Create the Group:**
    *   To find an existing group's ID, you might `GET /api/groups/` (TODO:
        Verify group endpoint) and filter/search for the desired group.
    *   To create a new group, `POST /api/groups/` with group details. Note its
        `id`.

3.  **Assign User to Group:**
    (TODO: Determine the exact method for assigning a user to a group. This
    might be a PATCH to the user object, a POST to a nested group resource like
    `/api/users/{user_id}/groups/`, or a PATCH to the group object.)
    *Example (assuming PATCH to user):*
    ```json
    // PATCH /api/users/{user_id}
    {
      "groups": [123] // Array of group IDs
    }
    ```

**Important Considerations:**
*   Review password policies and required fields when creating users.
*   Understand how permissions are managed (e.g., directly on the user, through
    group membership, using `permission_codenames`).

### 3.2. Managing Dashboards

The Dashboard API allows you to create, retrieve, update, and delete user
dashboards and their associated widgets.

**Key Endpoints:**

*   **List Dashboards:** `GET /api/dashboards` ([Swagger
    details](/api/docs/#/dashboards/dashboards_list)) (TODO: Verify link)
*   **Create Dashboard:** `POST /api/dashboards` ([Swagger
    details](/api/docs/#/dashboards/dashboards_create)) (TODO: Verify link)
*   **Retrieve Dashboard:** `GET /api/dashboards/{id}` ([Swagger
    details](/api/docs/#/dashboards/dashboards_read)) (TODO: Verify link)
*   (TODO: Add endpoints for Update, Delete, managing dashboard widgets, etc.)

**Example Workflow: Creating a Simple Dashboard with One Widget**

1.  **Create the Dashboard:**
    Send a `POST` request to `/api/dashboards/`.
    ```json
    // POST /api/dashboards
    {
      "name": "My System Overview",
      "description": "Primary dashboard for monitoring system health.",
      "is_public": false // Or true, if it should be accessible by others
      // TODO: Add other relevant fields like owner, layout configuration
    }
    ```
    Note the `id` of the newly created dashboard from the response.

2.  **Add a Widget to the Dashboard:**
    (TODO: Determine the endpoint and method for adding widgets. This could be
    `/api/dashboards/{dashboard_id}/widgets/` or similar.)
    *Example (assuming POST to a nested widget resource):*
    ```json
    // POST /api/dashboards/{dashboard_id}/widgets
    {
      "name": "CPU Usage Last Hour",
      "widget_type": "timeseries_chart", // TODO: Verify available widget types
      "configuration": {
        "query": "program=collectd AND metric_type=cpu_usage", // Example query
        "time_range": "last_1_hour"
        // TODO: Add other widget-specific configuration fields (size, position, colors)
      }
    }
    ```

**Important Considerations:**
*   Understand the different widget types available and their specific
    configuration options.
*   Familiarize yourself with how dashboard layouts are defined if configurable
    via the API.

---
(More workflows like "Querying Event Data", "Managing Triggers and Actions",
"Configuring System Settings", "Managing Reports", "Accessing Audit Logs" etc.
would follow here, each with a similar structure.)

## 4. Practical Examples & Use Cases

This section provides more comprehensive examples that demonstrate how to
combine multiple API calls to achieve realistic goals. These examples are
designed to illustrate common patterns and showcase the power and flexibility of
the LogZilla API.

(TODO: Develop 2-3 detailed practical examples. These should be more involved
than the single workflow examples in Section 3. For instance:
    *   **Example 1: Automated Alert Escalation and Ticket Creation:**
        1.  Query for critical events matching certain criteria (`GET
            /api/events/` or `/api/query/`).
        2.  If critical events are found, check if a notification has already
            been sent for a similar recent event (perhaps by checking a custom
            tag or an external system).
        3.  If no recent notification, create a new alert/notification entry in
            LogZilla (`POST /api/alerts/` - endpoint hypothetical).
        4.  Simultaneously, forward details to an external ticketing system
            (e.g., JIRA, ServiceNow) by making an HTTP POST request (could be
            initiated via a LogZilla script action triggered by the API, or
            directly if the API supports outbound webhooks).
        5.  Update the LogZilla event/alert with the ticket ID from the external
            system (`PATCH /api/events/{id}` or `/api/alerts/{id}`).
    *   **Example 2: Proactive Host Onboarding and Monitoring Setup:**
        1.  A new host is provisioned and its IP/hostname is available.
        2.  Use the API to add this host to a "monitored hosts" group in
            LogZilla (`POST /api/hostgroups/{id}/hosts/` - endpoint
            hypothetical).
        3.  Automatically create a set of standard monitoring rules/triggers for
            this new host based on a template (`POST /api/triggers/` using
            pre-defined criteria targeting the new host or its group).
        4.  Create a dedicated view or dashboard widget for events from this new
            host (`POST /api/views/` or `POST /api/dashboards/{id}/widgets/`).
    *   **Example 3: Generating a Custom Weekly Security Report:**
        1.  Define criteria for security-relevant events.
        2.  At the end of the week (e.g., via a script run by cron):
            a.  Query the API for all security-relevant events from the past
            week (`GET /api/query/` with appropriate filters and time range).
            b.  Query for any changes to user permissions or group memberships
            in the past week (`GET /api/auditlogs/` - endpoint hypothetical, or
            `/api/users/` and `/api/groups/` and diffing if audit specific
            endpoint not available).
            c.  Aggregate and format this data into a report (e.g., CSV, HTML).
            d.  Optionally, use an API endpoint to upload this report or send it
            via an integrated notification channel (`POST /api/reports/` or
            `POST /api/notifications/`).
Each example should include:
    *   A clear description of the goal.
    *   Step-by-step breakdown of API calls.
    *   Sample request/response snippets where useful.
    *   Explanation of any logic involved in processing data between API calls.
)

---

