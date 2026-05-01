import {Injectable, Component, Inject} from '@angular/core';
import { Solution } from "./solution.model";
import { Conditions } from "./simulation/conditions.model";
import { Observable, throwError } from "rxjs";
import {HttpClient, HttpErrorResponse} from "@angular/common/http";
import { API_URL } from "./env";
import {catchError} from "rxjs/operators";


@Injectable({
  providedIn: 'root'
})
export class SolverService {

  constructor(private http: HttpClient) { }

  private handleError(error: HttpErrorResponse) {
    console.log(error);
    if (error.error instanceof ErrorEvent) {
      console.error('An error occurred:', error.error.message);
    } else {
      console.error(
        `Backend returned code ${error.status}, ` +
        `body was: ${error.error.message}`);
    }

    if (error.status == 0) {
      return throwError("Failed to contact solution service. Please try again later.");
    } else {
      return throwError(error.error.message);
    }
  };

  solve(conditions: Conditions): Observable<Solution> {
    return this.http.post<Solution>(API_URL+"/solve", conditions)
      .pipe(
        catchError(this.handleError)
      );
  }
}
