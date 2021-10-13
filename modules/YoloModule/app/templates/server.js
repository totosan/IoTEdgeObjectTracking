import internal from "stream";
import WSMessage from "./WSMessage.js";

const express = require("express");
const WebSocket = require("ws");
const http = require("http");
const path = require("path");
const fileSystem = require("fs");
const app = express();
const server = http.createServer(app);

var testfolder = path.resolve(__dirname, "..", "test_images");
var testImage = fileSystem.readFileSync(testfolder + "/frame001.jpg", { encoding: "base64",});
let rulesEditEnabled = false;

express.static.mime.define({ "application/javascript": ["js"] });
app.use("/", express.static(__dirname + "/"));
app.use("/img", express.static(testfolder));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname + "/index.html"));
});
server.listen(8080, () => console.log("Listening on port 8080!"));

const ws = new WebSocket.Server({ server: server, path: "/stream" });

ws.on("connection", function connection(wsConnection) {
  wsConnection.on("message", function incoming(message) {
    var msg = WSMessage.fromText(message);
    if (msg.type == "command" && msg.payload == "next") {
      let msg = new WSMessage("image", testImage);
      wsConnection.send(JSON.stringify(msg));

      if (rulesEditEnabled == true) {
        msg.type = 'mode';
        msg.payload = { 'ModeName': 'RulesEdit', 'Value': true };
        wsConnection.send(JSON.stringify(msg));
      }
    }
  });
});

function pad(num, size) {
  var s = "000" + num;
  return s.substr(s.length - size);
}
