import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
} from '@angular/core';
import {Line, TMArc} from "../interfaces";
import {animate, state, style, transition, trigger} from "@angular/animations";
import {EditTmSegmentDialogComponent} from "../edit-tm-segment-dialog/edit-tm-segment-dialog.component";
import {MatDialog} from "@angular/material";

@Component({
  selector: 'g[tm-segment]',
  templateUrl: './tm-segment.component.html',
  styleUrls: ['./tm-segment.component.scss'],
  animations: [trigger('overLine', [
    state('hover', style({ strokeWidth: '35' })),
    state('unhover', style({ strokeWidth: '25' })),
    transition('unhover => hover', animate('0.15s')),
    transition('hover => unhover', animate('0.15s'))
  ])]
})
export class TmSegmentComponent implements OnInit {
  @Input() circle;

  @Output() segChange: EventEmitter<TMArc> = new EventEmitter<TMArc>();

  @Input() seg: TMArc;

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
    this.angleStart = (this.seg.hour - 1) * 2 * Math.PI / 12;
    this.angleStop = (this.seg.hour) * 2 * Math.PI / 12;
    this.setPathParams();
    this.setSepParams();
  }

  private setPathParams() {
    this.x1 = (this.circle.radius - this.circle.strokeWidth / 2 - 6.7) * Math.cos(this.angleStart + 0.0075) + this.circle.centerX;
    this.y1 = (this.circle.radius - this.circle.strokeWidth / 2 - 6.7) * Math.sin(this.angleStart + 0.0075) + this.circle.centerY;
    this.x2 = (this.circle.radius - this.circle.strokeWidth / 2 - 6.7) * Math.cos(this.angleStop - 0.0075) + this.circle.centerX;
    this.y2 = (this.circle.radius - this.circle.strokeWidth / 2 - 6.7) * Math.sin(this.angleStop - 0.0075) + this.circle.centerY;
    this.d = `M ${this.x1} ${this.y1} A ${this.circle.radius - this.circle.strokeWidth / 2} ${this.circle.radius - this.circle.strokeWidth / 2} 0 0 1 ${this.x2} ${this.y2}`;
  }

  private setSepParams() {
    this.separator = {
      x1: Math.cos(this.angleStop) * (this.circle.radius - this.circle.strokeWidth / 2 - 19.6) + this.circle.centerX,
      y1: Math.sin(this.angleStop) * (this.circle.radius - this.circle.strokeWidth / 2 - 19.6) + this.circle.centerY,
      x2: Math.cos(this.angleStop) * (this.circle.radius - this.circle.strokeWidth / 2 + 5.8) + this.circle.centerX,
      y2: Math.sin(this.angleStop) * (this.circle.radius - this.circle.strokeWidth / 2 + 5.8) + this.circle.centerY
    }
  }

  editSegment(): void {
    const dialogRef = this.dialog.open(EditTmSegmentDialogComponent, {
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
