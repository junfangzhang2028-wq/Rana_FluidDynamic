import { BrowserModule } from '@angular/platform-browser';
import {NgModule, ɵQueryValueType} from '@angular/core';
import { HttpClientModule } from "@angular/common/http";
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FlexLayoutModule } from "@angular/flex-layout";
import { LayoutModule } from '@angular/cdk/layout';
import {
  MatFormFieldModule,
  MatSelectModule,
  MatCardModule,
  MatOptionModule,
  MatDividerModule,
  MatInputModule,
  MatListModule,
  MatCheckboxModule,
  MatTooltipModule,
  MatButtonModule,
  MatIconModule,
  MatDialogModule,
  MatToolbarModule,
  MatSidenavModule,
  MatProgressSpinnerModule,
  MatTabsModule,
  MatTreeModule,
  MatSnackBarModule
} from '@angular/material';
import { SimulationComponent, ErrorDialogComponent } from './simulation/simulation.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { EditConstantsDialogComponent } from "./edit-constants-dialog/edit-constants-dialog.component";
import { AppRoutingModule } from "./app-routing.module";
import { SidenavComponent } from "./sidenav/sidenav.component";
import { CreateStentDialogComponent } from "./create-stent-dialog/create-stent-dialog.component";
import { VisualEditorComponent } from "./visual-editor/visual-editor.component";
import { SurgeryArcComponent } from "./surgery-arc/surgery-arc.component";
import { CCLineComponent } from './cc-line/cc-line.component';
import { SolutionComponent } from './solution/solution.component';
import { AboutComponent } from './about/about.component';
import { InstructionsComponent } from './instructions/instructions.component';
import { SafePipe } from './safe.pipe';
import { DisclaimerComponent } from './disclaimer/disclaimer.component';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import { TmSegmentComponent } from './tm-segment/tm-segment.component';
import { EditTmSegmentDialogComponent } from './edit-tm-segment-dialog/edit-tm-segment-dialog.component';
import { ScSegmentComponent } from './sc-segment/sc-segment.component';
import { EditScSegmentDialogComponent } from './edit-sc-segment-dialog/edit-sc-segment-dialog.component';
import { EditCcDialogComponent } from './edit-cc-dialog/edit-cc-dialog.component';


@NgModule({
    declarations: [
        AppComponent,
        SimulationComponent,
        EditConstantsDialogComponent,
        SidenavComponent,
        CreateStentDialogComponent,
        VisualEditorComponent,
        SurgeryArcComponent,
        CCLineComponent,
        SolutionComponent,
        AboutComponent,
        ErrorDialogComponent,
        InstructionsComponent,
        SafePipe,
        DisclaimerComponent,
        TmSegmentComponent,
        EditTmSegmentDialogComponent,
        ScSegmentComponent,
        ScSegmentComponent,
        EditScSegmentDialogComponent,
        EditCcDialogComponent
    ],
  entryComponents: [
    EditConstantsDialogComponent,
    CreateStentDialogComponent,
    ErrorDialogComponent,
    EditTmSegmentDialogComponent,
    EditScSegmentDialogComponent,
    EditCcDialogComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    BrowserAnimationsModule,
    LayoutModule,
    MatFormFieldModule,
    MatSelectModule,
    MatCardModule,
    MatOptionModule,
    MatInputModule,
    MatDividerModule,
    MatListModule,
    MatCheckboxModule,
    FormsModule,
    ReactiveFormsModule,
    MatTooltipModule,
    MatButtonModule,
    MatIconModule,
    MatDialogModule,
    AppRoutingModule,
    MatToolbarModule,
    MatSidenavModule,
    FlexLayoutModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    MatTreeModule,
    MatSnackBarModule
  ],
  providers: [
    { provide: MAT_DIALOG_DATA, useValue: {} },
     { provide: MatDialogRef, useValue: {} }],
  bootstrap: [AppComponent]
})
export class AppModule { }

