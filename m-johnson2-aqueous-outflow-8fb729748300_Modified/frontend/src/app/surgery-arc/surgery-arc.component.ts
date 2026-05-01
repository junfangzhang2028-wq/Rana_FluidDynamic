import {
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnChanges,
  OnDestroy,
  OnInit,
  Output,
  ViewChild
} from '@angular/core';
import {SurgArc, Circle, Coords, Line} from "../interfaces";
import { fromEvent, merge, Subscription } from "rxjs";
import { switchMap, takeUntil, throttleTime } from "rxjs/operators";
import {transition, state, trigger, style, animate} from "@angular/animations";

const THROTTLE_DEFAULT = 50;

@Component({
  selector: 'g[surgery-arc]',
  templateUrl: './surgery-arc.component.html',
  styleUrls: ['./surgery-arc.component.scss'],
  animations: [trigger('overLine', [
    state('hover', style({ strokeWidth: '10' })),
    state('unhover', style({ strokeWidth: '*' })),
    transition('unhover => hover', animate('0.15s')),
    transition('hover => unhover', animate('0.15s'))
  ])]
})
export class SurgeryArcComponent implements OnInit, OnChanges, OnDestroy {
  @Input() circle: Circle;

  @Output() arcChange: EventEmitter<SurgArc> = new EventEmitter<SurgArc>();

  @Input() arc: SurgArc;

  public d1: string;
  public d2: string;
  public color: string;
  public startLine: Line;
  public stopLine: Line;
  public focused = false;

  private x1: number;
  private y1: number;
  private midX1: number;
  private midY1: number;
  private midX2: number;
  private midY2: number;
  private x2: number;
  private y2: number;
  private startSubscription: Subscription;
  private segmentSubscription: Subscription;
  private stopSubscription: Subscription;
  private angleLength: number;


  @ViewChild("segment") private segment: ElementRef;
  @ViewChild("start") private start: ElementRef;
  @ViewChild("stop") private stop: ElementRef;

  constructor() {

  }

  private static extractMouseEventCoords(e: MouseEvent | TouchEvent) {
    const coords: Coords =
      e instanceof MouseEvent
        ? {
          x: e.offsetX,
          y: e.offsetY
        }
        : {
          x: e.changedTouches.item(0).clientX,
          y: e.changedTouches.item(0).clientY
        };
    return coords;
  }

  ngOnInit() {
    this.setObservables();
    this.angleLength = this.arc.angleStop - this.arc.angleStart;
    this.setPathParams();
    this.setLineParams();
  }

  ngOnChanges() {
    this.setPathParams();
    this.setLineParams();
  }

  ngOnDestroy() {
    this.closeStreams();
  }

  private setObservables() {
    const mouseMove$ = merge(
      fromEvent(document, "mousemove"),
      fromEvent(document, "touchmove")
    );
    const mouseUp$ = merge(
      fromEvent(document, "mouseup"),
      fromEvent(document, "touchend")
    );

    this.startSubscription = merge(
      fromEvent(this.start.nativeElement, "touchstart"),
      fromEvent(this.start.nativeElement, "mousedown")
    )
      .pipe(
        switchMap(_ =>
          mouseMove$.pipe(
            takeUntil(mouseUp$),
            throttleTime(THROTTLE_DEFAULT)
          )
        )
      )
      .subscribe((res: MouseEvent | TouchEvent) => {
        this.handleStartPan(res);
      });

    this.stopSubscription = merge(
      fromEvent(this.stop.nativeElement, "touchstart"),
      fromEvent(this.stop.nativeElement, "mousedown")
    )
      .pipe(
        switchMap(_ =>
          mouseMove$.pipe(
            takeUntil(mouseUp$),
            throttleTime(THROTTLE_DEFAULT)
          )
        )
      )
      .subscribe((res: MouseEvent | TouchEvent) => {
        this.handleStopPan(res);
      });
  }

  private closeStreams() {
    if (this.startSubscription) {
      this.startSubscription.unsubscribe();
      this.startSubscription = null;
    }
    if (this.stopSubscription) {
      this.stopSubscription.unsubscribe();
      this.stopSubscription = null;
    }
  }

