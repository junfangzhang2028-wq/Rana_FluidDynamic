import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
} from '@angular/core';
import {Line, SCArc} from "../interfaces";
import {animate, state, style, transition, trigger} from "@angular/animations";
import {EditTmSegmentDialogComponent} from "../edit-tm-segment-dialog/edit-tm-segment-dialog.component";
import {MatDialog} from "@angular/material";
import {EditScSegmentDialogComponent} from "../edit-sc-segment-dialog/edit-sc-segment-dialog.component";

@Component({
  selector: 'g[sc-segment]',
  templateUrl: './sc-segment.component.html',
  styleUrls: ['./sc-segment.component.scss'],
  animations: [trigger('overLine', [
    state('hover', style({ strokeWidth: '61' })),
    state('unhover', style({ strokeWidth: '41' })),
    transition('unhover => hover', animate('0.15s')),
    transition('hover => unhover', animate('0.15s'))
  ])]
})
export class ScSegmentComponent implements OnInit {
  @Input() circle;

  @Output() segChange: EventEmitter<SCArc> = new EventEmitter<SCArc>();

  @Input() seg: SCArc;

  public d: string;
  public color: string;
  public separator: Line;
  public focused = false;

  private x1: number;
  private y1: number;
  private x2: number;
  private y2: number;
  private angleStart: number;
  private angleStop: number;

  constructor(public dialog: MatDialog) { }

  ngOnInit() {
    this.angleStart = (this.seg.seg - 1) * 2 * Math.PI / 30;
    this.angleStop = (this.seg.seg) * 2 * Math.PI / 30;
    this.setPathParams();
    this.setSepParams();
  }

  private setPathParams() {
    this.x1 = (this.circle.radius) * Math.cos(this.angleStart + 0.0075) + this.circle.centerX;
    this.y1 = (this.circle.radius) * Math.sin(this.angleStart + 0.0075) + this.circle.centerY;
    this.x2 = (this.circle.radius) * Math.cos(this.angleStop - 0.0075) + this.circle.centerX;
    this.y2 = (this.circle.radius) * Math.sin(this.angleStop - 0.0075) + this.circle.centerY;
    this.d = `M ${this.x1} ${this.y1} A ${this.circle.radius} ${this.circle.radius} 0 0 1 ${this.x2} ${this.y2}`;
  }

  private setSepParams() {
    this.separator = {
      x1: Math.cos(this.angleStop) * (this.circle.radius - this.circle.strokeWidth / 2) + this.circle.centerX,
      y1: Math.sin(this.angleStop) * (this.circle.radius - this.circle.strokeWidth / 2) + this.circle.centerY,
      x2: Math.cos(this.angleStop) * (this.circle.radius + this.circle.strokeWidth / 2) + this.circle.centerX,
      y2: Math.sin(this.angleStop) * (this.circle.radius + this.circle.strokeWidth / 2) + this.circle.centerY
    }
  }

  editSegment(): void {
    const dialogRef = this.dialog.open(EditScSegmentDialogComponent, {
      data: this.seg
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result != null) {
        this.seg = result;
        this.segChange.emit(result);
      }
    })
  }

}
