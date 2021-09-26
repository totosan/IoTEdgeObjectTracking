"use strict";

class DrawLines {
  constructor() {
    this.can = document.querySelector("#canvas");
    this.context = this.can.getContext("2d");

    this.startPosition = { x: 0, y: 0 };
    this.lineCoordinates = { x: 0, y: 0 };
    this.isDrawStart = false;
    this.lineCollection = {
      lines: [],
    };
    this.setListeners();
    this.setUpCanvas();
  }

  getClientOffset(event) {
    const { pageX, pageY } = event.touches ? event.touches[0] : event;
    const x = pageX - this.can.offsetLeft;
    const y = pageY - this.can.offsetTop;

    return {x,y,};
  }

    setUpCanvas() {
    
    // Feed the size back to the canvas.
    var img = document.querySelector("#currentImage");
    this.can.width = img.width;
    this.can.height = img.height;
    //this.context.drawImage(img, 0, 0, this.can.width, this.can.height);
  }

  drawLine() {
    this.drawLineL(this.startPosition, this.lineCoordinates);
  }

  drawLineL(start, end) {
    this.context.beginPath();
    this.context.moveTo(start.x, start.y);
    this.context.lineTo(end.x, end.y);
    this.context.stroke();
  }

  drawLineMarked(start, end) {
    this.context.beginPath();
    this.context.moveTo(start.x, start.y);
    this.context.lineTo(end.x, end.y);
    this.context.lineWidth = 6;
    this.context.stroke();
  }

  mouseDownListener(event) {
    this.startPosition = this.getClientOffset(event);
    this.lineCoordinates = Object.assign({}, this.startPosition);
    this.isDrawStart = true;
  }

  mouseMoveListener(event) {
    if (!this.isDrawStart) return;

    this.lineCoordinates = this.getClientOffset(event);
    this.clearCanvas();
    this.repaintCanvas();
    this.drawLine();
  }

  mouseUpListener(event) {
    this.isDrawStart = false;
    var line = {
      start: Object.assign({}, this.startPosition),
      end: Object.assign({}, this.lineCoordinates),
    };

    if (this.calculateLineLength(line) > 10) {
      this.addLineToCollection(line);
    } else {
      var index = this.findNearestLineIndex(line.end);
      this.lineCollection.activeLine = index;
      //drawLineMarked(lineCollection.lines[index].start, lineCollection.lines[index].end);
      this.clearCanvas();
      this.repaintCanvas();
    }
  }

  addLineToCollection(line) {
    this.lineCollection.lines.push(Object.assign({}, line));
  }

  clearCanvas() {
    this.context.clearRect(0, 0, this.can.width, this.can.height);
  }

  repaintCanvas() {
    this.setUpCanvas();

    this.lineCollection.lines.forEach((line, i) => {
      if (this.lineCollection.activeLine === i) this.context.lineWidth = 6;
      else this.context.lineWidth = 1;

      this.drawLineL(line.start, line.end);
    });

    this.context.lineWidth = 1;
  }

  calculateLineLength(line) {
    var X = Math.pow(line.end.x - line.start.x, 2);
    var Y = Math.pow(line.end.y - line.start.y, 2);
    return Math.abs(Math.sqrt(X + Y));
  }

  findNearestPointOnLine(p, a, b) {
    var atob = { x: b.x - a.x, y: b.y - a.y };
    var atop = { x: p.x - a.x, y: p.y - a.y };
    var len = atob.x * atob.x + atob.y * atob.y;
    var dot = atop.x * atob.x + atop.y * atob.y;
    var t = Math.min(1, Math.max(0, dot / len));
    dot = (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x);
    return { x: a.x + atob.x * t, y: a.y + atob.y * t };
  }

  findNearestLine(coord) {
    return this.lineCollection.lines[this.findNearestLineIndex(coord)];
  }

  findNearestLineIndex(coord) {
    let listOfLines = [];

    for (var i = 0; i < this.lineCollection.lines.length; i++) {
      var line = this.lineCollection.lines[i];
      var dist = this.distanceToLine(coord, line);
      listOfLines.push({ index: i, distance: dist });
    }
    listOfLines.sort((a, b) => {
      if (a.distance > b.distance) return 1;
      if (a.distance < b.distance) return -1;
      return 0;
    });
    return listOfLines[0].index;
  }

  distanceToLine(coord, line) {
    var point = this.findNearestPointOnLine(coord, line.start, line.end);
    var dist = this.calculateLineLength({ start: coord, end: point });
    return dist;
  }

  keyUpListener(event) {
    event = event || window.event;
    if (event.key == "Delete") {
      this.lineCollection.lines.splice(this.lineCollection.activeLine, 1);
      this.lineCollection.activeLine = null;
      this.clearCanvas();
      this.repaintCanvas();
    }
  }

  setListeners = () => {
      this.can.addEventListener("mousedown", event => this.mouseDownListener(event));
    this.can.addEventListener("mousemove", event=> this.mouseMoveListener(event));
    this.can.addEventListener("mouseup", event => this.mouseUpListener(event));

    this.can.addEventListener("touchstart", event=> this.mouseDownListener(event));
    this.can.addEventListener("touchmove", event=> this.mouseMoveListener(event));
    this.can.addEventListener("touchend", event=> this.mouseUpListener(event));

    document.addEventListener("keyup", event=> this.keyUpListener(event));
    document.addEventListener("resize", event=> this.setUpCanvas(event));
  };
}
