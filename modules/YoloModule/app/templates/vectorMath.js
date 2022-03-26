export default class VectorMath{
 
    static calculateLineLength(line) {
        var X = Math.pow(line.end.x - line.start.x, 2);
        var Y = Math.pow(line.end.y - line.start.y, 2);
        return Math.abs(Math.sqrt(X + Y));
      }
    
    static  findNearestPointOnLine(p, a, b) {
        var atob = { x: b.x - a.x, y: b.y - a.y };
        var atop = { x: p.x - a.x, y: p.y - a.y };
        var len = atob.x * atob.x + atob.y * atob.y;
        var dot = atop.x * atob.x + atop.y * atob.y;
        var t = Math.min(1, Math.max(0, dot / len));
        dot = (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x);
        return { x: a.x + atob.x * t, y: a.y + atob.y * t };
      }
    
     static findNearestLine(coord, lines) {
        if (lines.length == 0) return null;
        return lines[findNearestLineIndex(coord, lines)];
      }
    
      static findNearestLineIndex(coord, lines) {
        if (lines.length == 0) return -1;
        let listOfLines = [];
    
        for (var i = 0; i < lines.length; i++) {
          var line = lines[i];
          var dist = VectorMath.distanceToLine(coord, line);
          listOfLines.push({ index: i, distance: dist });
        }
        listOfLines.sort((a, b) => {
          if (a.distance > b.distance) return 1;
          if (a.distance < b.distance) return -1;
          return 0;
        });
        return listOfLines[0].index;
      }
    
      static distanceToLine(coord, line) {
        var point = VectorMath.findNearestPointOnLine(coord, line.start, line.end);
        var dist = VectorMath.calculateLineLength({ start: coord, end: point });
        return dist;
      }
}