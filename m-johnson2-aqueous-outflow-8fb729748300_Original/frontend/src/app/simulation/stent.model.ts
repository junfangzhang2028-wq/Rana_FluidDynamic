import { StentInfo } from "./stent-info.model";
import { FormControl, Validators } from "@angular/forms";

export class Stent {
  public loc: number;
  public stent: StentInfo;
  public locControl: FormControl;

  constructor(loc?: number, stent?: StentInfo) {
    this.loc = loc;
    this.stent = stent;
    this.locControl = new FormControl(this.loc, [
      Validators.max(360 - (this.stent.length / 100)),
      Validators.min( 0)
    ])
  }
}
