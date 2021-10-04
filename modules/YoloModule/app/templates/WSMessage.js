export default class WSMessage{
  type;
  payload;
  constructor(typeOfMessage, payload) {
    this.type = typeOfMessage;
    this.payload = payload;
  }

  get Type(){
    return this.type;
  }

  get Payload() {
    return this.payload;
  }

  static fromText(text) {
    let plainObj = JSON.parse(text);
    
    if (plainObj.type && plainObj.payload) {
      return new WSMessage(plainObj.type, plainObj.payload);
    }
  }
}