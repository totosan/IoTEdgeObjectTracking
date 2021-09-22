var imageDpi = 300;
window.onload = function () {
  var can = document.querySelector("#canvas");
  var img = document.querySelector("#currentImage");
  var width = (can.width = img.width);
  var height = (can.height = img.height);

  var context = can.getContext("2d");

  context.drawImage(img, 10, 10);
  let startPosition = { x: 0, y: 0 };
  let lineCoordinates = { x: 0, y: 0 };
  let isDrawStart = false;
  let lineCollection = {
    lines: [],
  };

  const getClientOffset = (event) => {
    const { pageX, pageY } = event.touches ? event.touches[0] : event;
    const x = pageX - can.offsetLeft;
    const y = pageY - can.offsetTop;

    return {
      x,
      y,
    };
  };

  const drawLine = () => {
    drawLineL(startPosition, lineCoordinates);
  };

  const drawLineL = (start, end) => {
    context.beginPath();
    context.moveTo(start.x, start.y);
    context.lineTo(end.x, end.y);
    context.stroke();
  };

  const drawLineMarked = (start, end) => {
    context.beginPath();
    context.moveTo(start.x, start.y);
    context.lineTo(end.x, end.y);
    context.lineWidth = 6;
    context.stroke();
  };

  const mouseDownListener = (event) => {
    startPosition = getClientOffset(event);
    lineCoordinates = Object.assign({}, startPosition);
    isDrawStart = true;
  };

  const mouseMoveListener = (event) => {
    if (!isDrawStart) return;

    lineCoordinates = getClientOffset(event);
    clearCanvas();
    repaintLines();
    drawLine();
  };

  const mouseUpListener = (event) => {
    isDrawStart = false;
    var line = {
      start: Object.assign({}, startPosition),
      end: Object.assign({}, lineCoordinates),
    };

    if (calculateLineLength(line) > 10) {
      addLineToCollection(line);
    } else {
      var index = findNearestLineIndex(line.end);
      lineCollection.activeLine = index;
      //drawLineMarked(lineCollection.lines[index].start, lineCollection.lines[index].end);
      clearCanvas();
      repaintLines();
    }
  };

  const addLineToCollection = (line) => {
    lineCollection.lines.push(Object.assign({}, line));
  };

  const clearCanvas = () => {
    context.clearRect(0, 0, can.width, can.height);
  };

  const repaintLines = () => {
    lineCollection.lines.forEach((line, i) => {
      if (lineCollection.activeLine === i) context.lineWidth = 6;
      else context.lineWidth = 1;

      drawLineL(line.start, line.end);
    });
    context.lineWidth = 1;
  };

  const calculateLineLength = (line) => {
    X = Math.pow(line.end.x - line.start.x, 2);
    Y = Math.pow(line.end.y - line.start.y, 2);
    return Math.abs(Math.sqrt(X + Y));
  };

  function findNearestPointOnLine(p, a, b) {
    var atob = { x: b.x - a.x, y: b.y - a.y };
    var atop = { x: p.x - a.x, y: p.y - a.y };
    var len = atob.x * atob.x + atob.y * atob.y;
    var dot = atop.x * atob.x + atop.y * atob.y;
    var t = Math.min(1, Math.max(0, dot / len));
    dot = (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x);
    return { x: a.x + atob.x * t, y: a.y + atob.y * t };
  }

  const findNearestLine = (coord) => {
    return lineCollection.lines[findNearestLineIndex(coord)];
  };

  const findNearestLineIndex = (coord) => {
    let listOfLines = [];

    for (i = 0; i < lineCollection.lines.length; i++) {
      var line = lineCollection.lines[i];
      dist = distanceToLine(coord, line);
      listOfLines.push({ index: i, distance: dist });
    }
    listOfLines.sort((a, b) => {
      if (a.distance > b.distance) return 1;
      if (a.distance < b.distance) return -1;
      return 0;
    });
    return listOfLines[0].index;
  };

  const distanceToLine = (coord, line) => {
    var point = findNearestPointOnLine(coord, line.start, line.end);
    var dist = calculateLineLength({ start: coord, end: point });
    return dist;
    };
    
    const keyUpListener = (event) => {
        event = event || window.event;
        if (event.key == 'Delete') {
            lineCollection.lines.splice(lineCollection.activeLine, 1);
            lineCollection.activeLine = null;
            clearCanvas();
            repaintLines();
        }
    }

  can.addEventListener("mousedown", mouseDownListener);
  can.addEventListener("mousemove", mouseMoveListener);
  can.addEventListener("mouseup", mouseUpListener);

  can.addEventListener("touchstart", mouseDownListener);
  can.addEventListener("touchmove", mouseMoveListener);
  can.addEventListener("touchend", mouseUpListener);

    document.addEventListener("keyup", keyUpListener);
};
