// Interface for surgery arcs on visual editor
export interface SurgArc {
  angleStart: number;
  angleStop: number;
  color: string;
  type: string;
  surgIndex: number;
  arcIndex: number;
  lengthLocked?: boolean;
  strokeWidth?: number;
}

// Interface for TM arcs on visual editor
export interface TMArc {
  hour: number;
  resistance: number;
}

// Interface for SC arcs on visual editor
export interface SCArc {
  seg: number;
  height: number;
}

// Interface for tree levels on Instructions page
export interface InstructionNode {
  name: string;
  children?: InstructionNode[];
}

export interface FlatNode {
  expandable: boolean;
  name: string;
  level: number;
}

export interface SolvedCC {
  loc: number;
  jcc: number;
}

export interface NodeArc {
  d: string
  colorH: string;
  colorP: string;
  theta: number;
  pressure: number;
  height: number;
}

export interface Circle {
  radius: number;
  strokeWidth: number;
  centerX: number;
  centerY: number;
  showDegrees?: boolean;
}

export interface IText {
  x: number;
  y: number;
  anchor?: string;
  fontSize?: number;
}

export interface Line {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  strokeWidth?: number;
  text?: IText;
  color?: string;
  focused?: boolean;
}

export interface Coords {
  x: number;
  y: number;
}
