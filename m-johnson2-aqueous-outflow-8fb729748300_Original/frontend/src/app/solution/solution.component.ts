import { Component, OnInit, Input, OnChanges } from '@angular/core';
import {NodeArc, Circle, Line, SolvedCC} from '../interfaces';
import { Solution } from "../solution.model";
import { interpolateRgb } from 'd3-interpolate';
import {animate, state, style, transition, trigger} from "@angular/animations";
import {environment} from "../env";

const colorScale = interpolateRgb("#1e88e5", "#e53935");

@Component({
  selector: 'app-solution',
  templateUrl: './solution.component.html',
  styleUrls: ['./solution.component.scss'],
  animations: [trigger('overLine', [
    state('hover', style({ strokeWidth: '9' })),
    state('unhover', style({ strokeWidth: '3' })),
    transition('unhover => hover', animate('0.15s ease-out')),
    transition('hover => unhover', animate('0.15s ease-out'))
  ])]
})
export class SolutionComponent implements OnInit {
  @Input() circleProps: Circle;
  @Input() solution: Solution;

  public degreeTicks: Line[] = [];
  public nodeArcs: NodeArc[] = [];
  public ccLines: Line[] = [];
  public nodeHl = false;
  public ccHl = false;
  public hln: NodeArc;
  public hlcc: number;
  public conditions = environment.conditions;

  constructor() { }

  ngOnInit() {
    this.setCircleCenter();
    this.drawDegrees();
    this.setPathParams();
    this.drawCCs();
  }

  public getContainerWidth() {
    const { strokeWidth, radius } = this.circleProps;
    return strokeWidth * 3 + radius * 2 + 2;
  }

  public setCircleCenter() {
    const halfOfContainer = this.getContainerWidth() / 2;
    this.circleProps.centerX = halfOfContainer + 100;
    this.circleProps.centerY = halfOfContainer;
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
          x1: Math.cos(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2 - 24) + this.circleProps.centerX,
          y1: Math.sin(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2 - 24) + this.circleProps.centerY,
          x2: Math.cos(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2) + this.circleProps.centerX,
          y2: Math.sin(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2) + this.circleProps.centerY,
          strokeWidth: 2,
          text: {
            x: Math.cos(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2 - 29) + this.circleProps.centerX - offsetX,
            y: Math.sin(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2 - 29) + this.circleProps.centerY - offsetY,
            fontSize: 9,
            anchor: 'middle'
          }
        });
      } else if (deg % 5 == 0) {
        this.degreeTicks.push({
          x1: Math.cos(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2 - 10) + this.circleProps.centerX,
          y1: Math.sin(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2 - 10) + this.circleProps.centerY,
          x2: Math.cos(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2) + this.circleProps.centerX,
          y2: Math.sin(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2) + this.circleProps.centerY,
          strokeWidth: 1
        });
      } else {
        this.degreeTicks.push({
          x1: Math.cos(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2 - 5) + this.circleProps.centerX,
          y1: Math.sin(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2 - 5) + this.circleProps.centerY,
          x2: Math.cos(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2) + this.circleProps.centerX,
          y2: Math.sin(deg * Math.PI / 180) * (this.circleProps.radius - this.circleProps.strokeWidth / 2) + this.circleProps.centerY,
          strokeWidth: 1
        });
      }
    }
  }

  private setPathParams() {
    const arcLength = 2 * Math.PI / this.solution.pressure.length;
    let index = 0;
    for (let p of this.solution.pressure) {
      let startAngle = index * arcLength;
      let stopAngle = startAngle + arcLength;
      let h0 = this.conditions.h0[Math.floor(index/this.conditions.constants.m)].height;
      let x1 = this.circleProps.radius * Math.cos(startAngle) + this.circleProps.centerX;
      let y1 = this.circleProps.radius * Math.sin(startAngle) + this.circleProps.centerY;
      let x2 = this.circleProps.radius * Math.cos(stopAngle + 0.01) + this.circleProps.centerX;
      let y2 = this.circleProps.radius * Math.sin(stopAngle + 0.01) + this.circleProps.centerY;
      this.nodeArcs.push({
        d: `M ${x1} ${y1} A ${this.circleProps.radius} ${this.circleProps.radius} 0 0 1 ${x2} ${y2}`,
        height: this.getHeight(p, h0),
        colorH: colorScale(this.getHeight(p, h0) / h0),
        colorP: colorScale((p - this.conditions.constants.pev) / (this.solution.iop - this.conditions.constants.pev)),
        pressure: p,
        theta: startAngle * 180 / Math.PI
      });
      index += 1;
    }
  }

  private getHeight(p, h0) {
    let height = 0;
    let ks = this.conditions.constants.etm * (1 - this.conditions.constants.hs/h0)
    if ((this.solution.iop - p) < ks) {
      height = h0 * (1 - (this.solution.iop - p) / this.conditions.constants.etm);
    } else {
      // console.log("Septae height triggered");
      height = this.conditions.constants.hs * Math.pow(ks / (this.solution.iop - p), 1/3);
      // console.log(height);
    }

    return height;
  }

  private drawCCs() {
    const numNodes = this.solution.pressure.length;
    const maxFlow = Math.max.apply(Math, this.solution.jcc.map(function (o) { return o.jcc; }));

    for (let cc of this.solution.jcc) {
      let theta = 2 * Math.PI * cc.loc / numNodes;
      this.ccLines.push({
        x1: Math.cos(theta) * (this.circleProps.radius + this.circleProps.strokeWidth / 2 - 0.001) + this.circleProps.centerX,
        y1: Math.sin(theta) * (this.circleProps.radius + this.circleProps.strokeWidth / 2 - 0.001) + this.circleProps.centerY,
        x2: Math.cos(theta) * (this.circleProps.radius + this.circleProps.strokeWidth) + this.circleProps.centerX,
        y2: Math.sin(theta) * (this.circleProps.radius + this.circleProps.strokeWidth) + this.circleProps.centerY,
        color: colorScale(cc.jcc / maxFlow),
        focused: false
      })
    }
  }

  public displayVal(node) {
    this.nodeHl = true;
    this.hln = node;
  }

  public displayJcc(i) {
    this.ccHl = true;
    this.ccLines[i].focused = true;
    this.hlcc = this.solution.jcc[i].jcc;
  }

  public unfocusJcc(i) {
    this.ccHl = false;
    this.ccLines[i].focused = false;
  }

}
