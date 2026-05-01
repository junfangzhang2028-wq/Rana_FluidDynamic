import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TmSegmentComponent } from './tm-segment.component';

describe('TmSegmentComponent', () => {
  let component: TmSegmentComponent;
  let fixture: ComponentFixture<TmSegmentComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TmSegmentComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TmSegmentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
