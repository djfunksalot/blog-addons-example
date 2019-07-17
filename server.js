"use strict";
process.title = 'padio-socketserv';
var webSocketsServerPort = 6789;
var webSocketServer = require('websocket').server;
var http = require('http');
// list of currently connected clients (users)
var clients = [ ];
var STATE = {'value_vG': 0, 'value_vB':0 , 'value_did': 0, 'value_cid':0};
/**
 * HTTP server
 */
var server = http.createServer(function(request, response) {
});
server.listen(webSocketsServerPort, function() {
  console.log((new Date()) + " Server is listening on port "
      + webSocketsServerPort);
});
var wsServer = new webSocketServer({
  httpServer: server
});
wsServer.on('request', function(request) {
  console.log((new Date()) + ' Connection from origin '
      + request.origin + '.');
  var connection = request.accept(null, request.origin); 
  var index = clients.push(connection) - 1;
  var userName = false;
  var userColor = false;
  console.log((new Date()) + ' Connection accepted.');
  connection.on('message', function(message) {
	  console.log(message)
    if (message.type === 'utf8') { // accept only text
	    if(message.utf8Data) {
                var decoded = JSON.parse(message.utf8Data);
		    if(decoded.action) {
	                console.log(decoded.action)
		        if(decoded.action == 'plus_did') {
	                    STATE.value_did  = STATE.value_did + 1;
			}
			if(decoded.action == 'minus_did' && STATE.value_did > 0) {
	                    STATE.value_did  = STATE.value_did - 1;
			}JSON.parse(message.utf8Data)
		    }
              }
        var json = JSON.stringify(Object.assign({type:'state'},STATE));
        for (var i=0; i < clients.length; i++) {
          clients[i].sendUTF(json);
        }
      }
  });
  // user disconnected
  connection.on('close', function(connection) {
    if (userName !== false && userColor !== false) {
      console.log((new Date()) + " Peer "
          + connection.remoteAddress + " disconnected.");
      // remove user from the list of connected clients
      clients.splice(index, 1);
      // push back user's color to be reused by another user
      colors.push(userColor);
    }
  });
});
