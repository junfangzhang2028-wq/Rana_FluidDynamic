export class CC {
  public loc: number;
  public g_ratio: number;

  constructor(loc?: number, g_ratio?: null) {
    if (loc) {
      this.loc = loc;
    }
    if (g_ratio) {
      this.g_ratio = g_ratio;
    }
  }
}

export interface CCwIndex {
  cc: CC;
  index: number;
}

export interface EditCCSignal {
  delete: boolean;
  data: any;
}
