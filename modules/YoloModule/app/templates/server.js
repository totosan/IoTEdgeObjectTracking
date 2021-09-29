const express = require('express');
var path = require("path");
const app = express();

express.static.mime.define({'application/javascript': ['js']});
app.use('/', express.static(__dirname + '/'));
var testfolder = path.resolve(__dirname, '..', 'test_images');
app.use( '/img', express.static( testfolder ));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname + '/index.html'));
});
app.listen(8080, () => console.log('Listening on port 8080!'));