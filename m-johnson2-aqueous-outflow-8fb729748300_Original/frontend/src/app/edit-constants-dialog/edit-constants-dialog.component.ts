import { Component, Inject } from '@angular/core';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';
import { Constants } from "./constants.model";
import {Conditions} from "../simulation/conditions.model";
// import { FormControl, Validators } from "@angular/forms";

@Component({
  selector: 'app-edit-constants-dialog',
  templateUrl: './edit-constants-dialog.component.html',
  styleUrls: ['./edit-constants-dialog.component.scss']
})
export class EditConstantsDialogComponent {
  constructor(public dialogRef: MatDialogRef<EditConstantsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: Conditions) {
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  // intFormControl = new FormControl('', [
  //   Validators.pattern('^\d+$')
  // ]);
  //
  // positiveFormControl = new FormControl('', [
  //   Validators.min(0)
  // ]);


}