  private handleStartPan(e: MouseEvent | TouchEvent) {
    this.focused = true;
    const coords = SurgeryArcComponent.extractMouseEventCoords(e);
    let newAngle = Math.atan2(coords.y - this.circle.centerY, coords.x - this.circle.centerX) % (2 * Math.PI);

    if (newAngle < 0) {
      newAngle += 2 * Math.PI;
    }

    if (newAngle <= this.arc.angleStop && !this.arc.lengthLocked) {
      this.arc.angleStart = newAngle;
    } else if (this.arc.lengthLocked) {
      if (newAngle + this.angleLength <= 2 * Math.PI) {
        this.arc.angleStart = newAngle;
        this.arc.angleStop = newAngle + this.angleLength;
      }
    } else if (Math.abs(newAngle - 2 * Math.PI) < Math.abs(newAngle - this.arc.angleStop)) {
      this.arc.angleStart = 0;
    } else {
      this.arc.angleStart = this.arc.angleStop;
    }

    this.arcChange.emit(this.arc);
    this.setPathParams();
    this.setLineParams();
  }

  private handleStopPan(e: MouseEvent | TouchEvent) {
    const coords = SurgeryArcComponent.extractMouseEventCoords(e);
    let newAngle = Math.atan2(coords.y - this.circle.centerY, coords.x - this.circle.centerX) % (2 * Math.PI);

    if (newAngle < 0) {
      newAngle += 2 * Math.PI;
    }

    if (newAngle >= this.arc.angleStart && !this.arc.lengthLocked) {
      this.arc.angleStop = newAngle;
    } else if (this.arc.lengthLocked) {
      if (newAngle - this.angleLength >= 0) {
        this.arc.angleStop = newAngle;
        this.arc.angleStart = newAngle - this.angleLength;
      }
    } else if (Math.abs(newAngle) < Math.abs(this.arc.angleStart / 2)) {
      this.arc.angleStop = 2 * Math.PI - 0.001;
    }  else {
      this.arc.angleStop = this.arc.angleStart;
    }

    this.arcChange.emit(this.arc);
    this.setPathParams();
    this.setLineParams();
  }

  private setPathParams() {
    // todo: comment/explain all of this math so it's easier to change, same in other methods and components
    this.x1 = (this.circle.radius + 2.5) * Math.cos(this.arc.angleStart) + this.circle.centerX;
    this.y1 = (this.circle.radius + 2.5) * Math.sin(this.arc.angleStart) + this.circle.centerY;
    this.midX1 = (this.circle.radius + 2.5) * Math.cos(this.arc.angleStart + (this.arc.angleStop - this.arc.angleStart) / 2 + 0.01) + this.circle.centerX;
    this.midY1 = (this.circle.radius + 2.5) * Math.sin(this.arc.angleStart + (this.arc.angleStop - this.arc.angleStart) / 2 + 0.01) + this.circle.centerY;
    this.midX2 = (this.circle.radius + 2.5) * Math.cos(this.arc.angleStart + (this.arc.angleStop - this.arc.angleStart) / 2) + this.circle.centerX;
    this.midY2 = (this.circle.radius + 2.5) * Math.sin(this.arc.angleStart + (this.arc.angleStop - this.arc.angleStart) / 2) + this.circle.centerY;
    this.x2 = (this.circle.radius + 2.5) * Math.cos(this.arc.angleStop) + this.circle.centerX;
    this.y2 = (this.circle.radius + 2.5) * Math.sin(this.arc.angleStop) + this.circle.centerY;
    this.d1 = `M ${this.x1} ${this.y1} A ${this.circle.radius + 2.5} ${this.circle.radius + 2.5} 0 0 1 ${this.midX1} ${this.midY1}`;
    this.d2 = `M ${this.midX2} ${this.midY2} A ${this.circle.radius + 2.5} ${this.circle.radius + 2.5} 0 0 1 ${this.x2} ${this.y2}`;
    this.color = this.arc.color;

  }

  private setLineParams() {
    this.startLine = {
      x1: Math.cos(this.arc.angleStart) * (this.circle.radius - this.circle.strokeWidth / 2 - 20) + this.circle.centerX,
      y1: Math.sin(this.arc.angleStart) * (this.circle.radius - this.circle.strokeWidth / 2 - 20) + this.circle.centerY,
      x2: Math.cos(this.arc.angleStart) * (this.circle.radius + this.circle.strokeWidth / 2) + this.circle.centerX,
      y2: Math.sin(this.arc.angleStart) * (this.circle.radius + this.circle.strokeWidth / 2) + this.circle.centerY
    };

    this.stopLine = {
      x1: Math.cos(this.arc.angleStop) * (this.circle.radius - this.circle.strokeWidth / 2 - 19.6) + this.circle.centerX,
      y1: Math.sin(this.arc.angleStop) * (this.circle.radius - this.circle.strokeWidth / 2 - 19.6) + this.circle.centerY,
      x2: Math.cos(this.arc.angleStop) * (this.circle.radius + this.circle.strokeWidth / 2) + this.circle.centerX,
      y2: Math.sin(this.arc.angleStop) * (this.circle.radius + this.circle.strokeWidth / 2) + this.circle.centerY
    };

  }

}
