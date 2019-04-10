# Language Server Protocol 

This document describes version 2.0 - 2.1 of the language server protocol. Change

#### Abstract Message

A general message as defined by JSON-RPC. The language server protocol always uses "2.0" as the jsonrpc version.

```typescript
interface Message {
	jsonrpc: string;
}
```
#### RequestMessage 

A request message to describe a request between the client and the server. Every processed request must send a response back to the sender of the request.

```typescript
interface RequestMessage extends Message {

	/**
	 * The request id.
	 */
	id: number | string;

	/**
	 * The method to be invoked.
	 */
	method: string;

	/**
	 * The method's params.
	 */
	params?: any
}
```

#### Response Message

#### <a name="exit"></a>Exit Notification

A notification to ask the server to exit its process.
The server should exit with `success` code 0 if the shutdown request has been received before; otherwise with `error` code 1.

_Notification_
* method: 'exit'
* params: undefined

# foo

hoi
