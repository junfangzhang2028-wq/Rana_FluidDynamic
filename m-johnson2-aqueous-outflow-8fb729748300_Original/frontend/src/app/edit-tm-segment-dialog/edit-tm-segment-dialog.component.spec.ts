import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditTmSegmentDialogComponent } from './edit-tm-segment-dialog.component';

describe('EditTmSegmentDialogComponent', () => {
  let component: EditTmSegmentDialogComponent;
  let fixture: ComponentFixture<EditTmSegmentDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditTmSegmentDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditTmSegmentDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
