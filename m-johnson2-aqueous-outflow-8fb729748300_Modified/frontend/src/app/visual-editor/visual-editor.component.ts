import { Component, OnInit, OnChanges, Input, Output, EventEmitter, ViewChild, ElementRef } from '@angular/core';
import {SurgArc, TMArc, Circle, Line, SCArc} from "../interfaces";
import {CCwIndex, EditCCSignal} from "../simulation/cc.model";


@Component({
  selector: 'app-visual-editor',
  templateUrl: './visual-editor.component.html',
  styleUrls: ['./visual-editor.component.scss']
})
export class VisualEditorComponent implements OnInit, OnChanges {
  @Input() props: Circle;
  @Input() arcs: SurgArc[];
  @Input() ccs: CCwIndex[];
  @Input() tm: TMArc[];
  @Input() sc: SCArc[];

  @Output() arcChange = new EventEmitter<SurgArc>();
  @Output() ccChange = new EventEmitter<EditCCSignal>();
  @Output() tmChange = new EventEmitter<TMArc>();
  @Output() scChange = new EventEmitter<SCArc>();

  public degreeTicks: Line[] = [];

  @ViewChild("circle") private circle: ElementRef;

  constructor() {
  }

  ngOnInit() {
    this.setCircleCenter();
    this.drawDegrees();
  }

  ngOnChanges() {
  }

  onArcChange(arc) {
    this.arcs[arc.arcIndex] = arc;
    this.arcChange.emit(arc);
  }

  onTMChange(segment) {
    this.tm[segment.hour - 1] = segment;
    this.tmChange.emit(segment);
  }

  onSCChange(segment) {
    this.sc[segment.seg - 1] = segment;
    this.scChange.emit(segment);
  }

  onCCChange(result) {
    if (!result.delete){
      this.ccs[result.data.index] = result.data;
    }
    this.ccChange.emit(result);
  }

  public getContainerWidth() {
    const { strokeWidth, radius } = this.props;
    return strokeWidth * 3 + radius * 2 + 2;
  }

  public setCircleCenter() {
    const halfOfContainer = this.getContainerWidth() / 2;
    this.props.centerX = halfOfContainer;
    this.props.centerY = halfOfContainer;
  }

  public getTranslate(): string {
    return ` translate(
    ${this.props.strokeWidth / 2 + this.props.radius + 1},
    ${this.props.strokeWidth / 2 + this.props.radius + 1} )`;
  }

  public getTranslateFrom(x, y): string {
    return ` translate(${x}, ${y})`;
  }

  private drawDegrees() {
    const degrees = new Array(360).fill(0);
    for (let d in degrees) {
      let deg = Number(d);
      if (deg % 10 == 0) {
        let offsetX = 0;
        let offsetY = 0;
        if (deg > 130 && deg < 230) {
          offsetX = -10;
        }
        if ((deg > 150 && deg < 210) || deg < 30) {
          offsetY = -5;
        } else if (deg > 210) {
          offsetY = -8;
        }
        if (deg > 300) {
          offsetX = 10;
        } else if (deg < 30) {
          offsetX = 5
        }
        this.degreeTicks.push({
          x1: Math.cos(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2 - 24) + this.props.centerX,
          y1: Math.sin(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2 - 24) + this.props.centerY,
          x2: Math.cos(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2) + this.props.centerX,
          y2: Math.sin(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2) + this.props.centerY,
          strokeWidth: 2,
          text: {
            x: Math.cos(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2 - 29) + this.props.centerX - offsetX,
            y: Math.sin(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2 - 29) + this.props.centerY - offsetY,
            fontSize: 9,
            anchor: 'middle'
          }
        });
      } else if (deg % 5 == 0) {
        this.degreeTicks.push({
          x1: Math.cos(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2 - 10) + this.props.centerX,
          y1: Math.sin(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2 - 10) + this.props.centerY,
          x2: Math.cos(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2) + this.props.centerX,
          y2: Math.sin(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2) + this.props.centerY,
          strokeWidth: 1
        });
      } else {
        this.degreeTicks.push({
          x1: Math.cos(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2 - 5) + this.props.centerX,
          y1: Math.sin(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2 - 5) + this.props.centerY,
          x2: Math.cos(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2) + this.props.centerX,
          y2: Math.sin(deg * Math.PI / 180) * (this.props.radius - this.props.strokeWidth / 2) + this.props.centerY,
          strokeWidth: 1
        });
      }
    }
  }

}
