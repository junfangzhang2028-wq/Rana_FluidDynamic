import {FormControl, FormGroup} from "@angular/forms";

export class Trabeculotomy {
  public start: number;
  public end: number;

  constructor(start?: number, end?: number){
    this.start = start;
    this.end = end;
  }
}
