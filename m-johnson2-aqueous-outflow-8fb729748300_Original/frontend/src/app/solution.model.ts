import { Constants } from "./edit-constants-dialog/constants.model";
import { CC } from "./simulation/cc.model";
import {SolvedCC} from "./interfaces";


export class Solution {
  public iop: number;
  public flowrate: number;
  public pressure: number[];
  public resistance: number;
  public facility: number;
  public jcc: SolvedCC[];
}
