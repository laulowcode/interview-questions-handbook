| Feature                | WebSockets                        | Server-Sent Events (SSE)         | gRPC (with streaming)            | Polling                          | Webhooks                         |
|------------------------|-----------------------------------|-----------------------------------|----------------------------------|----------------------------------|----------------------------------|
| **Direction**          | Bidirectional (full-duplex)       | Unidirectional (server → client)  | Bidirectional (with streams)     | Unidirectional (client → server) | Unidirectional (server → client) |
| **Transport**          | TCP (usually over HTTP/1.1/2)     | HTTP/1.1                          | HTTP/2                           | HTTP/1.1/2                       | HTTP/1.1/2                       |
| **Browser Support**    | Excellent                         | Excellent                        | Limited (needs client lib)       | Universal                        | N/A (server to server)           |
| **Realtime**           | Yes                               | Yes (server push only)            | Yes                              | No (depends on interval)         | Yes (on event)                   |
| **Client Complexity**  | Medium                            | Low                               | High                             | Low                              | Low                              |
| **Server Complexity**  | Medium                            | Low                               | High                             | Low                              | Medium                           |
| **Scalability**        | Harder (many open conns)          | Easier (HTTP, keep-alive)         | Harder (stateful, many streams)  | Easy (stateless)                 | Easy (stateless)                 |
| **Binary Support**     | Yes                               | No (text only)                    | Yes (protobuf)                   | Yes                              | Yes                              |
| **Reconnect/Retry**    | Manual                            | Built-in (auto-reconnect)         | Manual                           | N/A                              | N/A                              |
| **Firewall Friendly**  | Sometimes (non-HTTP upgrades)     | Yes (plain HTTP)                  | Sometimes (HTTP/2 required)      | Yes                              | Yes                              |
| **Use Cases**          | Chat, games, live dashboards      | Notifications, live feeds         | Microservices, IoT, APIs         | Simple updates, legacy systems   | 3rd-party integrations           |
| **Backpressure**       | Manual                            | Limited                           | Built-in                         | N/A                              | N/A                              |
| **Mobile Friendly**    | Medium (persistent conn drains)   | Good (HTTP, auto-reconnect)       | Medium (persistent conn drains)  | Good                             | Good                             |

**Summary:**
- **WebSockets**: Best for interactive, bidirectional, low-latency communication (e.g., chat, games).
- **SSE**: Simple, reliable server-to-client push for browsers (e.g., notifications, live scores).
- **gRPC**: High-performance, typed, bidirectional streaming for backend/backend or mobile.
- **Polling**: Easiest to implement, but inefficient for real-time; use for infrequent updates.
- **Webhooks**: Server-to-server push for event notifications (e.g., payment, GitHub events).

> Choose based on directionality, client/server support, and scalability needs.
