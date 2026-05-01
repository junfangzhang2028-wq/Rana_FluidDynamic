import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CcLineComponent } from './cc-line.component';

describe('CcLineComponent', () => {
  let component: CcLineComponent;
  let fixture: ComponentFixture<CcLineComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CcLineComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CcLineComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
