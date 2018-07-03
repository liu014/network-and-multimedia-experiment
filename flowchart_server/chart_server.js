var app = require('express')()
  , server = require('http').createServer(app)
  , io = require('socket.io').listen(server);

server.listen(8081);


let the_socket = [];
var net = require('net');
var server2 = net.createServer();

server2.listen(8082);
server2.on('connection', function(socket) {
    liste=[];
    object={};
    liste.push(socket.remoteAddress);
    console.log(liste);
    let flow_array = [];
    let array_length = [];
    let bullet_array = [];
    var fs = require('fs');
    socket.on('data', function(data) {
	
        var str= data.toString();//console.log(str);
        var indx = 1 + str.lastIndexOf('x')
	str = str.slice(indx)
	//str = str.substr(1);
	//str = str.slice(0,-1);
	var js_object = JSON.parse(str);
	for(key in js_object)
	{
	    var j = key.search("-");
	    var port_id = parseInt(key.slice(j + 1));
	    var switch_id = parseInt(key.slice(0,j));
	    
	    //console.log(switch_id);
	    //console.log(port_id);
	    if (flow_array.length < switch_id) 
	    {
		while (flow_array.length != switch_id) 
		{//console.log(switch_id - 1);console.log("asfafsas");
		    flow_array.push(new Array(1));
		    bullet_array.push(new Array(1));
		    array_length.push(0);
		}
		flow_array[switch_id - 1] = new Array(port_id);
		bullet_array[switch_id - 1] = new Array(port_id);
		array_length[switch_id - 1] = port_id;
	    }
	    else if (array_length[switch_id - 1] < port_id)
	    {
		while (array_length[switch_id - 1] != port_id) 
		{
		    flow_array[switch_id - 1].push(0);
		    bullet_array[switch_id - 1].push(null);
		    array_length[switch_id - 1] = array_length[switch_id - 1] + 1;
		}
	    }//console.log(js_object[key]);
	    flow_array[switch_id - 1][port_id - 1] = js_object[key];
	    let bullet_json = {
    		"title":key,"subtitle":js_object[key] + "bps","ranges":[2000000,10000000,30000000],"measures":[js_object[key]],"markers":[20000000]
	    }
 	    bullet_array[switch_id - 1][port_id - 1] = bullet_json;
	    
	}
	var write_str = "[\n";
	//console.log(JSON.stringify(bullet_array,null,0));
	//console.log(flow_array.length);console.log();
	for(var x = 0; x < flow_array.length; ++x)
	    for(var y = 0; y < array_length[x]; ++y) 
	    {//console.log(x);
		if (bullet_array[x][y] != null)
		{
		    write_str = write_str + "  ";
		    write_str = write_str + JSON.stringify(bullet_array[x][y],null,0);
		    if (x != flow_array.length - 1 || y != array_length[x] - 1) write_str = write_str + ",";
		    write_str = write_str + "\n";
		}
		
	    }
	write_str = write_str + "]";
	//var fs = require('fs');
	fs.writeFile("bullets.json",write_str,function(err) { if(err) console.log(err); });
	if (the_socket.length != 0) for(var z = 0; z < the_socket.length; ++z) the_socket[z].emit('news');
    });
});




app.get('/', function (req, res) {
  var options = { root: __dirname };
  res.sendFile('/index.html', options);
  //res.sendfile(__dirname + '/index.html');
});


app.get('/bullets.json', function (req, res) {
  var options = { root: __dirname };
  
  res.sendFile('/bullets.json', options);
  //res.sendfile(__dirname + '/index.html');
});


io.sockets.on('connection', function (socket) {
    the_socket.push(socket);//socket.emit('news');
/*  socket.emit('news', { hello: 'world' });
  socket.on('my other event', function (data) {
    console.log(data);
  });*/
});











