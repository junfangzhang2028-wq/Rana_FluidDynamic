import {Component, Inject} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from "@angular/material";
import {TMArc} from "../interfaces";

@Component({
  selector: 'app-edit-tm-segment-dialog',
  templateUrl: './edit-tm-segment-dialog.component.html',
  styleUrls: ['./edit-tm-segment-dialog.component.scss']
})
export class EditTmSegmentDialogComponent {

  constructor(public dialogRef: MatDialogRef<EditTmSegmentDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: TMArc) {
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

}
