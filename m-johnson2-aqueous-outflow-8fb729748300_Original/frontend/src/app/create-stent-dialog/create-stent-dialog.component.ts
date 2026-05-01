import { Component, Inject } from '@angular/core';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';
import { StentInfo } from "../simulation/stent-info.model";
import {animate, style, transition, trigger} from "@angular/animations";
import {FormControl, FormGroup, Validators} from "@angular/forms";
// import { FormControl, Validators } from "@angular/forms";

@Component({
  selector: 'app-create-stent-dialog',
  templateUrl: './create-stent-dialog.component.html',
  styleUrls: ['./create-stent-dialog.component.scss'],
  animations: [trigger('addRemove', [
    transition(':enter', [
      style({ height: '0px', minHeight: '0', opacity: 0 }),
      animate('0.4s 0.1s ease', style({ height: '*', opacity: 1 }))
    ]),
    transition(':leave', [
      style({ height: '*', opacity: 1 }),
      animate('0.4s 0.1s ease', style({ height: '0px', minHeight: '0', opacity: 0 }))
    ])
  ])]
})
export class CreateStentDialogComponent {

  public windowed = false;

  data: FormGroup = new FormGroup({
    name: new FormControl('New Stent'),
    length: new FormControl(1000, Validators.min(0)),
    loc_inlet: new FormControl(0, [
      Validators.min(0),
      Validators.max(1000)
    ]),
    w: new FormControl(230, Validators.min(0)),
    hd: new FormControl(50, Validators.min(0)),
    n_windows: new FormControl(0, Validators.min(0)),
    l_window: new FormControl(200, Validators.min(0)),
    h_window: new FormControl(50, Validators.min(0)),
    l_spine: new FormControl(200, Validators.min(0)),
    h_spine: new FormControl(50, Validators.min(0)),
    h_after: new FormControl(50, Validators.min(0)),
    g_inlet: new FormControl(50, Validators.min(0)),
    two_way: new FormControl(true),
    geometry: new FormControl('ellipse', Validators.pattern('(ellipse|rectangle)'))
  });

  constructor(public dialogRef: MatDialogRef<CreateStentDialogComponent>) {}

  onNoClick(): void {
    this.dialogRef.close();
  }

  lengthChange() {
    this.data.setControl('loc_inlet', new FormControl(this.data.get('loc_inlet').value, [
      Validators.min(0),
      Validators.max(this.data.get('length').value)
    ]));
  }

  // intFormControl = new FormControl('', [
  //   Validators.pattern('^\d+$')
  // ]);
  //
  // positiveFormControl = new FormControl('', [
  //   Validators.min(0)
  // ]);


}
