import {
  Component,
  EventEmitter,
  Input,
  OnChanges,
  OnInit,
  Output,
} from '@angular/core';
import {CCwIndex, EditCCSignal} from "../simulation/cc.model";
import {Circle, Coords, Line} from "../interfaces";
import {interpolateRgb} from 'd3-interpolate';
import {fromEvent, merge, Subscription} from "rxjs";
import {switchMap, takeUntil, throttleTime} from "rxjs/operators";
import {transition, state, trigger, style, animate} from "@angular/animations";
import {EditCcDialogComponent} from "../edit-cc-dialog/edit-cc-dialog.component";
import {MatDialog} from "@angular/material";

const THROTTLE_DEFAULT = 50;

@Component({
  selector: 'g[cc-line]',
  templateUrl: './cc-line.component.html',
  styleUrls: ['./cc-line.component.scss'],
  animations: [trigger('overLine', [
    state('hover', style({ strokeWidth: '9' })),
    state('unhover', style({ strokeWidth: '3' })),
    transition('unhover => hover', animate('0.15s ease-out')),
    transition('hover => unhover', animate('0.15s ease-out'))
  ])]
})
export class CCLineComponent implements OnInit, OnChanges {
  @Output() ccChange: EventEmitter<EditCCSignal> = new EventEmitter<EditCCSignal>();

  @Input() cc: CCwIndex;

  @Input() circle: Circle;
  @Input() maxG: number;

  public focused = false;
  public line: Line;
  public color: string;

  constructor(public dialog: MatDialog) { }

  ngOnInit() {
    this.setLineParams();
  }

  ngOnChanges() {
    this.setLineParams();
  }

  private setLineParams() {
    const theta = this.cc.cc.loc * Math.PI / 180;
    this.line = {
      x1: Math.cos(theta) * (this.circle.radius + this.circle.strokeWidth / 2 - 0.01) + this.circle.centerX,
      y1: Math.sin(theta) * (this.circle.radius + this.circle.strokeWidth / 2 - 0.01) + this.circle.centerY,
      x2: Math.cos(theta) * (this.circle.radius + this.circle.strokeWidth) + this.circle.centerX,
      y2: Math.sin(theta) * (this.circle.radius + this.circle.strokeWidth) + this.circle.centerY,
    };
  }

  editCC(): void {
    const dialogRef = this.dialog.open(EditCcDialogComponent, {
      data: this.cc
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result != null) {
        if (!result.delete) {
          this.cc = result.data;
        }
        this.ccChange.emit(result);
      }
    })
  }

}
