import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditScSegmentDialogComponent } from './edit-sc-segment-dialog.component';

describe('EditScSegmentDialogComponent', () => {
  let component: EditScSegmentDialogComponent;
  let fixture: ComponentFixture<EditScSegmentDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditScSegmentDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditScSegmentDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
