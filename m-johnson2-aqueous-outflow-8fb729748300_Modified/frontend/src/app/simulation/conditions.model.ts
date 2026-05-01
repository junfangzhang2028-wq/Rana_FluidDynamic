import { Constants } from "../edit-constants-dialog/constants.model";
import { Trabeculotomy } from "./trabeculotomy.model";
import { Sinusotomy } from "./sinusotomy.model";
import { Stent } from "./stent.model";
import { CC } from "./cc.model";
import {CCDistribution} from "./cc-distribution.model";
import {TMSegment} from "../tm-segment/tm-segment.model";
import {SCSegment} from "../sc-segment/sc-segment.model";

const defaultCCDist = new CCDistribution();
export const defaultTMSegs = [new TMSegment(1, 24),
new TMSegment(2, 24),
new TMSegment(3, 24),
new TMSegment(4, 24),
new TMSegment(5, 24),
new TMSegment(6, 24),
new TMSegment(7, 24),
new TMSegment(8, 24),
new TMSegment(9, 24),
new TMSegment(10, 24),
new TMSegment(11, 24),
new TMSegment(12, 24)];

export const defaultSCSegs = [new SCSegment(1, 20),
new SCSegment(2, 20),
new SCSegment(3, 20),
new SCSegment(4, 20),
new SCSegment(5, 20),
new SCSegment(6, 20),
new SCSegment(7, 20),
new SCSegment(8, 20),
new SCSegment(9, 20),
new SCSegment(10, 20),
new SCSegment(11, 20),
new SCSegment(12, 20),
new SCSegment(13, 20),
new SCSegment(14, 20),
new SCSegment(15, 20),
new SCSegment(16, 20),
new SCSegment(17, 20),
new SCSegment(18, 20),
new SCSegment(19, 20),
new SCSegment(20, 20),
new SCSegment(21, 20),
new SCSegment(22, 20),
new SCSegment(23, 20),
new SCSegment(24, 20),
new SCSegment(25, 20),
new SCSegment(26, 20),
new SCSegment(27, 20),
new SCSegment(28, 20),
new SCSegment(29, 20),
new SCSegment(30, 20)];


export class Conditions {
  public mode: 'constant pressure' | 'constant flow';
  public iop?: number;
  public qt?: number;
  public unconventional: boolean;
  public variable_rtm: boolean;
  public variable_h0: boolean;
  public trabeculotomies: Trabeculotomy[];
  public sinusotomies: Sinusotomy[];
  public stents: Stent[];
  public ccs: CC[];
  public rtm: TMSegment[];
  public h0: SCSegment[];
  public constants: Constants;

  constructor(mode, iop?, qt?, rtm?, pev?) {
    this.mode = mode;
    if (iop){
      this.iop = iop;
    } else {
      this.iop = 15;
    }
    if (qt) {
      this.qt = qt;
    } else {
      this.qt = 2.0
    }

    this.trabeculotomies = [];
    this.sinusotomies = [];
    this.stents = [];
    this.rtm = defaultTMSegs;
    this.h0 = defaultSCSegs;

    this.ccs = defaultCCDist.ccs;

    let rt = 2.0;
    if (rtm) {
      rt = rtm;
    }

    let pv = 8.0;
    if (pev) {
      pv = pev;
    }

    this.constants = {
      max_error: 1e-4,
      n: 30,
      m: 40,
      etm: 13,
      rtm: rt,
      hs: 3.0,
      rcc: undefined,
      h0: 20,
      pev: pv,
      qu: 0.28
    };
  }
}
