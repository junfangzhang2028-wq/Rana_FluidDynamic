import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditCcDialogComponent } from './edit-cc-dialog.component';

describe('EditCcDialogComponent', () => {
  let component: EditCcDialogComponent;
  let fixture: ComponentFixture<EditCcDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditCcDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditCcDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
