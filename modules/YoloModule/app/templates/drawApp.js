"use strict";
import VectorMath from "./vectorMath.js";

export default class DrawLines {
  constructor(canvas, image) {
    this.isResized = false;
    this.wasInit = false;
    this.can = canvas;
    this.img = image;
    this.context = this.can.getContext("2d");
    this.scaleX = -1;
    this.scaleY = -1;

    this.enabled = false;

    this.startPosition = { x: 0, y: 0 };
    this.lineCoordinates = { x: 0, y: 0 };
    this.isDrawStart = false;
    this.lineCollection = {
      lines: [],
      frameSize: [],
      scale: { x: 1, y: 1 },
    };
    this.#setListeners();
    this.setUpCanvas();
  }

  set setLines(lineCollection) {
    let lines = JSON.parse(JSON.stringify(lineCollection));
    if (this.wasInit) {
      let newScaleFactor = {
        x: this.lineCollection.frameSize[2] / lines.frameSize[2],
        y: this.lineCollection.frameSize[3] / lines.frameSize[3],
        sx: this.lineCollection.scale.x / lines.scale.x,
        sy: this.lineCollection.scale.y / lines.scale.y,
      };
      for (let index = 0; index < lines.lines.length; index++) {
        const element = lines.lines[index];
        element.start.x = element.start.x * newScaleFactor.x;
        element.start.y = element.start.y * newScaleFactor.y;
        element.end.x = element.end.x * newScaleFactor.x;
        element.end.y = element.end.y * newScaleFactor.y;
      }
      lines.frameSize = Object.assign({}, this.lineCollection.frameSize);
      this.lineCollection = JSON.parse(JSON.stringify(lines));
    }
  }
  get getLines() {
    return this.lineCollection;
  }

  initObject() {
    if (!this.wasInit) {
      this.lineCollection.frameSize = [
        this.img.offsetTop,
        this.img.offsetLeft,
        this.img.width,
        this.img.height,
      ];

      this.resizeWindow();
      this.wasInit = true;
    }
  }

  #getClientOffset(event) {
    const { pageX, pageY } = event.touches ? event.touches[0] : event;
    const x = ((pageX - this.img.x) * this.can.width) / this.can.clientWidth;
    const y = ((pageY - this.img.y) * this.can.height) / this.can.clientHeight;

    return { x: x / this.scaleX, y: y / this.scaleY };
  }

  resizeWindow() {
    this.isResized = true;

    this.setUpCanvas();
    this.scaleX = this.img.width / this.lineCollection.frameSize[2];
    this.scaleY = this.img.height / this.lineCollection.frameSize[3];
    this.lineCollection.scale = { x: this.scaleX, y: this.scaleY };
    this.refreshCanvas();
    this.isResized = false;
  }

  setUpCanvas() {
    // Feed the size back to the canvas.
    this.can.width = this.img.width;
    this.can.height = this.img.height;
  }

  #clearCanvas() {
    this.context.clearRect(0, 0, this.can.width, this.can.height);
  }

  refreshCanvas() {
    var scaleX = this.scaleX;
    var scaleY = this.scaleY;

    this.lineCollection.lines.forEach((line, i) => {
      if (this.lineCollection.activeLine === i) this.context.lineWidth = 4;
      else this.context.lineWidth = 1;

      this.#drawLineL(line.start, line.end);
    });

    this.context.lineWidth = 1;
  }

  #drawLine() {
    this.#drawLineL(this.startPosition, this.lineCoordinates);
  }

  #drawLineL(start, end) {
    this.context.beginPath();
    this.context.moveTo(start.x * this.scaleX, start.y * this.scaleY);
    this.context.lineTo(end.x * this.scaleX, end.y * this.scaleY);
    this.context.stroke();
  }

  #mouseDownListener(event) {
    this.startPosition = this.#getClientOffset(event);
    this.lineCoordinates = Object.assign({}, this.startPosition);
    this.isDrawStart = true;
  }

  #mouseMoveListener(event) {
    if (!this.isDrawStart) return;

    this.lineCoordinates = this.#getClientOffset(event);
    this.#clearCanvas();
    this.refreshCanvas();
    this.#drawLine();
  }

  #mouseUpListener(event) {
    this.isDrawStart = false;

    var line = {
      start: Object.assign({}, this.startPosition),
      end: Object.assign({}, this.lineCoordinates),
    };

    if (VectorMath.calculateLineLength(line) > 10) {
      //add line
      this.#addLineToCollection(line);
    } else {
      var index = VectorMath.findNearestLineIndex(
        // select line
        line.end,
        this.lineCollection.lines
      );
      this.lineCollection.activeLine = index;
    }
    this.#clearCanvas();
    this.refreshCanvas();
  }

  #addLineToCollection(line) {
    this.lineCollection.lines.push(Object.assign({}, line));
  }

  removeCurrentLine() {
    if (this.lineCollection.activeLine > -1) {
      this.lineCollection.lines.splice(this.lineCollection.activeLine, 1);
      this.lineCollection.activeLine = -1;
      this.#clearCanvas();
      this.refreshCanvas();
    }
  }

  #keyUpListener(event) {
    event = event || window.event;
    if (event.key == "Delete" && this.lineCollection.activeLine > -1) {
      this.removeCurrentLine();
    }
    if (event.key == "s") {
      console.log(JSON.stringify(this.lineCollection));
    }
  }

  #setListeners() {
    this.can.addEventListener("mousedown", (event) => {
      if (this.enabled) this.#mouseDownListener(event);
    });
    this.can.addEventListener("mousemove", (event) => {
      if (this.enabled) this.#mouseMoveListener(event);
    });
    this.can.addEventListener("mouseup", (event) => {
      if (this.enabled) this.#mouseUpListener(event);
    });
/*
    this.can.addEventListener("touchstart", (event) => {
      if (this.enabled) this.#mouseDownListener(event);
    });
    this.can.addEventListener("touchmove", (event) => {
      if (this.enabled) this.#mouseMoveListener(event);
    });
    this.can.addEventListener("touchend", (event) => {
      if (this.enabled) this.#mouseUpListener(event);
    });
    */
    
    window.addEventListener("resize", (event) => this.resizeWindow());
  }
}
