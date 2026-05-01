import {Component, Inject} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from "@angular/material";
import {SCArc} from "../interfaces";

@Component({
  selector: 'app-edit-sc-segment-dialog',
  templateUrl: './edit-sc-segment-dialog.component.html',
  styleUrls: ['./edit-sc-segment-dialog.component.scss']
})
export class EditScSegmentDialogComponent {

  constructor(public dialogRef: MatDialogRef<EditScSegmentDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: SCArc) {
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

}
