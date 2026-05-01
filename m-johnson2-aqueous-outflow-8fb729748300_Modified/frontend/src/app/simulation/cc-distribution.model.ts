import {CC} from "./cc.model";

export class CCDistribution {
  public name: string;
  public ccs: CC[];

  constructor(name?: string, ccs?: CC[]) {
    if (name) {
      this.name = name;
    } else {
      this.name = 'Default';
    }
    if (ccs) {
      this.ccs = ccs;
    } else {
      this.ccs = [];
      const XCC = 360 / 30;
      const locs = new Array(30).fill(0);
      for (let ind in locs) {
        let i = Number(ind);
        this.ccs.push({
          loc: i * XCC,
          g_ratio: 1
        });
      }
    }
    console.log(this.name + ' has been created')
  }
}
