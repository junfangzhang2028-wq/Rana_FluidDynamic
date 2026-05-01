import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ScSegmentComponent } from './sc-segment.component';

describe('ScSegmentComponent', () => {
  let component: ScSegmentComponent;
  let fixture: ComponentFixture<ScSegmentComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ScSegmentComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScSegmentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
