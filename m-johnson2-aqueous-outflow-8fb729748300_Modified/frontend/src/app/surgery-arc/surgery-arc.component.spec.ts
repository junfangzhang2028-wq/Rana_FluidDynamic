import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SurgeryArcComponent } from './surgery-arc.component';

describe('SurgeryArcComponent', () => {
  let component: SurgeryArcComponent;
  let fixture: ComponentFixture<SurgeryArcComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SurgeryArcComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SurgeryArcComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
