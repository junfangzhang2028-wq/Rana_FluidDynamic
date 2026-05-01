import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateStentDialogComponent } from './create-stent-dialog.component';

describe('CreateStentDialogComponent', () => {
  let component: CreateStentDialogComponent;
  let fixture: ComponentFixture<CreateStentDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CreateStentDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateStentDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
