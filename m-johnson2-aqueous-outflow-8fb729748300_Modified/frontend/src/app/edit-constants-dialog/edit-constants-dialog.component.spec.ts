import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditConstantsDialogComponent } from './edit-constants-dialog.component';

describe('CreateStentDialogComponent', () => {
  let component: EditConstantsDialogComponent;
  let fixture: ComponentFixture<EditConstantsDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditConstantsDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditConstantsDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
