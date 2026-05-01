import {Component, Inject} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from "@angular/material";

import {CCwIndex} from "../simulation/cc.model";

@Component({
  selector: 'app-edit-cc-dialog',
  templateUrl: './edit-cc-dialog.component.html',
  styleUrls: ['./edit-cc-dialog.component.scss']
})
export class EditCcDialogComponent {
  public error = false;
  constructor(public dialogRef: MatDialogRef<EditCcDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: CCwIndex) {
  }

  saveCC() {
    if (this.data.cc.loc === null || this.data.cc.g_ratio === null) {
      this.error = true;
    } else {
      this.error = false;
      this.dialogRef.close({delete: false, data: this.data})
    }
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

}
