import { NgModule } from '@angular/core';
import {RouterModule, Routes } from "@angular/router";
import {SimulationComponent} from "./simulation/simulation.component";
import {AboutComponent} from "./about/about.component";
import {InstructionsComponent} from "./instructions/instructions.component";
import {DisclaimerComponent} from "./disclaimer/disclaimer.component";

const routes: Routes = [
  { path: 'simulation', component: SimulationComponent },
  { path: 'instructions', component: InstructionsComponent },
  { path: 'about', component: AboutComponent, data: {title: 'About'} },
  { path: 'disclaimer', component: DisclaimerComponent },
  { path: '**', redirectTo: 'simulation'}
];

@NgModule({
  imports: [ RouterModule.forRoot(routes, {useHash: true}) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule { }
