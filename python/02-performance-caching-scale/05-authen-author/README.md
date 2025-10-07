# Authentication/authorization: JWT vs sessions vs OAuth2 — which fits when?

The choice depends on your application's architecture and needs. **Sessions** are for stateful, traditional web apps. **JWT** is for stateless applications like APIs and SPAs. **OAuth2** is an authorization framework for delegated access, not a direct alternative for session management.

***

### Sessions

Session-based authentication is a **stateful** mechanism. When a user logs in, the server creates a unique session ID, stores it in a cookie on the user's browser, and keeps a record of that session ID and its associated user data on the server (in memory, a database, or a cache like Redis).

* **How it works:** On each subsequent request, the browser sends the session ID cookie. The server uses this ID to retrieve the user's session data and validate the request.
* **Pros:**
    * **Secure:** Session data isn't stored on the client, only the ID.
    * **Easy Revocation:** A session can be instantly invalidated on the server (e.g., on logout or password change).
* **Cons:**
    * **Scalability Issues:** Requires server-side storage, which can be difficult to manage in a distributed or load-balanced environment. All servers must have access to the same session store.
    * **Stateful:** The server must maintain the state for every active user, consuming memory and resources.
* **When to use:**
    * Traditional, monolithic web applications where the server and client are tightly coupled.
    * Applications where server-side state is not a scalability concern.

***

### JWT (JSON Web Tokens)

JWT is a standard for creating self-contained access tokens that assert claims as a JSON object. It's a **stateless** mechanism. The token is signed by the server and sent to the client, which stores it and includes it in the `Authorization` header for subsequent API calls.



* **How it works:** The server validates the token by checking its signature using a secret key. Since the user data (payload) is inside the token itself, the server doesn't need to store any session information.
* **Pros:**
    * **Stateless:** No session data is stored on the server, making it highly scalable and ideal for microservices or serverless architectures.
    * **Decoupled:** Works well between different services, domains, and on mobile/web clients.
* **Cons:**
    * **Revocation is Hard:** Once a token is issued, it's valid until it expires. Revoking it before expiration requires a server-side blocklist, which defeats the purpose of being stateless.
    * **Data Exposure:** The token's payload is encoded (Base64), not encrypted, so it's readable. **Never store sensitive data in a JWT payload.**
* **When to use:**
    * APIs, especially for Single-Page Applications (SPAs) and mobile apps.
    * Microservices architectures where services need to communicate securely and without a shared session store.

***

### OAuth 2.0

OAuth2 is not an authentication protocol; it is an **authorization framework**. Its primary purpose is to grant a third-party application limited access to a user's resources on another service, without sharing the user's credentials. It defines the flow for how an application can obtain an access token to act on the user's behalf.

* **How it works:** It standardizes the process where a user (Resource Owner) grants a third-party app (Client) permission to access their data from a service (Resource Server) via an Authorization Server. The result of a successful OAuth2 flow is an **access token** (which is often, but not necessarily, a JWT).
* **Pros:**
    * **Delegated Access:** The standard for secure third-party authorization.
    * **Granular Permissions:** Allows for specific scopes of access (e.g., read-only access to contacts).
* **Cons:**
    * **Complexity:** The specification can be complex to implement correctly.
    * **Not for Authentication:** By itself, OAuth2 only tells you that the application is authorized to access resources on behalf of *some* user; it doesn't verify the user's identity to the application. For that, you need a protocol like **OpenID Connect (OIDC)**, which is built on top of OAuth2.
* **When to use:**
    * Allowing users to "Log in with Google/Facebook/GitHub."
    * Granting a third-party application (e.g., a photo printing service) access to a user's resources on your platform (e.g., their photos).

## Summary Comparison

| Feature | Session-Based | JWT (JSON Web Tokens) | OAuth 2.0 |
| :--- | :--- | :--- | :--- |
| **Type** | Stateful Authentication | Stateless Authentication | Authorization Framework |
| **Data Storage** | Server-side | Client-side (in token) | N/A (Defines a flow) |
| **Primary Use Case**| Traditional Web Apps | APIs, SPAs, Microservices | Delegated Third-Party Access |
| **Scalability** | Limited | High | N/A |
| **Revocation** | Easy (Server-side delete) | Hard (Requires blocklist) | Depends on token type |