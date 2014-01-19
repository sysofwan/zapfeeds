var connect = require('connect'),
    sharejs = require('share').server
    connectRoute = require('connect-route')
    render = require('connect-render');

var server = connect(
	  render({root: __dirname + '/public', layout: 'index.html', cache: wd false}),
      connect.logger(),
      connect.static(__dirname + '/public')
    );

server.use(connectRoute(function(router) {
	router.get('/code/:name', function (req, res, next) {
    	res.render('index.html');
    });
	router.get('/', function (req, res, next) {
        res.end('index');
        console.log('hi!!');
    });
}));
var options = {db: {type: 'redis'}}; // See docs for options. {type: 'redis'} to enable persistance.

// Attach the sharejs REST and Socket.io interfaces to the server
sharejs.attach(server, options);

server.listen(8000, function(){
    console.log('Server running at http://127.0.0.1:8000/');
});
/// Hi!!! asdasd qwqdwdqwdewd

// edit over hereuifhuibgfibxfjbgfxiubdfipiiwedwedwedwedwed