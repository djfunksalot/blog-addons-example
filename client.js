const testAddon = require('./build/Release/testaddon.node');
const WebSocket = require('ws');
 
const ws = new WebSocket('ws://padio:6789');

const devmap = [[16,16],[0,9],[0,10],[0,14],[9,0],[0,13],[0,15]];

function did_to_dev (did) {
	len = devmap.length
	i = did % len
	return(devmap[i])


}
 
//ws.on('open', function open() {
//  ws.send('something');
//});
 
ws.on('message', function incoming(json) {
	//
	data = JSON.parse(json)
	var channel = did_to_dev(data.value_did)
        console.log('channel ', testAddon.channel(channel[0], channel[1]));

});
